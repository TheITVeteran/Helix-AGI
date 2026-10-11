"""Read-only analysis of the real wizard run; NOT a new product evaluation.

Only two production helpers execute: history serialization and topic tracking.
No model, retriever, database, agent loop, or canonical state is initialized.
Run from the repository root with venv/bin/python; JSON goes to stdout.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "documents/audits/2026-10-10-operational-recheck"
sys.path.insert(0, str(ROOT))


def read(name):
    return json.loads((RUN / name).read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = read("composition-manifest.json")
    archived_hashes = read("artifact-hashes.json")
    used = ["composition-manifest.json", "runtime-receipts.jsonl", "trace.jsonl"]
    names = ("conversation", "sense", "read", "script")
    used += [f"cases/{name}/{kind}.json" for name in names
             for kind in ("provider", "context", "delivered", "ingestion")]
    artifact_checks = {}
    for name in used:
        actual = digest(RUN / name)
        assert actual == archived_hashes[name], f"Archived evidence changed: {name}"
        artifact_checks[name] = actual

    source_checks = {}
    sources = {
        "helix": ["core/context_compressor.py", "core/mindscape.py",
                  "core/mindscape_lanes.py", "core/mindscape_context.py",
                  "core/pulse_context.py", "core/context_focus.py",
                  "core/preconscious.py", "core/unified_retrieval.py",
                  "llm/providers/ollama_provider.py"],
        "mightymem": ["context_loom/compiler.py", "context_loom/topical.py",
                      "habitus_ai/retrieval.py"],
    }
    for group, files in sources.items():
        for name in files:
            actual = digest(Path(manifest[group]["root"]) / name)
            assert actual == manifest[group]["files"][name], f"Source drift: {name}"
            source_checks[f"{group}/{name}"] = actual

    canonical_before = {name: digest(ROOT / name) for name in manifest["canonical_before"]}
    trace = [json.loads(line) for line in (RUN / "trace.jsonl").open()]
    receipts = [json.loads(line) for line in (RUN / "runtime-receipts.jsonl").open()]
    contexts = sorted((x for x in receipts if x.get("kind") == "pulse_context"),
                      key=lambda x: x["helix_pulse"])
    cases = {name: {"context": read(f"cases/{name}/context.json"),
                    "provider": read(f"cases/{name}/provider.json")[0]} for name in names}
    boot = cases["conversation"]["provider"]["locals"]["messages"][1:3]
    boot_deliver = next(x for x in trace if x["function"] == "_deliver_mindscape_output")
    first = cases["conversation"]
    combined_first = "\n".join(m["content"] for m in first["provider"]["locals"]["messages"])
    assert first["context"]["events"][0] in combined_first
    assert combined_first.count(boot[1]["content"]) == 2
    assert "inner voice" in boot[0]["content"]
    assert "cat traversing tiled flooring" in boot[0]["content"]
    assert not contexts[0]["events"]

    per_case = {}
    for name, case in cases.items():
        context, provider = case["context"], case["provider"]
        packet = context["loom_packet"]
        messages = provider["locals"]["messages"]
        assert messages[-1]["content"] == packet["rendered"]
        current = context["context_assembly"]["sections"]["messages"]
        assert all(event in messages[-1]["content"] for event in current)
        graph_entries = [entry for entry in packet["manifest"]
                         if entry["admitted"] and entry["lanes"].get("habitus_graph")]
        assert all(entry["lanes"]["habitus_graph"] == 1.0 and
                   entry["lane_ranks"]["habitus_graph"] == 1 for entry in graph_entries)
        per_case[name] = {
            "pulse": context["helix_pulse"],
            "provider_model": provider["model"],
            "packet_matches_actual_request": True,
            "request_time": provider["time"],
            "request_message_lengths": [len(m["content"]) for m in messages],
            "total_content_chars": sum(len(m["content"]) for m in messages),
            "fresh_message_chars": sum(map(len, current)),
            "packet_chars": len(packet["rendered"]),
            "fresh_heading_offset": packet["rendered"].index("[What was said to me now]"),
            "section_content_chars": {k: sum(map(len, v)) for k, v in
                                      context["context_assembly"]["sections"].items()},
            "packet_counter": context["context_assembly"]["token_counter"],
            "packet_tokens": packet["token_count"],
            "prompt_eval_count": provider["locals"]["response"]["prompt_eval_count"],
            "eval_count": provider["locals"]["response"]["eval_count"],
            "done_reason": provider["locals"]["response"]["done_reason"],
            "graph_boosted_admitted_records": graph_entries,
            "mrag_initial_query": context["mrag"].get("query"),
            "mrag_last_query": context["mrag"].get("memory_work_order", {}).get("raw_message"),
            "task_id": packet["task_id"],
        }

    # Narrow implementation reproduction, using exactly the saved history.
    from core.context_compressor import ContextCompressor
    compressor = ContextCompressor(context_length=8192, threshold_percent=0.5)
    read_provider = cases["read"]["provider"]
    full_history = read_provider["locals"]["messages"][1:] + [
        {"role": "assistant", "content": read_provider["result"]}]
    history = [{"role": "model" if m["role"] == "assistant" else "user",
                "parts": [{"text": m["content"]}]} for m in full_history]
    tail_start = compressor._find_tail_cut(history)
    middle = history[compressor.protect_first_n:tail_start]
    serialized = compressor._serialize_for_summary(middle)
    summary_call = next(x for x in trace if x["function"] == "_send_via_package"
                        and any("TURNS TO COMPRESS:" in m["content"]
                                for m in x["locals"]["messages"]))
    actual_summary_input = summary_call["locals"]["messages"][-1]["content"]
    assert serialized in actual_summary_input
    assert tail_start == 5 and len(middle) == 3
    assert "[What was said to me now]" not in serialized
    lost_events = {}
    for name in ("conversation", "sense"):
        event = cases[name]["context"]["context_assembly"]["sections"]["messages"][0]
        original = cases[name]["provider"]["locals"]["messages"][-1]["content"]
        one = compressor._serialize_for_summary([{"role": "user", "parts": [{"text": original}]}])
        assert event in original and event not in one
        lost_events[name] = {"event": event, "lost_from_own_serialized_turn": True,
                             "elsewhere_in_summary_input": event in actual_summary_input}
    script_messages = cases["script"]["provider"]["locals"]["messages"]
    assert script_messages[1:3] == boot
    assert summary_call["result"] in script_messages[3]["content"]
    fabricated_claim = "My response focused on suggesting clear, descriptive file naming conventions"
    assert fabricated_claim in summary_call["result"]
    assert fabricated_claim not in "\n".join(c["provider"]["result"] for c in cases.values())
    assert summary_call["time"] > cases["read"]["provider"]["time"]

    # The actual pure topic tracker consumes the previous compile's dictionary paths.
    native = Path(manifest["mightymem"]["root"])
    spec = importlib.util.spec_from_file_location("helix_audit_topical", native / "context_loom/topical.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    tracker = module.TopicalTracker(store=None)
    previous_paths, topic_checks = (), []
    for context in contexts:
        actual = tracker.observe_turn(previous_paths).as_dict()
        assert actual == context["topical"]
        topic_checks.append({"pulse": context["helix_pulse"], "frame": actual,
                             "received_path_keys": sorted(previous_paths[0]) if previous_paths else []})
        previous_paths = context["graph_trace"]["y_paths"]
    assert all(x["frame"]["focus_topics"] == [""] and x["frame"]["drift"] == 0.0
               for x in topic_checks[1:])
    assert cases["read"]["provider"]["locals"]["messages"][:6] == cases["sense"]["provider"]["locals"]["messages"]
    canonical_after = {name: digest(ROOT / name) for name in canonical_before}
    assert canonical_before == canonical_after
    for name, expected in artifact_checks.items():
        assert digest(RUN / name) == expected

    print(json.dumps({
        "kind": "saved-live-receipt-analysis-and-narrow-implementation-diagnostics",
        "new_product_run": False, "product_score": None,
        "source_run": str(RUN), "artifact_hashes_verified": artifact_checks,
        "source_hashes_verified_against_run": source_checks,
        "pulse_loop_source_exception": "Later wake scheduling repair; not imported by these diagnostics",
        "canonical_files_unchanged_during_analysis": len(canonical_before),
        "boot": {"events": contexts[0]["events"], "rwkv_tokens": contexts[0]["rwkv_tokens"],
                 "selected_modality": contexts[0]["sensed_modality"],
                 "outbound_flag_returned": boot_deliver["result"],
                 "recipient": boot_deliver["locals"].get("recipient"),
                 "channel": boot_deliver["locals"].get("channel"),
                 "caution": "Direct logging returned delivered=True; no dashboard recipient receipt",
                 "first_reply_full_text_copies_in_next_request": 2},
        "cases": per_case,
        "compression": {"exact_serialization_matches_live_auxiliary_input": True,
                        "serialized_input": serialized, "summary_time": summary_call["time"],
                        "summary_output": summary_call["result"], "lost_events": lost_events,
                        "fabricated_completion_claim": fabricated_claim,
                        "summary_supplied_in_script_request": True, "boot_exchange_preserved": True,
                        "initial_failure_precedes_compression": True},
        "topic_tracker_reproduction": topic_checks,
        "interpretation_limits": [
            "Counts and deterministic transformations are not transformer attention measurements.",
            "No intervention isolated the behavioral contribution of any one mechanism.",
            "Later prompt-token drop despite a longer request suggests server pruning; exact removed spans unknown.",
            "No claim that a model change, larger context, or any proposed repair fixes conversation.",
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
