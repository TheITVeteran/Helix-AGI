"""Collect actual launcher evidence; never synthesize missing agent results."""
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import time

from llm.ollama_tokens import OllamaTokenCounter

run, audit = map(Path, sys.argv[1:3])
audit.mkdir(parents=True, exist_ok=True)
def rows(path):
    result = []
    for line in path.read_text().splitlines() if path.exists() else []:
        try:
            result.append(json.loads(line))
        except ValueError:
            pass
    return result

def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False))

manifest = json.loads((run / "composition-manifest.json").read_text())
native = [r for r in rows(run / "data/mindscape/receipts.jsonl") if r.get("time", 0) >= manifest["created"]]
trace = rows(run / "trace.jsonl")
journal = rows(run / "data/memory/cognitive_journal.jsonl")
counter = OllamaTokenCounter(manifest["models"]["foreground"])
checks = []
connection = sqlite3.connect((run / "data/mindscape/joint/mind.sqlite").as_uri() + "?mode=ro", uri=True)
connection.row_factory = sqlite3.Row
def row(table, key, value):
    found = connection.execute(f"SELECT * FROM {table} WHERE {key}=?", (value,)).fetchone()
    return dict(found) if found else None

action_checks = []
for action in (entry for entry in native if entry.get("kind") == "native_action_return"):
    receipt = action.get("receipt")
    if not receipt:
        action_checks.append({"helix_pulse": action["helix_pulse"], "action": action["action"],
                              "executed": False, "error": action.get("error")})
        continue
    call = row("records", "record_id", receipt["output_record_id"])
    returned = row("records", "record_id", receipt["return_record_id"])
    cycle = row("experience_cycles", "cycle_id", receipt["cycle_id"])
    outcome = row("outcomes", "outcome_id", receipt["outcome_id"])
    return_payload = json.loads(returned["text"]) if returned else {}
    outcome_payload = json.loads(outcome["payload_json"]) if outcome else {}
    call_metadata = json.loads(call["metadata_json"]) if call else {}
    next_contexts = [entry for entry in native if entry.get("kind") == "pulse_context"
                     and entry.get("helix_pulse", 0) > action["helix_pulse"]
                     and receipt["receipt_id"] in entry.get("loom_packet", {}).get("rendered", "")]
    action_checks.append({"helix_pulse": action["helix_pulse"], "action": action["action"],
                         "receipt_id": receipt["receipt_id"], "status": receipt["status"],
                         "authorized_call": bool(call_metadata.get("self_pulse_authorization_id"))
                             and call_metadata.get("authorized_output_node_id") == receipt["tool_id"]
                             and call_metadata.get("arguments") == receipt["arguments"],
                         "closed_cycle": bool(cycle and cycle["status"] == "closed"
                             and cycle["terminal_return_record_id"] == receipt["return_record_id"]),
                         "persisted_actual_return": bool(returned and return_payload.get("output") == receipt["output"]
                             and return_payload.get("status") == receipt["status"] and return_payload.get("error") == receipt["error"]),
                         "linked_outcome": outcome_payload.get("receipt_id") == receipt["return_record_id"],
                         "verified_outcome": outcome_payload.get("verified"),
                         "action_return_credit": outcome_payload.get("stability_delta"),
                         "credited_edges": outcome_payload.get("credited_edge_ids"),
                         "rwkv_return_tokens": action.get("rwkv_return_tokens"),
                         "subsequent_context_pulses": [entry["helix_pulse"] for entry in next_contexts],
                         "call": call, "return": returned, "cycle": cycle, "outcome": outcome})
connection.close()
write(audit / "native-action-evidence.json", action_checks)
for case in manifest["dataset"]:
    observed = run / f"{case}.observed.json"
    if not observed.exists():
        checks.append({"case": case, "completed_output_chain": False})
        continue
    result = json.loads(observed.read_text())
    # Submission can overlap a boot pulse. Attribute actions only from the
    # pulse that actually received this case, not merely from wall-clock overlap.
    attributed_actions = [entry for entry in result["native_actions"]
                          if result["first_pulse"] <= entry["helix_pulse"] <= result["final_pulse"]]
    directory = audit / "cases" / case
    directory.mkdir(parents=True, exist_ok=True)
    contexts = [r for r in native if r.get("kind") == "pulse_context" and result["first_pulse"] <= r.get("helix_pulse", 0) <= result["final_pulse"]]
    ingestion = [r for r in journal if result["request"]["content"] in r.get("content", "")]
    providers = [r for r in trace if r.get("function") == "_send_via_package" and r.get("thread") == "helix_pulse"
                 and result["submitted_at"] <= r["time"] <= result["finished_at"]
                 and any(any(message["role"] == "user" and message["content"].endswith(context["loom_packet"]["rendered"])
                             for message in r["locals"]["messages"]) for context in contexts)]
    token_checks = []
    for provider in providers:
        messages = provider["locals"]["messages"]
        response = provider["locals"].get("response") or {}
        predicted = counter.count_messages(messages)
        token_checks.append({"request_tokens": predicted, "evaluated_tokens": response.get("prompt_eval_count"),
                             "full_input_accounted": predicted == response.get("prompt_eval_count"),
                             "done_reason": response.get("done_reason"), "generated_tokens": response.get("eval_count")})
    exact = all(any(any(message["content"].endswith(context["loom_packet"]["rendered"])
                            for message in provider["locals"]["messages"])
                        for provider in providers) for context in contexts)
    checks.append({"case": case, "completed_output_chain": bool(contexts and providers and ingestion and result["outbound"]),
                   "canonical_input_ids": [r.get("id") for r in ingestion], "context_packets_reached_provider": exact,
                   "provider_checks": token_checks, "native_action_count": len(attributed_actions),
                   "native_action_pulses": [entry["helix_pulse"] for entry in attributed_actions],
                   "first_pulse": result["first_pulse"], "final_pulse": result["final_pulse"]})
    for name, value in (("observed", result), ("contexts", contexts), ("providers", providers), ("ingestion", ingestion)):
        write(directory / f"{name}.json", value)

root = Path(manifest["helix"]["root"])
verification = {"collected_at": time.time(), "collector_sha256": sha(Path(__file__)),
                "provider_attribution": "exact case pulse packet in actual model input, not wall-clock overlap alone",
                "full_readiness_result": None, "cases": checks,
                "canonical_files_checked": len(manifest["canonical_before"]),
                "canonical_changes": [name for name, digest in manifest["canonical_before"].items() if sha(root / name) != digest],
                "source_changes": {source: [name for name, digest in manifest[source]["files"].items()
                                             if sha(Path(manifest[source]["root"]) / name) != digest] for source in ("helix", "mightymem")},
                "workspace_files": {str(p.relative_to(run / "sensory-room")): {"sha256": sha(p), "size_bytes": p.stat().st_size}
                                    for p in (run / "sensory-room").rglob("*") if p.is_file()}}
write(audit / "verification.json", verification)
for name in ("composition-manifest.json", "runtime-parity.json", "host-runtime.json", "wizard-ui.jsonl", "trace.jsonl", "interactions.jsonl",
             "wizard-console.log", "cases-console.log", "stop-receipt.json", "driver-failure.json", "run.sh"):
    if (run / name).exists():
        shutil.copy2(run / name, audit / name)
for name in ("helix.log", "launcher.log", "bootstrap.log"):
    if (run / "logs" / name).exists():
        shutil.copy2(run / "logs" / name, audit / name)
shutil.copy2(run / "data/mindscape/composition-manifest.json", audit / "runtime-composition.json")
(audit / "runtime-receipts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in native))
for source in (run / "sensory-room/inbox").iterdir():
    target = audit / "input-files" / source.name
    target.parent.mkdir(exist_ok=True)
    shutil.copy2(source, target)
write(audit / "artifact-hashes.json", {str(p.relative_to(audit)): sha(p) for p in audit.rglob("*") if p.is_file() and p.name != "artifact-hashes.json"})
print(json.dumps(verification, indent=2))
