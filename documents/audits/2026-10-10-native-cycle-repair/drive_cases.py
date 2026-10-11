"""Submit normal dashboard messages; await real delivery and persisted pulse return."""
import hashlib
import json
from pathlib import Path
import sys
import time
import urllib.request

run = Path(sys.argv[1])
manifest = json.loads((run / "composition-manifest.json").read_text())

def rows(path):
    result = []
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                result.append(json.loads(line))
            except json.JSONDecodeError:
                pass  # An in-progress final write is retried on the next poll.
    return result

def write(name, value):
    (run / name).write_text(json.dumps(value, indent=2, ensure_ascii=False))

def runtime():
    path = run / "data/mindscape/composition-manifest.json"
    return json.loads(path.read_text()) if path.exists() else {}

def get_outbound():
    with urllib.request.urlopen("http://127.0.0.1:5050/api/messages/outbound") as response:
        return json.load(response)

while True:
    state = runtime()
    ui = rows(run / "wizard-ui.jsonl")
    child = next((r["child_pid"] for r in reversed(ui) if r.get("child_pid")), None)
    if child and state.get("process_id") == child:
        if state.get("status") == "failed":
            raise SystemExit("Full composition failed: " + state.get("error", "unknown"))
        if state.get("status") == "initialized":
            break
    time.sleep(2)

assert len(state["runtime"]["loom_lanes"]) == 9
assert state["runtime"]["action_intent_source"] == "granite_private"
assert set(state["runtime"]["native_abilities"]) == {"move", "sense", "open", "write", "mkdir", "run"}
assert state["configuration"]["mindscape"]["workspace"] == str(run / "sensory-room")
for source in ("helix", "mightymem"):
    for name, digest in manifest[source]["files"].items():
        assert hashlib.sha256((Path(manifest[source]["root"]) / name).read_bytes()).hexdigest() == digest, name
write("runtime-parity.json", {"verified_at": time.time(), "sources_unchanged": True,
                             "normal_entrypoint": True, "runtime": state})
print("Full declared runtime and source parity verified before submitting cases.", flush=True)

for case in ("conversation", "correction", "sense", "read", "script", "missing"):
    request = json.loads((run / f"{case}.request.json").read_text())
    before = get_outbound()["total"]
    submitted = time.time()
    http = urllib.request.Request("http://127.0.0.1:5050/api/messages", data=json.dumps(request).encode(),
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(http) as response:
        ingestion = json.load(response)
    entry = {"case": case, "request": request, "submitted_at": submitted, "http_response": ingestion}
    with (run / "interactions.jsonl").open("a") as stream:
        stream.write(json.dumps(entry) + "\n")
    print("Submitted " + case, flush=True)
    while True:
        state = runtime()
        if state.get("status") == "failed":
            write("driver-failure.json", {**entry, "runtime_failure": state.get("error"), "product_result": None})
            raise SystemExit("Agent stopped explicitly: " + state.get("error", "unknown"))
        native = [r for r in rows(run / "data/mindscape/receipts.jsonl") if r.get("time", 0) >= submitted]
        contexts = [r for r in native if r.get("kind") == "pulse_context" and
                    any(request["content"] in event for event in r.get("events", []))]
        outputs = get_outbound()
        finished = [r for r in native if r.get("kind") == "foreground_return" and r.get("external_outcome_verified")]
        if contexts and outputs["total"] > before and finished:
            result = {**entry, "finished_at": time.time(), "first_pulse": contexts[0]["helix_pulse"],
                      "final_pulse": finished[-1]["helix_pulse"], "foreground": finished[-1],
                      "outbound": [r for r in outputs["messages"] if r.get("timestamp", 0) >= submitted],
                      "native_actions": [r for r in native if r.get("kind") == "native_action_return"]}
            write(f"{case}.observed.json", result)
            print(json.dumps({"case": case, "first_pulse": result["first_pulse"], "final_pulse": result["final_pulse"],
                              "actions": len(result["native_actions"]), "reply": finished[-1]["thought"]}), flush=True)
            break
        time.sleep(2)

write("stop-receipt.json", {"time": time.time(), "reason": "all requested case turns reached actual output and persisted foreground return; request normal shutdown"})
(run / "close-wizard").write_text("Close after actual case completion.\n")
