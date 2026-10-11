# Context stability diagnosis — 2026-10-10

The recorded system repeatedly reintroduces its own old conversation into a new
turn, then compresses that mixture into a misleading account of what happened.
This is the strongest evidence-backed explanation for the observed repetition.
The audit establishes operative selection, serialization and orientation defects;
it does not isolate one sufficient cause inside Granite's attention mechanism.

This is **analysis of the actual wizard run**, not a new product test or a
performance score. Its entry point, models, state and receipt chain are in the
[operational recheck](../2026-10-10-operational-recheck/README.md). The intended
local composition remains Helix Pulse, mRAG, Context Loom and MightyMem/Habitus
with RWKV control and Granite language generation, as described in
[architecture_current](../../architecture_current.md).

The [reproducible analysis](analyze.py) verified 19 archived evidence files and
12 relevant source files against that run's manifests. It reproduced two pure
production transformations on those saved inputs: compressor serialization and
topic tracking. These are narrow implementation diagnostics, not replayed agent
competence tests. [Machine-readable evidence](evidence.json) includes the exact
compression input/output, per-case counts, source hashes and assertions. All 114
canonical files checked were unchanged during analysis. No runtime source was
edited and no inference or retrieval was rerun. The later PulseLoop wake repair
is disclosed as a source difference; that module is not imported here.

## 1. The wrong conversation starts before the fresh request is processed

Pulse 1 has no events and consumes zero new RWKV input tokens. Its context
nevertheless retrieves June assistant records, including:

- `mem_43`: grounding, a black cat on tiled flooring and coherent identity.
- `mem_47`: asking Joshua to explain the new inner voice.
- `mem_55`: the earlier statement “I am Gemini.” This is a recalled claim,
  not the configured model; the actual foreground calls are `granite4.1:3b`.

The pulse is classified as outward communication and instructed to address an
external recipient, although none is named. Granite produces an answer about
the cat and inner voice. The direct-channel fallback logs it as addressed to
`User` and returns `delivered=True`; there is no dashboard recipient receipt for
this startup output. It is nevertheless stored as an outbound response,
`mem_59`, and kept as an assistant turn in provider history.

On pulse 2 Mira's naming request is present, correctly routed, and passed to
Granite. The entire startup answer appears **twice** in that actual request:
once as an assistant history message and once as a newly recalled record. The
older source passages also recur. The response repeats their topic.

Autonomous idle thought is part of the intended design. The defect is the
combination of an unspecified outward target, storage/delivery semantics and
repeated re-exposure of that output, not the existence of idle pulses.

## 2. Retrieval keeps the old assistant narrative prominent

`core/mindscape_lanes.py:HabitusLane.nominate` assigns every eligible native
returned ID the same score, **1.0**. Native ordering and differentiated relevance
do not survive this adapter. Loom's tied-rank rule consequently gives each of
these records rank 1 for `habitus_graph`.

In this exact composition the lane contributes `1.10 × 1.0 / 1 = 1.10` to each
candidate. On the first conversational pulse:

| Old record | Semantic rank | Final utility | Contribution from the fixed Habitus vote |
| --- | ---: | ---: | ---: |
| `mem_43`, cat/grounding | 104 | 1.277658 | 86.09% |
| `mem_47`, inner voice | 83 | 1.105064 | 99.54% |
| `mem_30`, old stability discussion | 90 | 1.106942 | 99.37% |

These are inspected admission calculations, not attention measurements or
probabilities of truth. All three records actually enter the foreground packet.
The adapter's fixed vote dominates their other retrieval signals. The existing
assistant-continuity exception permits these records while many unverified
legacy records are rejected. This audit does not propose admitting everything
or changing a weight until a desired relevance contract is established.

**Architectural correction following the user's clarification:** the modules
serve different memory functions and should not compete directly. The larger
mismatch is the common candidate pool itself: Helix-supplied recollections and
native candidates share `_utility` and one sorted optional-admission pass.
Different section headings and different weights leave that competition intact.
The fixed Habitus vote demonstrates a consequence of this design; recalibrating
it alone would not restore the intended separation. Selection must remain
within each memory role, followed by composition that retains the role, source,
owner and evidence status. Focus-dependent space allocation at the real context
boundary is distinct from comparing cross-module relevance scores. This is the
required contract, not an implemented or behaviorally validated repair.

mRAG also does a second-hop expansion for the naming question. Its last query
adds `replied joshua thank you`, taken from a retrieved gravity basin, to the
fresh request. This is distinct from the old direct previous-thought query mix,
which the current code has removed. The recorded `last_stats` describe the last
hop, not every retrieval in the turn. Transport text such as `via dashboard`
also becomes a semantic head. These provide additional routes back to the old
conversation; their individual behavioral effects are not isolated.

## 3. The window preserves full memory presentations as chat turns

The first conversational pulse contains 203 characters of current message,
2,452 characters in the recalled-memory section and 4,516 characters of earlier
assistant statements. The fresh-message heading starts at character 7,732 of a
10,171-character packet. These are character counts, not model token counts.

The provider appends each entire packet as a `user` history message and sends
all previous packets again. Thus old retrieved material survives independently
of the next retrieval decision. Per-packet source deduplication does not remove
copies already in provider history. Focus weights affect candidate admission;
they do not replace these old snapshots or provide a persistent active-task
record (`task_id` is null in all four packets).

The headings now distinguish recalled and current material, but the provider
still presents a sequence of large memory snapshots interleaved with generated
answers. The initial failure occurred at **4,774 prompt tokens plus 101 output
tokens**, below the selected 8,192-token context, with normal `stop` termination.
Overflow is therefore not needed to explain that first failure. The evidence
does not establish that the preceding header/focus changes improved or worsened
behavior.

## 4. Compression deletes live requests and fabricates conversation history

This is a deterministically reproduced loss at a source handoff.
`ContextCompressor._serialize_for_summary` keeps only the first 3,000 and final
800 characters of a text longer than 4,000. The current-message section sits
inside the discarded span for both turns sent to the first compression pass.

| Turn being summarized | Current request survives its own serialized turn? | Survives elsewhere in the summary input? |
| --- | --- | --- |
| Suggest report names | No | Yes, as a recalled record in the following pulse |
| Feel files in the folder | No | No |

The production serializer's output exactly matches the saved auxiliary model
input. The loss is not inferred from a later bad answer. Metadata and recalled
passages survive while the current user section is removed. The naming request
is preserved incidentally by recall, without its original current-turn context.

The actual summary then claims that Mira supplied old grounding guidance and
that the agent's response suggested descriptive file names. The actual reply
did neither; it discussed the cat and asked about the inner voice. That summary
is subsequently given to Granite with a prefix asserting:

> You have already experienced everything described here in exactly this order.

The next request therefore contains a false account of successful assistance.
It also retains the complete idle startup exchange because the compressor
protects the first two history messages. The first bad reply precedes this
compression pass, so compression cannot be its initial cause. It is a confirmed
later source of lost instructions, wrong attribution and false continuity.

## 5. Topic orientation and total context accounting cannot correct the drift

Habitus paths use dictionary keys `target_node_id` and `path_node_ids`.
`TopicalTracker` reads `target_concept_id`/`target` and `path_nodes`/`nodes`, then
accepts an empty node ID. The adapter calls it before the current compile updates
the paths, giving it the previous pulse's result too. Reproducing that actual
sequence yields exactly the saved frames: a blank topic, zero drift and growing
familiarity across all four requests. This is a broken orientation signal, not
proof that the RWKV recurrent state is inactive. It also is not currently an
effective controller of Granite's topic selection.

Context accounting has a different scope mismatch. Loom budgets the current
packet with `RegexTokenCounter`; Ollama receives the system message, every
retained history message, the current packet and generation in its 8,192-token
window. There is no final tokenizer-based check of that complete request before
inference. Compression checks the previous response's usage, skips short
histories even when their messages are large, and uses character estimates.

| Request | Total submitted content characters | Reported prompt tokens |
| --- | ---: | ---: |
| Naming | 20,020 | 4,774 |
| Feel files | 31,913 | 7,525 |
| Read files | 45,716 | 6,585 |
| Write script, after compression | 38,878 | 7,586 |

The read request extends the preceding history, yet its reported prompt count
drops. This strongly suggests provider/server pruning at the context boundary.
The retained evidence does not identify exactly which spans the server removed;
normal `stop` is not proof that every submitted message was evaluated intact.
The first off-topic answer needs no such inference: it already fits the window.

## Repair order supported by this diagnosis

1. Establish one authoritative current conversation/task state and separate it
   from temporary retrieval presentations. Keep real dialogue and intended
   private continuity durable without repeatedly storing every memory snapshot
   as another user turn. Preserve provenance when a recollection becomes prose.
2. Preserve pending requests, speaker attribution, observations and actual
   outcomes through compression. Remove the demonstrated positional clipping;
   never assert that an unverified summary is exact lived history. Enforce the
   selected physical context boundary on the complete provider request.
3. Replace cross-module candidate competition with explicit memory-role
   contracts and role-preserving composition. Each function selects within its
   responsibility; focus governs placement and space at the actual context
   boundary. Preserve native relevance information within its proper role,
   repair the topic-path schema/timing, and represent an outward target
   explicitly. This does not require disabling RWKV or replacing the local
   architecture.
4. Re-run conversation and topic changes through the real launcher with a new
   composition manifest and per-turn receipts. Only that can establish whether
   the combined repairs restore coherent behavior. File actions additionally
   require the separately documented native actuator/observation connection.

No proposed repair in this document has been validated as a product improvement.
The diagnosis supports addressing these handoffs before increasing the context
window, switching models, adding more prompt reminders or training on the
confused conversations.

Reproduce the read-only evidence analysis from the repository root:

```sh
venv/bin/python documents/audits/2026-10-10-context-stability/analyze.py
```
