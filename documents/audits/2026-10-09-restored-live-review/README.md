# Restored Helix: setup and live local-path review

The restored application starts and runs local Granite through the real Helix pulse loop. The tested requests did not produce a delivered reply or the requested file. The requested non-tool movement and file-sensing pathway could not be activated in this composition. These are scoped operational observations, not a general performance or launch-readiness result.

## Composition and preservation

Source: commit `d78de2707dd44c7d88b41f57f67844255e42e952` plus the four pre-existing working-tree edits in README, SYSTEM_MANUAL, Curator and `documents/architecture_current.md`. The architecture document guided the route selection. Its standard persistent-session path was used; Office-first, the dual cloud/local loop and adjacent checkouts were not substituted.

The real `setup.py --non-interactive --local-mode --provider ollama --model granite4.1:3b` initialized a fresh profile. The real `main.py` then ran twice, including a restart over the actual state produced by the first process. A mount namespace kept the normal absolute code paths while redirecting data, config, journal, logs and credentials to isolated storage. Source files were read-only. The profile had no cloud keys or external messaging credentials. Camera/microphone devices were absent in the namespace, so sensory hardware was not evaluated.

The foreground and auxiliary model was local `granite4.1:3b`; semantic embeddings were local `qwen3-embedding:0.6b` at 1024 dimensions, with the separate MiniLM/8D spatial path. The recorded Ollama allocation used CPU, not VRAM. The existing venv was retained, including the installed MightyMem package; package presence does not establish integration.

Passive function-return instrumentation recorded actual ingestion, retrieval, compiled model input, complete provider responses, orchestration results and pulse completion. It did not replace methods, model responses, memory, tools or the entry point. The source hashes, configuration, limits, cases and hardware are in the [manifest](artifacts/manifest.json); both observer versions are retained with the artifacts and covered by the archive checksums. The transcription of the orchestrator request allowance is corrected to **one** in the [boundary correction](artifacts/evidence/boundary-correction.json). Inherited limits remain part of this unmodified runtime; this was not an uncapped benchmark.

## Observed outcomes

| Check | Observation | Evidence |
|---|---|---|
| Setup | Exit 0; 39 seed beliefs and 7 seed journal records | [Setup log](artifacts/evidence/setup.log) |
| Local inference and pulses | Six completed pulses across two processes; 15 actual Granite calls, all provider `stop` completions | [Pulse and model receipts](artifacts/evidence/pulse-case-map.json) |
| Terminal input and persistence | The fictional club message entered a real pulse and the canonical journal | [Complete trace](artifacts/evidence/trace.jsonl), [closed journal](artifacts/data/memory/cognitive_journal.jsonl) |
| Retrieval and context construction | Actual `UnifiedRetrieval` and `Preconscious.inject` outputs reached the foreground model requests | [Complete trace](artifacts/evidence/trace.jsonl) |
| Dashboard intake | Real HTTP POST returned 200; the normal poller consumed the message and it appeared in pulse 4 | [HTTP receipt](artifacts/evidence/dashboard-submit.json), [pulse map](artifacts/evidence/pulse-case-map.json) |
| Reply delivery | No reply invocation and no outbound dashboard entry during the completed runs; printed thoughts were not treated as delivery | [Final read-back](artifacts/evidence/final-verification.json) |
| Requested file write/read-back | `club-note.txt` was absent. The model requested only `desktop`; the planner asked for a missing target/action and returned no execution observations or receipts | [Case results](artifacts/evidence/case-results.json), [complete trace](artifacts/evidence/trace.jsonl) |
| Restart | A fresh process reopened 14 actual journal records; it subsequently stored two more thoughts. This is persistence evidence, not an answer-recall pass | [Closed journal](artifacts/data/memory/cognitive_journal.jsonl), [case results](artifacts/evidence/case-results.json) |
| Natural-intention execution with local Granite | Requested `HELIX_TASK_COGNITION=active`; runtime changed it to `observe`, recording `tool_capable=false` | [Activation receipt](artifacts/evidence/sensory-path-blocker.json) |
| Non-tool movement, touching and opening `.md` / `.pdf` | Blocked before the intended pathway could run. Valid input documents were prepared, but the sensory request was not submitted to a substitute tool pathway | [Sensory plan](artifacts/evidence/sensory-plan.json), [input provenance](artifacts/evidence/sensory-inputs.json) |

After the first requests, the application reached its own RESTING state with an empty event queue. No evaluator time or iteration cutoff was used to manufacture a failed action outcome. The main processes exited normally; the separately launched local review dashboard was stopped. The planned answer-recall and unknown-detail questions were not run after attention shifted to the requested sensory/motor activation check.

## What the architecture comparison establishes

The local setup selects `tool_format=orchestrated`. The actual main-model prompt still requires `{"tool_request": "..."}`; scoped tool passes perform execution. The model initially narrated plans without issuing that request. Later, its underspecified `desktop` request produced a clarification that also remained internal. The artifact/read-back failure is observed; it does not establish that every filesystem handler is broken.

The manual's natural-intention path corresponds to active task cognition. [The controller](../../../core/task_cognition/controller.py) currently allows only Gemini, Anthropic and Codex providers into active mode and explicitly downgrades Ollama to observe. This was verified during a real startup, not inferred solely from an inactive branch. Removing that check alone would not establish a sensory/motor implementation.

This restored Helix source does not instantiate a file sensory encoder, motor decoder or persistent environment-location controller. `core/somatic_engine.py` and `core/habitus_graph_manifold.py`, named in the current documentation, are absent from this restored checkout. Missing documented integration is a composition gap; it is not proof that disconnected legacy code is defective.

For lineage only, adjacent `/home/nemo/MightyMem/habitus_ai/sensory_motor_loop.py` contains `SensoryEncoder` and `MotorDecoder`. It is not imported by this launch path. Its `run_turn` uses a supplied `simulated_motor_intent` or defaults to PASS; its conscious-model stage is explicitly a placeholder. Its shown dispatcher implements READ/RUN, not environment movement. That source was inspected, not executed or substituted as product evidence. A valid non-tool test still needs the intended live producer of motor intentions, a location/action runtime and resulting sensory observations to be connected through the authoritative launch path.

One additional configuration discrepancy was measured: setup saved an 8,192-token local context, while `detect_available_provider` selected 64,000 and Ollama allocated 64,000. This is a real setting mismatch, but these runs do not prove it caused the failed requests.

## Verification and limits

All 407 captured source files remained byte-identical during execution, and all 122 protected lived-data/configuration/credential files remained unchanged. See [preservation verification](artifacts/evidence/final-verification.json) and [archive checksums](archive-sha256.json). No runtime code was patched for this review. The manual changed once before execution; that documentation-only change and the original manifest are retained in the artifact directory.

No valid product result exists for the requested non-tool sensory/motor system because the declared pathway could not be activated. Ordinary tool execution, a hand-selected motor vector, a standalone encoder or a plausible description of file contents would not resolve that blocker. Sleep consolidation, external channels, physical senses, larger-history recall and sustained unattended operation remain untested here.
