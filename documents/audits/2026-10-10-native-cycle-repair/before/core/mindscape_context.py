"""Helix's presentation of native Loom packets, with conditional source labels.

Import after activating the configured MightyMem package. Native lanes and
trust rules stay in ContextCompiler. Helix supplies typed recollections and
focus preferences to whole-item admission. _render counts the actual packet.
"""
from dataclasses import replace
import hashlib
from context_loom.compiler import ContextCompiler
from context_loom.models import Candidate
from core.context_focus import infer_focus, resolve_profiles
from core.pulse_context import PulseContext, SECTION_TITLES


class MindscapeContextCompiler(ContextCompiler):
    _pulse_context = None

    def __init__(self, *args, focus_profiles=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.focus_profiles = resolve_profiles(focus_profiles)
        self._supplied_candidates = {}

    def _optional(self, item):
        return item.section in {
            "recalled_thought", "personal", "associations", "recalled", "prior_user",
            "prior_assistant", "observations", "procedures", "summary", "topical",
        }

    def _merge_nominations(self, nominations):
        candidates = super()._merge_nominations(nominations)
        # Supply whole Helix recollections for the same physical admission
        # boundary as Loom. Never compare mRAG's raw similarity with Loom's.
        # Each producer's existing order is retained as a rank preference.
        ranks = {}
        for item in self._pulse_context.selected()[0] if self._pulse_context else ():
            if not self._optional(item):
                continue
            key = (item.section, item.text)
            cid = "helix_context:" + hashlib.sha256(repr(key).encode()).hexdigest()
            if cid in self._supplied_candidates:
                self._supplied_candidates[cid].append(item)
                continue
            self._supplied_candidates[cid] = [item]
            ranks[item.producer] = ranks.get(item.producer, 0) + 1
            candidates[cid] = Candidate(
                id=cid, text=item.text, section=item.section, source_record_ids=(),
                metadata={"helix_context": True, "producer": item.producer,
                          "source_ids": list(item.source_ids), "producer_rank": ranks[item.producer]},
            )
        return candidates

    def _utility(self, candidate):
        utility = (1.0 / candidate.metadata["producer_rank"]
                   if candidate.id in self._supplied_candidates else super()._utility(candidate))
        if self._pulse_context is None:
            return utility
        section = next(iter(self._present_sections({candidate.section: [candidate.text]})))
        return utility * self._pulse_context.focus.priority(section, self.focus_profiles)

    def _assembled(self, sections):
        if self._pulse_context is None:
            raise RuntimeError("No pulse under compilation")
        retained = [item for item in self._pulse_context.contributions if not self._optional(item)]
        presented = {}
        supplied_by_key = {
            (items[0].section, items[0].text): items
            for items in self._supplied_candidates.values()
        }
        for section, values in sections.items():
            for text in values:
                supplied = supplied_by_key.get((section, text))
                if supplied:
                    retained.extend(supplied)
                else:
                    presented.setdefault(section, []).append(text)
        return replace(self._pulse_context, contributions=tuple(retained)), self._present_sections(presented)

    def compile_pulse(self, context: PulseContext, *, scope="helix"):
        """Keep fresh search text separate from every retrieved contribution.

        The native compiler counts the complete assembly on each admission.
        Its immutable packet includes the exact rendering; the additional
        receipt accounts for sources supplied by Helix outside Loom's lanes.
        This method runs only on Mindscape's owning worker thread.
        """
        if self._pulse_context is not None:
            raise RuntimeError("Cannot overlap pulse context compilations")
        self._pulse_context = replace(context, focus=context.focus or infer_focus(context.query, context.query_source))
        self._supplied_candidates = {}
        self.last_assembly_receipt = None
        try:
            packet = self.compile(context.query, scope=scope, mode="pulse")
            assembled, additional = self._assembled(packet.sections)
            sections = assembled.grouped(additional)
            self.last_assembly_receipt = {
                **assembled.receipt(), "loom_packet_id": packet.id,
                "duplicates": context.selected()[1],
                "sections": sections,
                "policy": "independent retrieval; focus-weighted whole-item admission; no raw retrieval score fusion",
                "attention": self._pulse_context.focus.receipt(self.focus_profiles),
                "supplied_admission": [
                    {"candidate_id": entry.candidate_id, "admitted": entry.admitted,
                     "reason": entry.reason,
                     "sources": [item.receipt() for item in self._supplied_candidates[entry.candidate_id]]}
                    for entry in packet.manifest if entry.candidate_id in self._supplied_candidates
                ],
                "section_tokens": {key: self.token_counter.count(
                    f"[{SECTION_TITLES[key]}]\n" + "\n".join(values)) for key, values in sections.items()},
                "packet_tokens": packet.token_count,
                "input_token_boundary": packet.max_input_tokens,
                "token_counter": type(self.token_counter).__name__,
                "token_accounting": "section counts are standalone; packet count includes wrappers and tokenizer boundaries",
                "private_policy": "cognitive context only, never evidence of external action",
            }
            return packet
        finally:
            self._pulse_context = None
            self._supplied_candidates = {}

    def _trust_allowed(self, candidate):
        if self._pulse_context is not None:
            if candidate.id in self._supplied_candidates:
                return True, "Helix recollection retains its original evidence label; admission does not verify it"
            supplied = {
                (source, item.source_content_sha256)
                for item in self._pulse_context.selected()[0]
                for source in item.source_ids if item.source_content_sha256
            }
            for rid in candidate.source_record_ids:
                record = self.store.get_record(rid)
                if record and (record.metadata.get("helix_source_id"),
                               record.metadata.get("source_sha256")) in supplied:
                    return False, "same canonical source and content supplied by Helix context; see assembly receipt"
            if candidate.metadata.get("kind") == "thought":
                candidate.section = "recalled_thought"
                return True, "private thought admitted only as cognitive context, not external evidence"
        return super()._trust_allowed(candidate)

    @staticmethod
    def _present_sections(sections):
        mapping = {"evidence": "recalled", "multi_hop": "associations",
                   "continuity": "recalled", "private": "recalled_thought"}
        presented = {}
        for native_key, values in sections.items():
            for value in values:
                key = mapping.get(native_key, native_key)
                if native_key == "continuity":
                    if value.startswith("- Earlier assistant statement (unverified):"):
                        key = "prior_assistant"
                    elif value.startswith("- Conversation:"):
                        key = "prior_user"
                presented.setdefault(key, []).append(value)
        return presented

    SECTION_TITLES = {
        **ContextCompiler.SECTION_TITLES,
        "work": "What I am working on",
        "evidence": "What I recalled — evidence and its source labels",
        "multi_hop": "Related memories and associations — recalled",
        "topical": "My recalled topic orientation",
        "summary": "My recalled summary",
        "personal": "My recalled preferences and personal context",
        "procedures": "Procedures I recalled — verification labels apply",
        "observations": "Observations I recalled — source and verification labels apply",
        "continuity": "Earlier conversation I recalled",
        "prior_assistant": "What I previously thought or said — recalled, unverified",
        "prior_user": "What was said to me before — recalled",
    }
    SECTION_ORDER = ContextCompiler.SECTION_ORDER + ("observations", "prior_user", "prior_assistant")

    def _render(self, *, mode, sections, capabilities, current_input):
        if self._pulse_context is not None:
            # Preserve the native mode/capability/response contract. Render all
            # populated sources together, instead of nesting an already
            # retrieved packet inside the next retriever's current input.
            wrapper = super()._render(mode=mode, sections={}, capabilities=capabilities,
                                      current_input="")
            suffix = "[CURRENT INPUT]\n"
            if not wrapper.endswith(suffix):
                raise RuntimeError("Loom input wrapper changed; review Helix context rendering")
            assembled, additional = self._assembled(sections)
            return wrapper[:-len(suffix)] + assembled.render(additional)

        # Native render_record supplies these prefixes from record kinds, not
        # from substring matches in their bodies. Retain each complete entry,
        # including source IDs, evidence status, timestamps and version labels.
        presented = {key: list(values) for key, values in sections.items()}
        presented["continuity"] = []
        for value in sections.get("continuity", ()):
            if value.startswith("- Earlier assistant statement (unverified):"):
                key = "prior_assistant"
            elif value.startswith("- Conversation:"):
                key = "prior_user"
            else:
                key = "continuity"
            presented.setdefault(key, []).append(value)

        # Keep native mode/capability/response-contract rendering. Supply an
        # empty input to replace only its final wrapper, never user content.
        rendered = super()._render(
            mode=mode, sections=presented, capabilities=capabilities, current_input=""
        )
        suffix = "[CURRENT INPUT]\n"
        if not rendered.endswith(suffix):
            raise RuntimeError("Loom input wrapper changed; review Helix context rendering")
        return rendered[:-len(suffix)] + "[This pulse]\n" + current_input
