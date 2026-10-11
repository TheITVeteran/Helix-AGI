"""Gestate/resume MightyMem's native RWKV/cortex within the Helix pulse.

Helix owns cadence, mRAG, physics, foreground inference and host actions. This
adapter owns the joint recurrent state and Loom projection on one worker thread.
It does not invent motor vectors or turn an unverified thought into an outcome.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import time
from typing import Any, Sequence

from core.mindscape_config import ROOT, activate, source_receipt, write_json
from core.pulse_context import ContextContribution, PulseContext


def projection(item):
    """Content-address mutable beliefs; retain the canonical Helix source ID."""
    content = str(item["content"])
    digest = hashlib.sha256(content.encode()).hexdigest()
    source_id = str(item["id"])
    envelope = item.get("record_envelope") or {}
    kind = envelope.get("kind") or envelope.get("record_kind") or item.get("record_kind")
    if item.get("memory_type") == "thought" or kind == "thought":
        loom_kind, status, native_kind = "thought", "private", "thought"
    elif kind == "inbound_message":
        loom_kind, status, native_kind = "user", "user_reported", "inbound_message"
    elif kind == "outbound_message":
        loom_kind, status, native_kind = "assistant", "model_inferred", "outbound_message"
    else:
        # Historical status labels and model beliefs do not prove observations.
        loom_kind, status, native_kind = "episode", "unverified", "raw_memory"
    created = item.get("created_at")
    if isinstance(created, str) and created:
        parsed = datetime.fromisoformat(created.replace("Z", "+00:00"))
        created = parsed.replace(tzinfo=parsed.tzinfo or timezone.utc).timestamp()
    return {"id": f"helix:{source_id}:{digest}", "source_id": source_id,
            "content": content, "sha256": digest, "kind": loom_kind,
            "evidence_status": status, "native_kind": native_kind,
            "created_at": float(created) if created else 0.0,
            "metadata": {"helix_source_id": source_id, "source_sha256": digest,
                         "historical_projection": True, "record_envelope": envelope}}


def classify_sensed_feeling(sensed: Any, events: Sequence[str]) -> dict[str, Any]:
    """Decode RWKV recurrent cortex dynamics into an explicit sensory-motor feeling.

    Distinguishes between:
      - EXTERNAL_COMMUNICATION: outbound message/response directed at an external recipient.
      - INTERNAL_MONOLOGUE: private self-reflection / inner thought; not to be sent externally.
    """
    from habitus_ai.types import OutputTrunk

    speak_prob = 0.0
    cortex_valence = 0.0
    cortex_confidence = 0.0
    if getattr(sensed, "cortex_proposal", None) is not None:
        speak_prob = float(sensed.cortex_proposal.action_probabilities.get("SPEAK", 0.0))
        cortex_valence = float(getattr(sensed.cortex_proposal, "predicted_valence", 0.0))
        cortex_confidence = float(getattr(sensed.cortex_proposal, "confidence", 0.0))

    cycle = getattr(sensed, "cycle", None)
    selected_outputs = getattr(cycle, "selected_outputs", ()) or ()
    selected_speak = any(
        getattr(item, "trunk", None) == OutputTrunk.SPEAK or str(getattr(item, "trunk", "")) == "SPEAK"
        for item in selected_outputs
    )
    route_speak = "OUT:SPEAK" in (getattr(sensed, "route_ids", ()) or ())
    recurrent = getattr(cycle, "recurrent", None)
    recurrent_express = bool(getattr(recurrent, "should_express", False))

    # Detect if any incoming event is explicitly addressing Helix from outside
    has_inbound_speaker = False
    inbound_speaker_name = None
    inbound_channel = None
    for ev in events:
        text = str(ev).strip()
        lower = text.lower()
        if "is talking to me via" in lower:
            has_inbound_speaker = True
            cleaned = re.sub(r"^(?:\[[^\]]+\]\s*)+", "", text)
            match = re.search(r"^([A-Za-z][\w .'-]{0,39})\s+is talking to me via\s*(\w+)?", cleaned, re.IGNORECASE)
            if match:
                inbound_speaker_name = match.group(1).strip()
                if match.group(2):
                    inbound_channel = match.group(2).strip()
            break
        elif lower.startswith("user:") or lower.startswith("[user]") or "user_message" in lower:
            has_inbound_speaker = True
            inbound_speaker_name = "User"
            inbound_channel = "direct"
            break
        elif any(marker in lower for marker in ("telegram:", "discord:", "[direct]")):
            has_inbound_speaker = True
            inbound_channel = "direct"
            break

    # Determine feeling modality:
    # An external communication is felt if:
    # 1) An inbound speaker addressed us AND cortex supports speaking (or doesn't inhibit it)
    # 2) Or the recurrent state's desire/pressure indicates should_express with speak affordance/route
    # 3) Or cortex proposal strongly predicts SPEAK (prob >= 0.5)
    is_external = False
    if has_inbound_speaker and (speak_prob >= 0.25 or selected_speak or route_speak or recurrent_express):
        is_external = True
    elif selected_speak or route_speak or (recurrent_express and speak_prob >= 0.4):
        is_external = True

    modality = "EXTERNAL_COMMUNICATION" if is_external else "INTERNAL_MONOLOGUE"

    if is_external:
        feeling_tag = "[Somatic Sensory Feeling: EXTERNAL_COMMUNICATION_DIRECTED]"
        target_str = f" ({inbound_speaker_name})" if inbound_speaker_name else ""
        feeling_guidance = (
            f"{feeling_tag}\n"
            f"The RWKV recurrent cortex registers an OUTWARD COMMUNICATIVE IMPULSE "
            f"(speak_salience={speak_prob:.2f}, express_pressure={recurrent_express}). "
            f"This turn is intended as a DIRECT RESPONSE or MESSAGE to an external recipient{target_str}. "
            f"Address the recipient directly with your response. This utterance will cross the somatic membrane and be sent to them."
        )
    else:
        feeling_tag = "[Somatic Sensory Feeling: INTERNAL_MONOLOGUE_ONLY]"
        feeling_guidance = (
            f"{feeling_tag}\n"
            f"The RWKV recurrent cortex registers NO outbound communicative impulse "
            f"(speak_salience={speak_prob:.2f}, express_pressure={recurrent_express}). "
            f"This turn is PURE INTERNAL MONOLOGUE / PRIVATE REFLECTION. "
            f"Do NOT address an external interlocutor, do NOT format as a conversational message, "
            f"and do NOT leak private musings into external channels. Think purely to yourself."
        )

    return {
        "modality": modality,
        "is_external": is_external,
        "speak_probability": speak_prob,
        "recurrent_express": recurrent_express,
        "selected_speak": selected_speak,
        "route_speak": route_speak,
        "inbound_speaker": inbound_speaker_name,
        "inbound_channel": inbound_channel,
        "predicted_valence": cortex_valence,
        "confidence": cortex_confidence,
        "feeling_tag": feeling_tag,
        "feeling_guidance": feeling_guidance,
    }


class Mindscape:
    def __init__(self, config, data_dir, preconscious, *, local_models=None):
        self.config = activate(config)
        self.preconscious = preconscious
        if preconscious._unified is None:
            raise RuntimeError("Full mindscape cannot start: native Helix mRAG failed to initialize")
        self.directory = Path(data_dir).resolve() / "mindscape"
        self.directory.mkdir(parents=True, exist_ok=True)
        self._owner = (self.directory / "launcher.lock").open("a")
        try:
            fcntl.flock(self._owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self._owner.close()
            raise RuntimeError(f"Mindscape already has a launcher owner: {self.directory}") from None
        self._worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="helix-mindscape")
        self._closed = False
        self.native = None
        self.loom = None
        self.manifest = {
            "schema": "helix-mindscape-composition-v1",
            "process_id": os.getpid(),
            "status": "initializing",
            "entrypoint": "main.py -> setup_helix -> PulseLoop._pulse",
            "helix": source_receipt(ROOT),
            "mightymem": source_receipt(self.config["mindscape"]["package_path"]),
            "configuration": {key: self.config[key] for key in (
                "composition", "pulse_mode", "local_provider", "local_model", "local_context_window", "mindscape")},
            "stores": {"canonical": str(Path(data_dir).resolve()), "joint_state": str(self.directory / "joint"),
                       "loom_projection": str(self.directory / "loom.sqlite")},
            "route": ["Helix canonical memory and beliefs", "native mRAG and Context Office",
                      "Helix preconscious and 8D physics", "MightyMem Habitus graph and cortex",
                      "RWKV recurrent input and native cortex bridge", "Context Loom compiler",
                      "local Granite foreground", "Helix action/channel path", "canonical post-pulse persistence"],
            "hardware": {"platform": platform.platform(), "neural_device": "cpu"},
            "local_models": local_models,
            "evaluation": {"kind": "composition initialization", "dataset": None, "grader": None,
                           "product_result": None},
            "boundaries": {
                "new_action_or_reasoning_ceiling": None, "sync_record_limit": None,
                "rwkv_chunk_tokens": {"value": 128, "meaning": "native compute batch; all input tokens consumed"},
                "loom_context": {"value": self.config["local_context_window"], "reason": "selected foreground context"},
                "loom_adaptive_shortlist": "disabled; compiler uses selected context",
                "private_evidence": "typed cognitive context only; not factual or action evidence",
                "inherited_helix_limits": "unchanged; preconscious selection, provider retries, tool orchestration and context lifecycle require a separate audit before behavioral scoring",
            },
            "capability_status": {
                "rwkv_role": "native recurrent input/cortex coupling; Granite retains foreground language",
                "non_tool_file_motor": "not established by composition startup",
                "rwkv_gradient_training": False,
                "cortex_plasticity": "native Habitus runtime; no fabricated rewards",
            },
        }
        write_json(self.directory / "composition-manifest.json", self.manifest)
        try:
            self._worker.submit(self._open).result()
            self.sync()
            self._worker.submit(self._checkpoint, "helix-launch-sync").result()
            self.manifest["status"] = "initialized"
            write_json(self.directory / "composition-manifest.json", self.manifest)
        except BaseException as error:
            self.manifest.update(status="failed", error=f"{type(error).__name__}: {error}")
            write_json(self.directory / "composition-manifest.json", self.manifest)
            self._worker.submit(self._release).result()
            self._worker.shutdown(wait=True)
            self._owner.close()
            raise

    def _receipt(self, kind, **values):
        with (self.directory / "receipts.jsonl").open("a") as stream:
            stream.write(json.dumps({"time": time.time(), "kind": kind, **values}, default=str, allow_nan=False) + "\n")

    def _open(self):
        from habitus_ai.continual_mind import ContinualMind
        from context_loom.engine import ContextLoom
        from context_loom.compiler import CompilerConfig, AdaptiveBudgetPolicy
        from context_loom.topical import TopicalTracker
        from core.mindscape_context import MindscapeContextCompiler
        from core.mindscape_lanes import HabitusLane, SemanticBridge
        # Reading a chunk must not inspect only its first four sentences.
        # All sentence heads participate; existing derived-head and candidate
        # policies remain visible inherited boundaries, not coverage claims.
        self.preconscious._unified.lane_a.contextual_sentence_heads = True
        joint = self.directory / "joint"
        resumed = (joint / "LATEST.json").exists()
        if not resumed and self.config["mindscape"]["gestation"] == "resume_only":
            raise RuntimeError(f"Resume required but no joint checkpoint exists: {joint}")
        self.native = ContinualMind(model=Path(self.config["mindscape"]["rwkv_model"]),
                                    directory=joint, workspace=Path(self.config["mindscape"]["workspace"]))
        self.native.backend.training_enabled = False
        if str(self.native.backend.device) != "cpu" or str(self.native.runtime.cortex.device) != "cpu":
            raise RuntimeError("Native joint bridge initialized on an undeclared device")
        self.loom = ContextLoom(self.directory / "loom.sqlite",
            config=CompilerConfig(model_context_tokens=int(self.config["local_context_window"]),
                                  reserved_output_tokens=0,
                                  adaptive_budget=AdaptiveBudgetPolicy(enabled=False),
                                  render_capability_schemas=False),
            embedding_provider=SemanticBridge(self.preconscious.physics.semantic_encoder),
            install_default_capabilities=False)
        compiler = self.loom.compiler
        self.loom.compiler = MindscapeContextCompiler(
            compiler.store, config=compiler.config,
            embedding_provider=compiler.embedding_provider,
            lanes=compiler.lanes, token_counter=compiler.token_counter,
            focus_profiles=self.config["mindscape"]["context_focus_profiles"],
        )
        self.graph_lane = HabitusLane(self.native.mind)
        self.loom.compiler.lanes.append(self.graph_lane)
        with self.loom.store.connection:
            self.loom.store.connection.execute(
                "CREATE TABLE IF NOT EXISTS helix_graph_projection (record_id TEXT PRIMARY KEY)")
        self.topical = TopicalTracker(self.loom.store)
        self.manifest["runtime"] = {
            "gestation": "resumed" if resumed else "new",
            "rwkv": self.native.backend.identity,
            "rwkv_parameters": self.native.backend.statistics["weight_tensor_elements"],
            "cortex_parameters": self.native.runtime.cortex.parameter_count,
            "joint_generation": self.native.generation,
            "loom_lanes": [lane.name for lane in self.loom.compiler.lanes],
            "context_compiler": "core.mindscape_context.MindscapeContextCompiler",
            "context_layout": "independent-retrieval-focus-context-v3",
            "context_focus_profiles": self.loom.compiler.focus_profiles,
            "context_focus_status": "configurable bootstrap priorities; not learned RWKV attention",
            "context_queries": "fresh events; last complete private thought only on idle continuation",
            "context_receipt": "pulse_context.context_assembly plus native loom_packet manifest",
            "inline_annotations": "exact unique passage anchors from actual mRAG sentence-head returns; no truth or permission inference",
            "sentence_coverage": "all nonempty sentence views; inherited candidate/context admission limits remain",
            "mrag": type(self.preconscious._unified.lane_a).__module__,
            "embedding": self.loom.compiler.embedding_provider.identity,
        }
        self._receipt("initialized", **self.manifest["runtime"])
        if not resumed:
            # Preserve the actual gestation before slow historical indexing.
            # A later sync failure must not strand an uncheckpointed mind.
            self._checkpoint("helix-gestation")

    def sync(self):
        # Read the actual Helix corpus on its calling thread. Nothing is sampled
        # or replaced by a prepared candidate cache.
        items = [projection(item) for item in self.preconscious._unified.corpus.all_items()]
        return self._worker.submit(self._sync, items).result()

    def _sync(self, items):
        from context_loom.models import RecordKind, EvidenceStatus
        from habitus_ai.types import RecordType, InputTrunk
        added = 0
        indexed = 0
        heads = json.loads(self.native.mind.store.get_metadata("helix_sync_heads", "{}"))
        for item in items:
            rid = item["id"]
            metadata = item["metadata"]
            previous = heads.get(item["source_id"])
            supersedes = previous if previous and previous != rid else None
            if self.native.mind.store.get_record(rid) is None:
                self.native.mind.remember(item["content"], record_id=rid, event_id=rid,
                    source_id="helix-canonical-projection", record_type=RecordType(item["native_kind"]),
                    timestamp=datetime.fromtimestamp(item["created_at"], timezone.utc).isoformat(),
                    input_trunk=InputTrunk.NOTICE, metadata=metadata, supersedes_id=supersedes,
                    provenance={"source_record_ids": [item["source_id"]], "evidence_status": item["evidence_status"]})
            present = self.loom.store.get_record(rid) is not None
            projected = self.loom.store.connection.execute(
                "SELECT 1 FROM helix_graph_projection WHERE record_id=?", (rid,)).fetchone()
            if not projected:
                self.loom.log(speaker="helix-canonical", kind=RecordKind(item["kind"]),
                    content=item["content"], scope="helix", record_id=rid,
                    created_at=item["created_at"], source_ids=[item["source_id"]], metadata=metadata,
                    evidence_status=EvidenceStatus(item["evidence_status"]), supersedes_id=supersedes)
                self.loom.graph_store.index_record(rid, item["content"])
                with self.loom.store.connection:
                    self.loom.store.connection.execute(
                        "INSERT INTO helix_graph_projection(record_id) VALUES (?)", (rid,))
                indexed += 1
            if not present:
                added += 1
            heads[item["source_id"]] = rid
        self.native.mind.store.set_metadata("helix_sync_heads", json.dumps(heads))
        self._receipt("canonical_sync", source_records=len(items), added=added, graph_indexed=indexed,
                      gradient_updates=0, source_ids=[item["source_id"] for item in items])
        return added

    def prepare(self, events, message, pulse, *, context: PulseContext):
        try:
            self.sync()
            mrag = dict(self.preconscious._unified.last_stats)
            mrag["query"] = getattr(self.preconscious, "_last_retrieval_query", "")
            mrag["passage_hits"] = getattr(self.preconscious._unified.lane_a, "last_anchor_hits", {})
            if context.pulse != pulse:
                raise ValueError("Pulse context does not match current pulse")
            return self._worker.submit(self._prepare, list(events), context, pulse, mrag).result()
        except Exception as error:
            self.fail(error, events, message, pulse)
            raise

    def fail(self, error, events, message, pulse):
        self.manifest.update(status="failed", error=f"{type(error).__name__}: {error}")
        write_json(self.directory / "composition-manifest.json", self.manifest)
        write_json(self.directory / "pending-failed-pulse.json", {
            "pulse": pulse, "events": list(events), "message": message,
            "error": str(error), "recovery": "resume the last joint checkpoint and explicitly resubmit the preserved input"})

    def _prepare(self, events, context, pulse, mrag):
        from habitus_ai.developmental_runtime import DevelopmentalInput
        from habitus_ai.types import InputTrunk
        before = hashlib.sha256(self.native.backend.dump_state()).hexdigest()
        inputs = []
        token_count = 0
        for event in events:
            # These are Helix's provenance-bearing event strings, not recalled
            # context replayed as a fresh utterance. No gradient learning here.
            ids = self.native.backend.encode(event)
            if ids:
                self.native.backend.consume(ids)
                token_count += len(ids)
            inputs.append(DevelopmentalInput(content=event, lane=InputTrunk.NOTICE,
                source_id="helix-pulse-event", motor_eligible=False,
                embedding=tuple(self.native.runtime.embedder.embed(event)),
                metadata={"helix_pulse": pulse, "unverified_event": True}))
        sensed = self.native.runtime.advance(tuple(inputs), allow_idle=not inputs)
        self.native.backend.begin_slice()
        self.native.latest_pulse = sensed
        frame = self.topical.observe_turn(getattr(self.graph_lane, "paths", ()))

        feeling = classify_sensed_feeling(sensed, events)
        self.last_sensed_feeling = feeling
        self.last_sensed_modality = feeling["modality"]

        state = {"habitus_pulse": self.native.mind.pulse,
                 "rwkv_input_tokens": token_count,
                 "sensed_modality": feeling["modality"],
                 "communicative_intent": feeling["is_external"],
                 "speak_salience": round(feeling["speak_probability"], 3),
                 "recurrent_express": feeling["recurrent_express"],
                 "cortex_proposal": asdict(sensed.cortex_proposal) if sensed.cortex_proposal else None,
                 "topical": frame.as_dict(), "external_evidence": False}
        context = context.extend(
            ContextContribution("direction", feeling["feeling_guidance"], "habitus_modality",
                                kind="output_direction", evidence="internal state"),
            ContextContribution("state", "Recurrent state — not external evidence:\n" + json.dumps(state),
                                "rwkv_cortex", kind="internal_state", evidence="internal state"))
        packet = self.loom.compiler.compile_pulse(context, scope="helix")
        after = hashlib.sha256(self.native.backend.dump_state()).hexdigest()
        self._receipt("pulse_context", helix_pulse=pulse, events=events, rwkv_tokens=token_count,
            joint_state_before=before, joint_state_after=after, habitus_pulse=self.native.mind.pulse,
            sensed_modality=feeling["modality"], communicative_intent=feeling["is_external"],
            cortex_proposal=asdict(sensed.cortex_proposal) if sensed.cortex_proposal else None,
            graph_field=list(sensed.graph_field), topical=frame.as_dict(),
            mrag=mrag, loom_packet=packet.to_dict(), graph_trace=self.graph_lane.trace,
            context_assembly=self.loom.compiler.last_assembly_receipt)
        return packet.rendered

    def finish(self, thought, pulse, *, delivered_external=False):
        try:
            self.sync()
            return self._worker.submit(self._finish, thought, pulse, delivered_external).result()
        except Exception as error:
            self.fail(error, [], thought, pulse)
            raise

    def _finish(self, thought, pulse, delivered_external=False):
        feeling = getattr(self, "last_sensed_feeling", None) or {}
        was_external_felt = feeling.get("is_external", False)
        has_outbound_tag = any(tag in thought for tag in ("[REPLY:", "[SPEAK:", "[MESSAGE:", "[response]"))
        is_external_response = bool(
            delivered_external
            or (was_external_felt and not str(thought).startswith(("[internal error:", "[no LLM session")))
            or (has_outbound_tag and delivered_external)
        )

        self._receipt("foreground_return", helix_pulse=pulse, thought=thought,
                      modality="external_response" if is_external_response else "internal_monologue",
                      sensed_modality=feeling.get("modality", "INTERNAL_MONOLOGUE"),
                      external_outcome_verified=is_external_response)
        self._checkpoint(f"helix-pulse-{pulse}")
        return {"is_external_response": is_external_response,
                "modality": "external_response" if is_external_response else "internal_monologue"}

    def _checkpoint(self, label):
        manifest = self.native.save(label=label)
        self._receipt("joint_checkpoint", label=label, generation=manifest["generation"],
                      numeric_state_sha256=manifest["numeric_state_sha256"], files=manifest["files"])

    def _release(self):
        if self.loom is not None:
            self.loom.close()
            self.loom = None
        if self.native is not None:
            self.native.close()
            self.native = None

    def close(self):
        if not self._closed:
            self._closed = True
            try:
                self._worker.submit(self._release).result()
            finally:
                self._worker.shutdown(wait=True)
                self._owner.close()
