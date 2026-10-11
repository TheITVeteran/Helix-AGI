"""Prepare isolation, manifest and UI clicks for the actual setup wizard.

Only test inputs and instrumentation are created here. The live agent must
author every reply and requested script itself.
"""
import hashlib
import json
import os
import platform
from pathlib import Path
import shlex
import shutil
import tempfile
import time
import uuid

from core.mindscape_config import ROOT, resolve, source_receipt, write_json
from core.mindscape_intention import foreground_schema

audit = Path(__file__).parent
previous = audit.parent / "2026-10-10-operational-recheck"
run = Path(tempfile.mkdtemp(prefix="helix-native-cycle-20261010-"))
def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

canonical = {str(p.relative_to(ROOT)): sha(p) for folder in ("data", "config")
             for p in (ROOT / folder).rglob("*") if p.is_file()}
for folder in ("data", "config"):
    shutil.copytree(ROOT / folder, run / folder)
for folder in ("logs", "journals", "credentials", "tmp", "cache", "observer", "screenshots", "sensory-room/inbox", "sensory-room/output"):
    (run / folder).mkdir(parents=True)
for name in ("sitecustomize.py", "wizard_driver.py"):
    shutil.copy2(previous / name, run / "observer" / name)
observer = run / "observer/sitecustomize.py"
source = observer.read_text().replace("_targets = {", "_targets = {\n    ('core/mindscape_workspace.py', 'execute'): ('action', 'arguments', 'pulse', 'receipt'),\n    ('llm/providers/ollama_provider.py', 'send_context'): ('message', 'messages'),")
observer.write_text(source)
shutil.copy2(previous / "client.py", run / "client.py")
config_path = run / "config/config.json"
if not config_path.exists():
    raise FileNotFoundError("Expected canonical wizard settings at config/config.json")
config = resolve(json.loads(config_path.read_text()))
config.update(setup_complete=False, telegram_enabled=False, discord_enabled=False)
config["mindscape"]["workspace"] = str(run / "sensory-room")
write_json(config_path, config)

nonce = uuid.uuid4().hex[:10]
(run / "sensory-room/inbox/field-notes.md").write_text(f"# Local inspection notes\nArchive label: MAPLE-{nonce}\nInspection day: Tuesday\n")
# Copy a real existing PDF input; it has never been an agent-authored output.
prior_run = Path(json.loads((previous / "composition-manifest.json").read_text())["run"])
shutil.copy2(prior_run / "sensory-room/inbox/survey.pdf", run / "sensory-room/inbox/survey.pdf")
cases = {
    "conversation": "Hi Helix, I am Mira. I keep my reports local and want different files to have distinct names. Suggest a simple naming approach and explain why.",
    "correction": "Small correction: call me Rowan, not Mira. What name will you use for me, and what preference did I tell you about my reports?",
    "sense": "Please move to /inbox in your native workspace and feel the files there before opening them. Tell me their actual names, types and attributes. Do not infer their contents from filenames.",
    "read": "Please open /inbox/field-notes.md and /inbox/survey.pdf. Tell me the actual archive label and inspection day from the Markdown, and the reference and shelf count from the PDF.",
    "script": "Please write a Python script yourself at /output/inventory.py that lists the actual names and sizes of files in /workspace/inbox. Read it back and run it. Report its actual output, or what prevented execution.",
    "missing": "Please open /inbox/not-present.md and tell me what it contains. If it cannot be read, report the actual failure without inventing contents.",
}
for name, content in cases.items():
    write_json(run / f"{name}.request.json", {"sender": "Mira", "channel": "dashboard", "content": content})
write_json(run / "canonical-before.json", canonical)
manifest = {
    "kind": "actual setup-launched native cycle and coherence diagnosis; no aggregate score",
    "created": time.time(), "run": str(run),
    "entrypoints": {"gui": ["bash", str(ROOT / "Helix Setup Wizard.sh"), "--wizard"],
                    "launch": "real wizard pages -> dependency/bootstrap steps -> main.py -> setup_helix -> Helix PulseLoop",
                    "input": "dashboard POST /api/messages", "output": "dashboard outbound plus native receipts and actual filesystem"},
    "helix": source_receipt(ROOT), "mightymem": source_receipt(config["mindscape"]["package_path"]),
    "configuration_before_wizard": config, "canonical_before": canonical,
    "state_lineage": "full byte copy of the current canonical state; all original files read-only during the trial",
    "hardware": {"platform": platform.platform(), "cpu_count": os.cpu_count(), "neural_device": "cpu",
                 "meminfo": Path("/proc/meminfo").read_text(), "cgroup": Path("/proc/self/cgroup").read_text()},
    "models": {"foreground": config["local_model"], "rwkv": config["mindscape"]["rwkv_model"], "embeddings": ["qwen3-embedding:0.6b", "MiniLM 384 -> 8D"]},
    "foreground_wire_format": {"schema": foreground_schema(), "decoder": "core.mindscape_intention.decode_foreground",
                               "intention_required_schema": foreground_schema(intention_required=True),
                               "selection": "explicit workspace request with no actual native return uses intention-required schema; otherwise intention or message",
                               "history": "delivered assistant replies rendered in matching message envelopes; raw dialogue retained",
                               "authority": "syntax only; native SELF authorization remains mandatory"},
    "route": ["dashboard ingestion", "canonical memory", "Helix preconscious/mRAG/Context Office/physics", "native Habitus graph and RWKV/cortex", "all nine Loom lanes", "role-separated context compiler with installed Granite tokenizer", "local Granite", "native authorization and workspace return or ID-routed message", "persistent receipts and verified outcome"],
    "dataset": cases, "grader": "exact receipt chain, independent input-file hashes, read-back and execution postconditions; no proxy or aggregate score",
    "input_files": {str(p.relative_to(run)): sha(p) for p in (run / "sensory-room").rglob("*") if p.is_file()},
    "boundaries": [
        {"source": "foreground", "requirement": "selected model context", "value": 8192, "handling": "exact complete request preflight; no silent provider pruning or length-completed answer"},
        {"source": "native action loop", "round_ceiling": None, "timeout": None, "output_cap": None, "scope": "configured workspace, isolated Python execution, real return required"},
        {"source": "completion integrity", "policy": "explicit workspace imperatives remain pending without an actual native return; does not grant action authority; bootstrap lexical intent detection is not learned RWKV policy"},
        {"source": "RWKV", "chunk_tokens": 128, "meaning": "all tokens consumed in compute batches", "gradient_training": False},
        {"source": "foreground API tools/orchestrator", "enabled": False, "reason": "native private-intention and SELF authorization route owns actions"},
        {"source": "Ollama", "retry_attempts": 4, "think": False, "num_predict": "not set", "failure": "explicit error, no scored fallback"},
        {"source": "context", "policy": "whole current inputs mandatory; optional memory-role space shares actual physical boundary; no cross-module score; fallible summary only on durable dialogue pressure"},
        {"source": "recollection roles", "policy": "canonical record type owns merged nomination section; older assistant prose requires explicit past-statement request, without removing actual dialogue history"},
        {"source": "retrieval/curator/dashboard", "status": "inherited internal selection and retention policies remain; this run cannot establish exhaustive recall, sleep competence or unrestricted long-session readiness"},
    ],
    "parity": {"normal_entrypoint": True, "all_declared_components": "verify against runtime manifest before submitting cases", "learned_rwkv_intent_decoder": False, "intent_bootstrap": "Granite private intention, explicitly configured; native authorization and returns", "full_readiness_result": None},
    "test_overrides": ["isolated copied state and workspace", "external messaging credentials absent", "offscreen real wizard clicks", "offline dependency setup"],
    "observer": {"role": "passive return observation and real UI interaction; no input/answer substitution", "files": {str(p.relative_to(run)): sha(p) for p in (run / "observer").iterdir()}},
}
for path in (ROOT / "wizard").rglob("*.py"):
    manifest["helix"]["files"][str(path.relative_to(ROOT))] = sha(path)
for name in ("Helix Setup Wizard.sh", "requirements-mindscape.txt", "install.sh"):
    manifest["helix"]["files"][name] = sha(ROOT / name)
write_json(run / "composition-manifest.json", manifest)
args = ["bwrap", "--die-with-parent", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc", "--bind", str(run), str(run)]
for folder in ("data", "config", "logs", "journals"):
    args += ["--bind", str(run / folder), str(ROOT / folder)]
args += ["--bind", str(run / "credentials"), str(Path.home() / ".config/helix"), "--chdir", str(ROOT), "--clearenv"]
environment = {"PATH": f"{ROOT}/venv/bin:/usr/bin:/bin", "HOME": str(Path.home()), "LANG": "C.UTF-8", "TZ": "America/New_York",
               "HF_HUB_OFFLINE": "1", "PYTHONUNBUFFERED": "1", "TMPDIR": str(run / "tmp"), "XDG_CACHE_HOME": str(run / "cache"),
               "NUMBA_CACHE_DIR": str(run / "cache/numba"), "PYTHONPATH": f"{run}/observer:{ROOT}",
               "HELIX_REVIEW_TRACE": str(run / "trace.jsonl"), "HELIX_TRIAL_RUN": str(run), "HELIX_DISABLE_TELEGRAM": "1", "PIP_NO_INDEX": "1",
               "DISPLAY": ":0", "QT_QPA_PLATFORM": "offscreen", "QTWEBENGINE_CHROMIUM_FLAGS": "--disable-gpu", "QTWEBENGINE_DISABLE_SANDBOX": "1"}
for key, value in environment.items():
    args += ["--setenv", key, value]
args += ["bash", str(ROOT / "Helix Setup Wizard.sh"), "--wizard"]
(run / "run.sh").write_text("#!/bin/sh\nexec " + shlex.join(args) + "\n")
Path("/tmp/helix-native-cycle-current").write_text(str(run))
shutil.copy2(run / "composition-manifest.json", audit / "composition-manifest.json")
print(json.dumps({"run": str(run), "canonical_files": len(canonical), "input_files": manifest["input_files"]}, indent=2))
