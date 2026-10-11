"""Selection math and provenance regressions, not product retrieval evaluation."""
from collections import defaultdict
from dataclasses import dataclass
import hashlib
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

from core.mindscape_config import defaults
sys.path.insert(0, defaults()["mindscape"]["package_path"])
from context_loom.models import Candidate, MemoryRecord, RecordKind
from context_loom.compiler import ContextCompiler
from core.context_focus import ContextFocus, resolve_profiles
from core.mindscape_context import MindscapeContextCompiler
from core.mindscape_lanes import topical_paths, HabitusLane
from core.pulse_context import ContextContribution


class IndependentMemoryRoleTests(unittest.TestCase):
    def compiler(self):
        compiler = MindscapeContextCompiler.__new__(MindscapeContextCompiler)
        compiler._pulse_context = SimpleNamespace(focus=ContextFocus({"conversation": 1}, "diagnostic"),
                                                 contributions=(), query="diagnostic", selected=lambda: ([], []))
        compiler.focus_profiles = resolve_profiles({})
        compiler.config = SimpleNamespace(minimum_utility=None)
        compiler._supplied_candidates = {}
        compiler._covered_source_hashes = set()
        compiler._role_usage = defaultdict(int)
        compiler._producer_usage = defaultdict(int)
        compiler._offered_roles = {}
        return compiler

    def candidates(self, scale):
        return [Candidate(id=f"{role}:{index}", text="diagnostic", section=role, source_record_ids=(),
                          lane_scores={lane: scale if role == "associations" else 0.001}, lane_ranks={lane: index})
                for role, lane in (("associations", "habitus"), ("personal", "subjective"), ("procedures", "procedure"))
                for index in range(1, 5)]

    def ordered(self, scale):
        compiler = self.compiler()
        result = []
        for item in compiler._order_optional_candidates(self.candidates(scale)):
            result.append(item.id)
            compiler._candidate_admitted(item, 50)
        return result

    def test_graph_score_scale_cannot_displace_other_memory_roles(self):
        self.assertEqual(self.ordered(1), self.ordered(10**12))
        self.assertEqual({key.split(":")[0] for key in self.ordered(1)[:3]},
                         {"associations", "personal", "procedures"})

    def test_rejected_contribution_does_not_consume_role_space(self):
        compiler = self.compiler()
        ordered = compiler._order_optional_candidates(self.candidates(1))
        rejected = next(ordered)
        self.assertEqual(dict(compiler._role_usage), {role: 0 for role in ("associations", "personal", "procedures")})
        next_item = next(ordered)
        self.assertEqual(next_item.section, rejected.section)
        compiler._candidate_admitted(next_item, 17)
        self.assertEqual(sum(compiler._role_usage.values()), 17)
        self.assertEqual(sum(compiler._producer_usage.values()), 17)

    def test_native_path_fields_keep_real_topic_ids_and_reject_missing_identity(self):
        adapted = topical_paths([{"target_node_id": "concept:file", "path_node_ids": ["SELF", "concept:file"], "score": .2}])
        self.assertEqual(adapted[0]["target_concept_id"], "concept:file")
        self.assertEqual(adapted[0]["path_nodes"], ["SELF", "concept:file"])
        with self.assertRaises(ValueError):
            topical_paths([{"target_node_id": "", "path_node_ids": ["SELF"]}])

    def test_habitus_native_order_is_not_replaced_by_alphabetic_id_ties(self):
        @dataclass
        class Packet:
            selected_record_ids: tuple = ("z", "a")
            trace_hash: str = "diagnostic"
            y_paths: tuple = ()
        lane = HabitusLane(SimpleNamespace(recall=lambda *args, **kwargs: SimpleNamespace(packet=Packet())))
        context = SimpleNamespace(query="diagnostic", records=[MemoryRecord(
            id=name, kind=RecordKind.USER, content="diagnostic", created_at=1) for name in ("a", "z")])
        candidates = {item.id: item for item in lane.nominate(context)}
        ContextCompiler._assign_lane_ranks(candidates)
        ordered = sorted(candidates.values(), key=lambda c: c.lane_ranks["habitus_graph"])
        self.assertEqual([item.source_record_ids[0] for item in ordered], ["z", "a"])

    def test_dialogue_dedup_does_not_remove_an_independent_factual_source(self):
        compiler = self.compiler()
        compiler._pulse_context.query = "What did you say previously?"
        digest = hashlib.sha256(b"same words").hexdigest()
        compiler._covered_source_hashes = {digest}
        candidate = Candidate("candidate", "same words", "prior_assistant", ())
        compiler._supplied_candidates[candidate.id] = [ContextContribution(
            "prior_assistant", "same words", "mrag", kind="outbound_message", source_content_sha256=digest)]
        self.assertFalse(compiler._trust_allowed(candidate)[0])
        compiler._supplied_candidates[candidate.id] = [ContextContribution(
            "recalled", "same words", "mrag", kind="fact", source_content_sha256=digest)]
        self.assertTrue(compiler._trust_allowed(candidate)[0])

    def test_old_assistant_prose_is_conditional_on_a_past_statement_request(self):
        compiler = self.compiler()
        candidate = Candidate("old_answer", "old answer", "prior_assistant", ())
        compiler._supplied_candidates[candidate.id] = [ContextContribution(
            "prior_assistant", "old answer", "mrag", kind="outbound_message")]
        compiler._pulse_context.query = "What name and preference did I tell you?"
        self.assertFalse(compiler._trust_allowed(candidate)[0])
        for query in ("What was your earlier suggestion?", "What did you say?", "Quote your previous answer."):
            compiler._pulse_context.query = query
            self.assertTrue(compiler._trust_allowed(candidate)[0], query)

    def test_native_merge_cannot_reassign_a_record_role_by_lane_score(self):
        record = MemoryRecord(id="source", kind=RecordKind.FACT, content="source fact", created_at=1,
                              metadata={"context_role": "recalled"})
        for scale in (0.001, 10**12):
            compiler = self.compiler()
            compiler.store = SimpleNamespace(get_record=lambda rid: record, learned_utility=lambda rid: 0)
            nominees = [Candidate("fact", "source fact", "evidence", (record.id,), lane_scores={"exact": 1}),
                        Candidate("fact", "source fact", "multi_hop", (record.id,), lane_scores={"subjective": scale})]
            merged = compiler._merge_nominations(nominees)["fact"]
            self.assertEqual(merged.section, "recalled")
            self.assertEqual(merged.lane_scores["subjective"], scale)

    def test_actual_preconscious_adapter_retains_canonical_message_provenance(self):
        from core.preconscious import Preconscious
        from core.pulse_context import recalled_contribution
        source = {"id": "mem_diagnostic", "content": "diagnostic received words", "lane": "semantic",
                  "record_envelope": {"record_kind": "inbound_message", "actor": "Rowan"},
                  "record_kind": "inbound_message", "created_at": "2026-10-10"}
        adapter = Preconscious.__new__(Preconscious)
        adapter._prev_pulse_belief_ids = []
        adapter._belief_cache = []
        adapter._associative = None
        adapter._raw_spatial_candidates = lambda query: []
        adapter._resolve_associative_cluster = lambda item: (None, None)
        adapter._unified = SimpleNamespace(retrieve=lambda **kwargs: [source],
                                            effective_token_budget=lambda: 1000, last_stats={})
        selected = adapter._unified_select("diagnostic", [], 20, learn=False)
        contribution = recalled_contribution(selected[0])
        self.assertEqual(contribution.kind, "inbound_message")
        self.assertEqual(contribution.section, "prior_user")
        self.assertEqual(selected[0]["record_envelope"]["actor"], "Rowan")
        compiler = self.compiler()
        compiler._covered_source_hashes = {hashlib.sha256(source["content"].encode()).hexdigest()}
        candidate = Candidate("received", contribution.text, contribution.section, ())
        compiler._supplied_candidates[candidate.id] = [contribution]
        self.assertFalse(compiler._trust_allowed(candidate)[0])


if __name__ == "__main__":
    unittest.main()
