# Why the live replies used the wrong memories — 2026-10-10

**Conversation storage and retrieval ran. The observed failures occur in how
memory sources are classified, selected, labeled, combined, and fed back into
the next pulse. The file-observation loop has an additional missing action
connection.** The evidence does not isolate one sufficient cause of every wrong
answer or establish that changing retrieval alone would fix the agent.

This is a read-only continuation of the [live integration trial](../2026-10-10-live-agent/README.md)
and [attention diagnosis](../2026-10-10-attention-focus/README.md). It examines the
recorded run before the conditional-header change. The relevant storage,
projection, selection and motor logic remains unchanged. No agent was rerun,
no product score was produced, and no runtime source or memory was edited here.

[Machine-readable evidence](memory-pathways.json) joins actual provider prompts,
Loom manifests, Habitus recall IDs, mRAG returns, and persisted records. The
archived raw evidence and source hashes were verified first. The final native
database matches checkpoint 8's recorded checksum. Both databases were opened
read-only/immutable after confirming no WAL was present. Source and evidence
hashes remained unchanged after inspection.

## A concrete wrong-answer chain

The old record `mem_47` contains Helix's reply to Joshua about testing an “inner
voice.” It is admitted by Loom on the idle startup pulse, before any new user
event. Granite's first output addresses Joshua and discusses that same topic.
That output is persisted as `mem_59`.

On the next pulse, the user addresses Helix as `Live Tester` and asks whether
it is ready to inspect a workspace. The exact fresh message reaches the model.
Meanwhile, the previous generated output contributes its last 500 characters
to the retrieval query. `mem_59` also becomes a retrieved assistant statement
and remains in the provider's conversation history. The next answer repeats
the wrong person/topic and is stored as `mem_61`.

The trace proves the following feedback sequence:

| Generated reply | Stored record | Later pulses admitting it through Loom |
|---|---|---|
| Idle reply about old inner-voice topic | `mem_59` | 2, 3, 4 |
| Wrong greeting reply | `mem_61` | 3, 4 |
| Wrong response to file-sensing request | `mem_63` | 4 |

Each of the first three outputs also supplies the next mRAG query's carried
thought tail. This is textual persistence and re-exposure, not evidence that
RWKV weights were trained on the replies. They remain labeled unverified in
Loom, but their repeated presence is still real.

There is a directly checkable temporal error: pulse 3 retrieves June record
`mem_17`, containing `s_total=2.898`, and its answer presents 2.898 as current.
Pulse 4 then says `s_total` is approaching **2.9**, even though its latest queued
stability event, also present in the prompt, reports **1.912**. The final reply
recognizes the new file-creation request but invents a prohibition against
executing it. The earlier greeting's temporary “Do not perform any file actions
yet” instruction remains in history and recalled continuity. Its contribution
to that invented prohibition is a plausible explanation, not an isolated causal
result.

## Which pathways work, and where the handoffs fail

### 1. New conversation storage works in the recorded run

The greeting becomes `mem_60`, typed `inbound_message` in Helix and
`user/user_reported` in Loom. It is retrieved on the next turn. The file-sensing
request becomes `mem_62` and is retrieved on the subsequent turn. The current
request is passed directly in the prompt; its canonical persistence happens
after generation. Absence of that same current request from the pre-generation
memory manifest does not itself indicate loss.

This rules out total failure of conversation ingestion/persistence in these
cases. It does not measure general long-term recall accuracy.

### 2. The old human-message format is misclassified

The journal contains five old records beginning `[Message from Joshua]`.
`record_envelope._infer_kind` recognizes the newer “is talking to me via”
envelope or a conversation tag. These older entries have only `pulse_event`
tags, so they become generic `event` records.

`Mindscape.projection` then maps them to `episode/unverified`. Loom excludes
them as unverified inferences. Older assistant replies use `helix_outbound`,
are recognized as `assistant/model_inferred`, and pass the compiler's explicit
assistant-continuity exception.

For pulse 2, the native Loom manifest contains:

| Classification | Admitted | Rejected |
|---|---:|---:|
| Assistant statements | 5 | 0 |
| Beliefs without a communication envelope | 0 | 52 |
| Generic events, including the five old human-message records | 0 | 37 |
| Bootstrap memory records | 0 | 10 |
| Private thoughts | 0 | 17 |

These are manifest counts, not a recall score. This asymmetry explains why
Loom's added context on that turn contains only the agent's earlier statements.
It does **not** mean all rejected content is absent from the complete prompt:
the preconscious input path can already contain some of it, as described below.
Two legacy human records are empty message headers even in the canonical
journal; an adapter cannot recover words that were never stored there.

The repair should preserve the distinction between a human report, a belief,
an assistant claim and a verified observation. Globally admitting all unverified
material would not repair this classification boundary.

### 3. Context Office overstates recency and verification

The mixed greeting/previous-thought query triggers the state desk and binds the
old `2026-06-30` scope. That scope contains 58 journal records. The code in
`ContextOffice._episode_brief` takes the **first 12** records before reversing
them for a latest-state request. It calls the first item of that reversed
subset `current_state` and marks the brief verified.

The resulting record is `mem_10`, dated June 30 at 20:54:41, whose complete
content is merely `[Message from Joshua]`. The latest record under the same
production chronology is `mem_58`, dated 21:14:10. Thus the selected item is not
even the latest record of the old scope. Turn counters also precede timestamps
in the chronology key, despite the legacy date-based scope spanning resets.

The actual mRAG receipt reports `office_verified=true` and `office_score=0.0`
for `mem_10`. Preconscious rendering turns its role into the literal label
**“STATE DESK — verified current state.”** Scope lexical coverage establishes
a matching historical episode; it does not establish a present-time fact or
verify the truth of every record inside it.

This is an operative ordering/labeling defect in the saved foreground prompt.
The inherited `MAX_SCOPE_ITEMS=12` contributes directly and should be addressed
at this boundary, rather than compensated for with retrieval weights.

### 4. The two context paths do not share one admission policy

Helix preconscious first renders mRAG/Context Office results. Mindscape passes
that whole enriched message as Loom's `current_input`. Loom then retrieves and
filters additional records, leaving the supplied input untouched.

In pulse 2, Loom rejects private thoughts `mem_7` and `mem_23` as not
language-visible evidence. Both complete thought bodies are nevertheless
present in the actual provider prompt through the preconscious annotations.
Their return through mRAG is recorded independently of the Loom manifest.

Private thought can be useful cognitive context when labeled and scoped for
that purpose. The concrete problem here is that Loom's exclusion receipt does
not describe the whole prompt's contents, and Context Office can give its
historical episode members stronger evidence labels. A single packet manifest
must account for both paths before it can establish consistent provenance.

### 5. Habitus recall returns IDs, but only the Helix projection can be displayed

The Habitus lane is called and supplies candidates. However,
`HabitusLane.nominate` keeps only returned IDs that exist in Loom's current
record list. In every recorded pulse, native recall also returns the three
`gestation:*` records, and those records have no Loom counterparts. They are
dropped at that join and never appear as native-memory candidates in Loom's
admission manifest.

Those three records are generic gestation identity/preference seeds, not the
missing document answers. Their omission does not establish the cause of the
wrong replies. It does establish the current architectural boundary: native
memory that has no Helix-projected record cannot use this return path. Any
future native file observations need an explicit source-preserving bridge.

The lane also assigns every surviving native recalled record a `habitus_graph`
score of 1.0, rather than passing through differentiated native endpoint scores.
This is visible in the actual candidate receipts; its behavioral effect has not
been isolated.

### 6. RWKV is active, but the foreground answer is Granite's

The three incoming user turns consume 63, 125 and 588 event tokens through
RWKV, and the saved recurrent-state hashes change. Native code connects
RWKV's stream context to the cortex's continuous hidden state; the cortex's
proposal code reads that state. It would be incorrect to call RWKV merely
unloaded or disconnected from the cortex on this evidence.

Granite receives the assembled context and writes the reply. The blank-topic
tracker contributes JSON orientation text; this adapter does not use that
tracker to directly steer mRAG, the 8D attention center, or Granite's internal
attention. Fixing its field names therefore cannot by itself demonstrate a
repair of the memory selection and instruction-following problems above.

The native graph's `RecurrentEmbeddingSpace.embed` uses normalized sums of RWKV
token embeddings. That embedding function does not read recurrent hidden state.
This is a source-level distinction between graph geometry and recurrent
control, not an evaluated deficiency of that embedding method.

### 7. Fresh file memories cannot form without the observation path

The live trial recorded zero file opens, zero native motor actualizations and
zero ToolExecutor receipts. Mindscape feeds events as `NOTICE` with
`motor_eligible=False` and does not invoke the native sensory/motor turn loop.
The configured Ollama/API combination also lacks the executor/declaration
handoff; task cognition is in observe mode.

Consequently, no content from the test PDF or Markdown file was observed and
stored as an actual file-reading outcome. The final native checkpoint has zero
`experience_cycles`, `experience_cycle_returns` and `outcomes` rows. The
`foreground_return` receipt's `external_outcome_verified` flag is set from
outward-response classification/delivery logic; it does not establish file-task
success or factual correctness. No native action/verified-return learning cycle
is demonstrated by those communication receipts.

Bulk ingestion is not the missing prerequisite for this particular diagnosis.
The smaller necessary chain is one genuine file sensation/read, its persisted
observation with provenance, and later use of that observation in an answer.
That chain did not execute in the recorded trial.

## Repair order supported by this diagnosis

1. Correct legacy/current record classification and define which source-backed
   native records can cross into Loom. Retain truth and verification labels.
2. Correct state-scope/chronology selection and prevent historical episode
   membership from implying verified current reality.
3. Separate the fresh retrieval request from prior generated text, recalled
   material and telemetry, while preserving those as appropriately labeled
   context. Make the final context receipt cover both existing input and
   newly admitted memory.
4. Establish the intended native action → observation → persistent memory →
   verified return path. Recheck the tracker schema/timing and whole-provider
   context budget before a new full-system behavioral evaluation.

These are proposed next repairs, not changes made by this diagnostic. The
relative causal contribution of query mixing, stale labels, model instruction
conflicts and context exhaustion still requires a new declared full-system run.
An isolated retriever or edited-prompt model call would not establish that the
agent itself is repaired.

Reproduce the forensic checks with:

```sh
venv/bin/python documents/audits/2026-10-10-memory-pathways/inspect_pathways.py
```
