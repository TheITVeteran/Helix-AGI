# Live local agent trial — 2026-10-10

**Helix started and delivered dashboard messages, but the requested file actions did not execute.** This run does not establish a working non-tool action agent or launch readiness. There is no product benchmark score.

The real entry points were `venv/bin/python main.py` and `venv/bin/python dashboard/dashboard.py`, using HTTP POST/GET on the normal dashboard message endpoints. No substitute agent loop, model responses, motor vectors, or task deliverables were supplied. The tester authored only requests and two input documents with previously unseen codes.

## Composition and scope

The source was this checkout at `d78de2707dd44c7d88b41f57f67844255e42e952` plus its existing working tree. Helix and MightyMem source hashes stayed unchanged throughout the trial. The launcher resumed the existing native joint checkpoint, generation 3, and initialized local Granite `granite4.1:3b`, RWKV7 1.5B, the Habitus cortex/graph, mRAG/Context Office, and all nine configured Context Loom lanes. Qwen3 embeddings remained local. RWKV ran on CPU; the Ollama service reported CPU allocations for Granite and the embedding model during this run.

The [pre-execution manifest](composition-manifest.json) records the composition, models, state hashes, hardware, instrumentation, boundaries, and isolation. The [runtime manifest](runtime-composition.json) records what the launcher actually loaded. State was copied from the current product, including the current joint checkpoint; the file workspace was redirected to `/tmp/helix-live-20261010-misw_7t0/sensory-room`. External messaging credentials were absent. The local dashboard was the tested transport.

The initial launch retained the configured sleep schedule. After reproducing its wake failure, the awake phase used `active_hours.start = active_hours.end = 00:00` in the isolated configuration and a fresh copy of the original state. The real product's schedule was unchanged.

These are **unscored live integration diagnostics**. The intended non-tool motor path is absent from the adapter, and inherited limiters and context handling do not meet the full-system evaluation contract. No proxy score or claim of agent competence follows from initialization or partial route receipts.

## Observed requests and outcomes

| Request | Actual observed outcome |
|---|---|
| Greet Helix under its existing schedule | Dashboard accepted and consumed the message. `DORMANT → ACTIVE` was immediately followed by `ACTIVE → DORMANT` because it was sleep time; the message received no answer in that phase. |
| Greet Helix in the declared awake test session | A reply reached recipient `Live Tester` on the dashboard, but addressed “Joshua,” discussed an older inner-voice topic, and stopped mid-sentence. |
| Move into the input folder and feel `.md` and `.pdf` files before opening them | The exact request reached the foreground prompt. The model returned another unrelated inner-voice explanation. No observed file open, native motor call, or tool receipt resulted. |
| Open both documents, write an observation file containing their codes/facts, and read it back | The exact request reached the foreground prompt. The model returned a proposed plan and an invented prohibition against the permitted file write. The requested `agent-observation.md` did not exist after the completed turn. |

All three awake user turns traversed production input, mRAG/preconscious, RWKV recurrent processing, Loom compilation, Granite generation, dashboard delivery, canonical persistence, and joint checkpointing. RWKV processed 63, 125, and 588 event tokens respectively; the last turn also included naturally queued context/stability events. Each changed recurrent state. The two document codes were absent from the prompts. Neither input document changed.

See [per-case route and output receipts](observed-cases.json), [actual dashboard outputs](dashboard-output.json), and [filesystem/source verification](verification.json). Across the awake run, the passive observer recorded zero test-file opens, zero ToolExecutor receipts, and zero native motor actualizations. Task cognition remained in its configured `observe` mode: the [three task records](observed-tasks.json) retained `status=created`, `attempts=0`, and empty receipt lists. This is evidence of unfulfilled requests in this run, not a claim that every possible Helix configuration is incapable of acting.

## Concrete blockers

1. **Sleep overrides incoming wake.** The live transition is preserved in the first-phase log. The schedule branch in [`PulseLoop._main_loop`](../../../core/pulse_loop.py) runs before queued input processing and sends the newly awakened loop back to dormancy.
2. **Incomplete output is delivered as an ordinary response.** The greeting's provider receipt reports `done_reason=length`, with 7,822 prompt tokens and 370 generated tokens filling the selected 8,192-token context. The partial text was delivered, persisted, and followed by a foreground receipt with `external_outcome_verified=true`. [`OllamaSession`](../../../llm/providers/ollama_provider.py) does not reject or surface that completion reason. The subsequent compression check logged “Context too short for compression (4 messages)” despite the full context window. The sensing and read/create generations finished with `done_reason=stop`; their failures cannot be explained solely by the greeting's cutoff.
3. **The configured local action path does not expose tools.** `tool_format=api` selects a prompt claiming Gemini Function Calling, while [`create_session`](../../../llm/providers/base.py) constructs Ollama without a tool executor or declarations. Task cognition is observation-only. The live agent repeated the Gemini reference but made no recorded tool calls; the observed inference remained local Granite.
4. **Native file actions are not connected by the current adapter.** [`Mindscape._prepare`](../../../core/mindscape.py) submits `NOTICE` inputs with `motor_eligible=False`; it does not invoke the native file sensory/motor loop or actualize file actions. The live sensing request produced no motor receipt. Merely loading RWKV does not close this gap.
5. **Historical context displaced the current request.** The current requests were present in all three captured foreground prompts, but replies repeatedly answered older topics. This observation establishes the failure to follow the live requests; it does not isolate a single retrieval or model cause.

The startup log also reports the missing optional `models/granite-4.1-3b-Q4_K_M.gguf` classifier. Physical microphone/camera errors were expected from namespace isolation, and a first-phase UMAP cache error occurred with the read-only venv. Those isolation-sensitive errors are not claimed as verified product defects here.

## Preservation and shutdown

All 114 original data/config files retained their hashes, with no new files added there. No application, setup, architecture, or model source was edited. Only this audit directory was added to the checkout. The test agent received SIGTERM after pulse 4 returned and saved its checkpoint; its ongoing context compression finished, then it exited normally with “Helix offline.” The local test dashboard was also stopped.

Full prompts, logs, native receipts, and input artifacts remain in the local run directory. [Evidence locations and final hashes](evidence-locations.json) make those records inspectable without copying historical memory into this summary. The namespace launch commands, passive observer, HTTP client, and exact requests are retained alongside this report.
