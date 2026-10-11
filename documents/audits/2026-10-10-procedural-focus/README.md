# Procedural awareness and activity-sensitive context

This change implements context selection and procedural evidence plumbing. It
does not demonstrate live-agent learning, recall accuracy, or file-action
competence. No model was run and no product score is reported here. The previous
[wizard trial](../2026-10-10-wizard-live/README.md) remains the latest live evidence;
it predates these changes and does not validate them.

## What changed

The normal `PulseLoop._build_pulse_message` constructs a mixed activity signal
from fresh input, or private continuation on an idle pulse. Conversation, action,
writing, inquiry and reflection can coexist. Recalled text and ability guidance
are excluded from that classifier's input and from subsequent retrieval queries.
The lexical rules are a configurable starting policy, not a trained RWKV focus
decoder. Native RWKV/Habitus control and output routing are unchanged.

The local `MindscapeContextCompiler` still runs the configured Loom lanes and
accepts independently retrieved mRAG contributions. Previously those Helix
contributions were fixed content before Loom's selection. Now recalled items
participate in admission as complete items, preserving the upstream producer's
rank preference. The compiler multiplies candidate utility by a section's mixed
activity priority. It never mixes raw mRAG similarity with native Loom scores.
This is an admission preference, not a reserved token quota or calibrated
probability. Lower-priority material can use space when other sections are empty.

Current events, private continuation, state, output direction and relevant
capability descriptions remain required. An over-budget required frame raises
`ContextBudgetExceeded`. Optional items that do not fit are excluded whole;
their complete text, sources and exclusion reason remain in the assembly receipt.
Source bodies are not shortened. Exact passage anchoring, ownership and evidence
labels are preserved for admitted recollections.

`mindscape.context_focus_profiles` can override positive section priorities,
for example `{"inquiry": {"recalled": 3.0, "procedures": 1.0}}`. Omitted
section priorities are neutral (1.0). The resolved profiles, activity weights,
standalone section counts, packet count, counter type, packet input boundary and
admission decisions are receipt-visible. The native compiler's token counter is
used; this is **not** proof that provider history, system prompt and output all
fit Granite's actual tokenizer/context allocation. That earlier boundary issue
remains open.

## Procedural knowledge

Ability awareness describes when a connected ability is useful and what it
returns. It is conditional on the current activity and the actual route: local
tag dispatcher, a successfully wrapped orchestrated session, supported native
provider, or active task focus. Mere registration does not confer an ability.
The current Ollama API-only Mindscape session is correctly described as lacking
the file/command dispatcher. It can converse through its existing message route.
Its system instruction no longer advertises the Gemini Function Calling API.
This change does not switch providers, enable tools or invent a file motor.

`ProceduralMemory` previously counted `verified=None` as verified and treated
legacy success counters as evidence. Recommendation now needs an explicitly
verified result, a matching sequence of runtime action receipts, and the existing
deterministic receipt verifier's positive result. No extra model self-validation
call is introduced. Outcome hashes make replay idempotent, and receipt snapshots
survive task updates and restarts. Legacy records remain readable but counters
alone do not recommend them. The old 500-record, five-example, 180-character and
default three-result clipping are removed from this store/recall path.

A longer verified sequence records links to shorter previously supported
sequences it contains, with their supporting episode IDs. These are structural
subprocedure relations. Matching tool names cannot prove a semantic prerequisite,
logical entailment, or general factual belief; no such claim is generated.
Supported procedures whose handlers are available can enter the pulse procedure
section and compete for context space. The local API-only profile cannot produce
file-action experience until its intended action path is connected.

## Implementation diagnostics

Command (repository venv):

```sh
venv/bin/python -m unittest tests.test_context_focus tests.test_pulse_context tests.test_task_cognition tests.test_mindscape_setup tests.test_action_protocol tests.test_mrag_semantic_lane -q
```

These tests use temporary stores and constructed inputs, including native Loom
compiler diagnostics. They are deliberately **component checks**, not a product
test, benchmark, recall score or evidence that the foreground behaves better.
All 97 checks passed; changed Python sources parsed and `git diff --check`
passed. The command, observed output and source hashes are in
[verification.json](verification.json).
They cover mixed focus, whole-item selection changes at an identical boundary,
unused-space borrowing, required overflow, optional exclusion receipts, passage
anchoring, unconnected/dormant abilities, normal pulse construction, unsupported
success flags, legacy counters, replay, restart and structural reuse provenance.

The working tree already contained the preceding Mindscape changes. This turn
preserves those edits and does not modify canonical memory/configuration,
checkpoints, provider selection or external packages. Source snapshots taken
before editing are in `/tmp/helix-focus-before-20261010`.

## Remaining architectural work

Semantic generalization into higher-order beliefs and evidence-backed revision
of those beliefs are not implemented by sequence links. RWKV activity decoding
has not been trained or validated. Non-tool movement, feeling a file, opening it
and completing a script remain unestablished. The provider-context boundary and
other inherited limiters still need the declared full-system audit. Any future
behavior claim must come through the real wizard-launched composition and its
actual action/observation/output path, with a verified manifest and case receipts.
