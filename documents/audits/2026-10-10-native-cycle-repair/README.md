# Native cycle repair — paused for review

This is an implementation and actual-launch diagnosis. There is no full readiness
pass or aggregate product score. The original 114 canonical data/config files are
preserved; live trials use a byte copy through the real setup wizard and dashboard.

The composition remains this Helix checkout plus the configured MightyMem package,
local Granite 4.1 3B, native RWKV7 1.5B and its Habitus cortex, mRAG, Context Office,
8D physics and all nine Context Loom lanes. `composition-manifest.json` describes
the latest prepared trial; its runtime parity evidence belongs to that trial.

## Implemented boundaries

- Independent memory-role/producer admission uses each producer's own ordering.
  Focus changes accepted space allocation; score scale in one module cannot
  outrank unrelated memory roles. Whole contributions and provenance are retained.
- Installed Granite vocabulary/template accounting covers system, dialogue and
  pulse presentation. Old retrieved packets and undelivered private prose do not
  accumulate as conversation history. Incomplete/pruned inference fails explicitly.
- Summary serialization preserves complete messages. Summaries are fallible
  recollections, and failure preserves original dialogue on the native path.
- Current native traversal fields produce real topical IDs on the current pulse.
- The recurrent controller consumes its own foreground output and actual action
  returns. This does not enable gradient training or manufacture successful outcomes.
- Native workspace abilities preserve position; sense uses only attributes; open
  reads UTF-8 or extracts PDF text; writes require verified read-back; replacement
  and script execution require the observed file hash. Python execution uses an
  isolated filesystem/network with the selected workspace writable.
- The **explicit bootstrap** is Granite private intention -> native selected SELF
  affordance -> actuator -> native sensory return -> next Helix context. It is not
  a learned RWKV intent decoder. The standalone experimental motor-vector prototype
  is not substituted for this product route.

## Verification and current limitations

The consolidated review is [Mindscape diagnostics](../../mindscape_diagnostics_2026-10-10.md).
It separates current operative failures, confirmed source defects and proposed
repairs, with links to the latest complete six-request trial.

At the user's request, work is paused after this diagnostic handoff. Attempt 7
remains the latest live evidence. Subsequent v9 changes separate routing metadata
from preferences and clarify native ability effects; 83 focused checks pass, but
there has been no live retest. See [post-trial check evidence](post-trial-context-repair/README.md).
The task-completion gate and the remaining acceptance requirements are still open.

Focused diagnostics cover continuity, whole summary serialization, independent
role admission, current topic identity, metadata-only sensing, PDF extraction,
path confinement and write read-back. A separate real subprocess diagnostic
verified the confined Python interpreter. These do not measure agent competence.

The first real wizard trial initialized the full composition but stopped on its
first private pulse: the new continuation adapter passed a dictionary to native
SQLite metadata, whose contract is string-valued. No user conversation result
exists for that attempt. Its evidence is retained in
`attempt-1-metadata-failure/`; all 114 original canonical files were unchanged.
JSON serialization was repaired, with a regression against the actual native
`MindStore`, and a fresh wizard trial was started.

Attempt 2 completed all six delivery chains, but no native action was proposed.
The file reply invented details, then repeated those details for the script and
missing-file requests. Conversation correction also failed. Evidence is retained
in `attempt-2-native-bootstrap/`; it is a failure, not a readiness pass.

Attempt 3 again failed the conversational correction. Its workspace request
produced narrated JSON plus an invented result, not a private intention. The
completion gate withheld that prose; nothing ran. The next generation reached
the provider boundary and was explicitly withheld. Evidence is retained in
`attempt-3-context-action-handoff/`. Both runs preserve source/runtime parity and
all 114 original files. The canonical message envelopes were correct on disk but
the preconscious selection adapter dropped them, disabling dialogue deduplication.
That adapter now retains the envelopes. The foreground uses a private JSON wire
format distinguishing intentions from prose; this grants no execution authority.
Missing dispatch now returns explicit interface feedback on the next pulse.

Attempt 4 crossed the native action boundary: Granite issued intentions, native
SELF selected the sense ability, real filesystem attributes returned, and the
kernel persisted closed cycles and outcome-linked graph credit. Each observed
return reached RWKV and subsequent pulse context. The agent nevertheless repeated
the unchanged inbox sense and never moved or completed the request; shutdown
finished one final in-flight sense. Conversation correction used the requested
name but omitted the stated preference. `attempt-4-native-intentions/` preserves
these failures, including `native-action-evidence.json`. No reading/writing/run
result or readiness pass exists. Completed intentions had remained in the active
thought slot. They now retire into their receipts; the unfinished request has a
separate final task section. The sensory view keeps complete output/error and
arguments while control telemetry stays in the raw receipt.

Attempt 5 removed completed intentions from the active thought slot, but the
agent still issued repeated root sensing during a name/preference recall request.
Actual sensory returns were present in the next context; missing return delivery
was not the cause. `attempt-5-continuation/` preserves the failed run, source parity
and the unchanged 114 canonical files. No correction reply or later case result
exists. The next repair presents delivered dialogue in the foreground's current
JSON protocol, removes the concrete sense-action example from ability awareness,
and retains canonical memory roles through native candidate merging. Older model
statements now require an explicit request about past statements; actual provider
dialogue remains available.

Attempt 6 used that repair through the real wizard. Conversation stayed on topic
and used the corrected name, but still replaced the human's local-report preference
with the agent's own naming suggestion. The required original statement was in
the provider input. The file request produced repeated prose and invented names,
with zero native actions; the completion gate withheld the claims. The stopped
run is preserved in `attempt-6-canonical-roles/`. The next bootstrap repair makes
the grammar require an intention while the same existing observation gate is
active. Native authorization remains mandatory and no task output is prewritten.

Attempt 7 completed all six delivery chains through the real wizard composition.
Four native attempts have authorized calls, closed cycles, actual returns,
outcome credit, RWKV consumption and next-pulse context evidence. The actions
were two successful senses, a failed run on a missing script, and a failed sense
of a missing file. No move, open, write or script execution occurred. The agent
nevertheless claimed movement and opening. The missing-file reply was grounded;
preference recall and multi-step completion remained unreliable. The normal
shutdown, unchanged source hashes and 114 unchanged canonical files are recorded
in `attempt-7-intention-gate/`. No full readiness result exists.

Pending: successful conversation/action acceptance, restart continuity, document cursors
for observations larger than the selected context, supported native procedure
promotion, and the remaining inherited retrieval/retention boundary audit. PDF
opening extracts text; it does not provide page-image understanding or OCR.

The upstream MightyMem compiler changes are small default-preserving composition
hooks. Its pytest suite could not run because this Helix venv has no pytest;
the Helix-side narrow compiler diagnostics are separately recorded.

`before/` preserves the source versions at the start of this repair. Historical
audits retain their original findings and are not rewritten as successful tests.
