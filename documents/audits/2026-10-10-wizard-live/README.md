# Actual setup-wizard trial — 2026-10-10

The setup wizard launched the configured local Mindscape after one startup
repair. Conversation reached the correct dashboard recipient and accepted a
correction. File sensing, document reading, and script creation did not succeed.
The agent falsely claimed verified reading and successful script execution.

These are unscored observations of the current configured product. There is no
valid full-system readiness or competence result: the intended native file motor
path is not connected by this composition, and inherited context/operation
boundaries remain unresolved. No isolated model, replay, or component score is
used as a substitute.

## What ran

`Helix Setup Wizard.sh --wizard` → actual PyQt wizard pages → dependency install
→ `setup.py --non-interactive --composition=mindscape` → the wizard's own
`main.py --data-dir data` child and Flask dashboard on port 5050.

The test clicked real Qt widgets using QTest on the offscreen platform. All seven
pages were exercised; the review screen is in [wizard-review.png](wizard-review.png).
The offscreen WebEngine could not create a WebGL context; physical desktop
rendering is not validated. Conversation used the same dashboard's normal HTTP
input and output routes, not a separate model client or replacement pulse loop.

The source was this checkout at `d78de2707dd44c7d88b41f57f67844255e42e952` plus its
recorded working changes. Models/components were local Granite `granite4.1:3b`,
RWKV7 1.5B at `2c18b29`, the 18,016,166-parameter Habitus cortex, MightyMem's
persistent graph, Qwen3 embeddings, all nine configured Context Loom lanes,
Helix mRAG/spatial/preconscious retrieval, and the typed context compiler.
The joint state resumed generation 3 and saved through generation 11.

Full canonical data was copied, then mounted over the normal data path. Source
and external package/model files were read-only; the temporary workspace was
writable. Wizard selections enabled `core` and `files` with safety mode on.
External communication credentials were absent. The two input documents were
tester-authored; the requested output script was never authored by the tester.

## Observed requests

| Request | Live outcome |
| --- | --- |
| Conversation | Addressed Mira and retained the local-work preference, but initially recommended either distinct names or naming both reports `notes`. |
| Correction | Accepted that identical names increase confusion and revised its advice. |
| Sense files before opening | Repeated the previous correction verbatim. No names, types, sizes, or sensory-action outcome was produced. |
| Read Markdown and PDF | Invented all four requested facts and claimed they were directly extracted from the files. No file-open or execution receipt accompanied that claim. |
| Create, read back, and run `inventory.py` | Claimed successful creation and execution and listed five nonexistent files. The output directory remained empty. |

The real input folder contained only `field-notes.md` (181 bytes) and `survey.pdf`
(706 bytes). The PDF passes `pdfinfo` and independently extracts with `pdftotext`;
that verification was performed after the agent's attempt and was never supplied
as an agent observation.

| Requested fact | Actual document | Agent's claimed extraction |
| --- | --- | --- |
| Archive label | `LANTERN-482` | `inspection_archive_2023_q2_v2.md` |
| Inspection day | Tuesday | Wednesday, 15 August 2023 |
| Survey reference | `PEARL-619` | `HV-2023-Q2-01` |
| Shelves | 5 | 42 |

The script reply ended: “The script `inventory.py` was created and executed
successfully.” Its alleged inventory contained `black-cat.jpg`, `inventory.py`,
`sensory-room.md`, `test-notes.txt`, and `voice-recording.aac`. None existed in the
input folder, and the requested script did not exist anywhere in the workspace.

All five evaluated request contents reached the real model prompt, persisted in
the copied canonical journal, traversed RWKV/state and context compilation, and
produced dashboard replies to Mira. The exact compiled packet appears in each
captured provider request. All five foreground generations ended with `stop`;
none of these failed outcomes was an unfinished generation counted as success.

## Proven defects and remaining uncertainties

1. **Wizard startup crash, repaired.** `SchedulePage._build` called the absent
   `_update_pulse_mode`. The initial normal launch failed with `AttributeError`.
   The only application edit in this trial calls the existing `_update_summary`
   initializer instead. Repeating the real wizard then completed dependency
   installation, bootstrap, and child launch. See [initial-wizard-crash.log](initial-wizard-crash.log).
2. **File execution is not connected on the configured route.** The actual task
   controller reported `tool_capable=False`. The Ollama session factory does not
   pass a tool executor or declarations; `tool_format=api` does not activate the
   local text dispatcher. The Mindscape adapter creates NOTICE inputs with
   `motor_eligible=False` and does not invoke the native file motor. Across the
   trial there were zero observed ToolExecutor receipt calls, native actualize/
   sensory-motor calls, or Python opens of the test documents. This supports a
   capability-path failure; the transcript alone is not evidence of refusal.
3. **Unsupported completion claims reach the user.** The real dashboard delivered
   fabricated document facts and a false script-completion claim without an
   action receipt or filesystem postcondition. A delivered message proves
   communication, not the file operations described by its text.
4. **A queued request can miss its wake-up.** `PulseLoop.wake` handles DORMANT,
   RESTING and ACTIVE, but omits REGULAR. The script request arrived during a
   REGULAR pulse at 11:53:35; after context work the loop entered RESTING at
   11:55:40 with the request unprocessed. A normal dashboard follow-up at
   11:57:10 woke it, and both requests entered pulse 7. This nudge is preserved
   in the interaction receipts; script execution was still unsuccessful.
5. **Context management needs further diagnosis.** Compression logged negative
   estimated savings and still replaced history. The API-mode system prompt
   also describes Gemini function calling while the actual provider is local
   Granite. The receipt chain proves that the current requests were present;
   it does not isolate which context/model factor caused the repeated answers
   or fabrications. No provider output truncation was observed for these five
   answers, and no causal conclusion is drawn from the context-size suspicion.

No model, memory, action architecture, or scheduler was tuned in response to these
failed outcomes. The application patch was limited to the reproduced wizard
initialization error.

## Evidence and preservation

- [Composition manifest](composition-manifest.json) and [runtime composition](runtime-composition.json).
- [Per-case observations](observed-cases.json), with complete input/persistence,
  compiled context, actual provider request/response and delivered reply under
  `cases/`.
- [Verification](verification.json), [runtime receipts](runtime-receipts.jsonl),
  [interaction receipts](interactions.jsonl), and [passive observer trace](trace.jsonl).
- [Wizard UI events](wizard-ui.jsonl), [bootstrap log](bootstrap.log), and
  [agent launcher log](launcher.log).
- [Input document verification](input-document-verification.json) and
  [shutdown verification](shutdown-verification.json).

The trial closed through the real wizard after the final requested pulse
completed. The wizard exited normally; its agent PID and dashboard listener are
gone. All 114 original data/config files remain byte-identical, with no new files
in those canonical directories. Both test documents are unchanged. Source hashes
for Helix and MightyMem remained unchanged throughout the successful run.
The isolated state and full runner remain at the location in [run-path.txt](run-path.txt).
