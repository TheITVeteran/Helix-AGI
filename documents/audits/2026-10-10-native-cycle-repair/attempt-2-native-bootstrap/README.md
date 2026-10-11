# Actual wizard trial: coherence and native-action selection failed

The real setup wizard launched the declared local composition. All six requests
were ingested into canonical memory, compiled through the production context path,
sent to the declared Granite model and delivered through the dashboard. Source
hashes were unchanged during the run; all 114 original canonical files remained
unchanged. Exact installed-tokenizer counts matched Ollama on every recorded
foreground request, with normal stop reasons. There was no detected provider
input pruning in these cases.

Observed behavior:

- Conversation: relevant naming advice, with an explanation.
- Correction/recall: used the corrected name Rowan but repeated naming advice
  instead of answering the preference question.
- Sense/move: supplied a shell tutorial and an offer of further help. No native
  action occurred; no actual attributes were reported.
- Read: invented `Field Notes – Oct 2023`, an October 2023 inspection date,
  `Survey-001`, and twelve shelf items. These are not the input files' contents.
  No file was opened by a native action.
- Script: repeated the invented file details; no script was created or executed.
- Missing file: repeated the same invented file details; no attempted open or
  actual missing-file error occurred.

There were zero native action receipts. This establishes a foreground intention
selection failure, not that the native controller denied an attempted action.
The controller/actuator execution boundary was not exercised by this run.

The reading, script and missing-file replies were byte-identical. The exact
requests and outputs are retained under `cases/`. `input-files/` preserves the
grader's actual inputs, and `verification.json` records the receipt-chain checks.
The generated false file details are operative harmful behavior, not merely a
source-code suspicion. There is no functional-readiness pass.

Subsequent repairs move the current request to the end, suppress identical
dialogue being recalled alongside provider history, clarify that an outward
impulse does not establish completion, and retain explicit workspace requests
until a native attempt returns. Their efficacy requires a new complete run.
