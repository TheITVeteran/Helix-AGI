# Context weaving implementation — 2026-10-10

This change implements the user's requested presentation and retrieval contract.
It is not a product evaluation, a recall score, or a claim of reliable document
reading. No live Granite/RWKV agent was launched for these checks. The normal
entry point remains `main.py -> setup_helix -> PulseLoop`, in this checkout;
MightyMem source and saved joint checkpoints were not edited.

## What now happens

1. The pulse samples fresh sensory events before preconscious retrieval. Current
   messages, observations and tool returns drive the searches. Telemetry and
   previous outward answers do not get appended to those queries. During idle
   continuation, the latest complete private foreground thought can be the seed.
2. mRAG keeps its own selection; raw spatial/associative additions keep their
   provenance. The local Loom compiler runs all configured native lanes against
   fresh query text, not the already enriched mRAG prompt. Native Loom still
   fuses ranks among its own lanes; this patch does not claim every lane now has
   a wholly separate admission algorithm.
3. Every nonempty sentence view participates in mRAG head generation under the
   Mindscape profile, even beyond the legacy four-sentence/sixteen-total-head
   limits. Derived heads retain their prior policy. Retrieval records the
   actual passage heads that nominated each selected source, across retrieval
   hops without mutating the shared canonical item with the new anchor fields.
4. Typed contributions distinguish received messages, earlier replies, recalled
   observations, beliefs, preferences, associations and private thoughts. The
   prior generic `Personal Opinions` prose is not used by this compositor:
   pronouns and salience cannot turn a person's quote into Helix's preference.
   Context Office selection labels cannot upgrade a thought to verified state.
5. If a returned passage matches one current source location, the recalled item
   is rendered as an italic `[recollection source-id; evidence-status]` aside
   after that passage. Ambiguous or absent anchors leave the memory in its own
   section. The original event remains intact, and the receipt records original
   offsets, passage text, source IDs, source/target hashes and the rendered note.
   A retrieval association is explicitly not a verified contradiction.
6. Subjective material without an exact passage can sit beside Helix's latest
   complete private thought. This text is the actual foreground output, not a
   generated surrogate written by the adapter. A retrieved private record stays
   private in storage and is admitted only as cognitive context. Outward replies
   remain separately labeled conversation. Preferences retain their recorded
   owners; a preference does not itself revoke or grant permission.
7. Loom's immutable packet stores the exact composed rendering and counts it
   during admission. `context_assembly` records the additional contributions,
   inline placements and duplicate exclusions and joins to `loom_packet_id`.
   A duplicate requires both the canonical ID and content hash to match. Fixed
   content exceeding the selected packet context causes an explicit error.

An illustrative format, not an observed agent thought or answer:

> A + B = D. *([recollection mem-example; reported by speaker] Joshua told me: “A + B = C.”)*

Helix must assess whether the recalled report is relevant, correct and current.
The assembly does not insert “therefore D is false,” fabricate a recollection,
or silently replace text in the document. Exact quotes can be long: natural
short paraphrases would require an additional grounded generation/verification
step, which this patch does not pretend to provide.

## Verification and limits

`verification.json` records the completed implementation checks and source hashes.
Tests use real source renderers/native Loom compilation with diagnostic stores;
some retrieval tests deliberately use synthetic vectors/stubs to inspect code
contracts. None is full-product evidence. Checks include exact passage binding,
ambiguous/missing anchors, quote ownership, false office-verification labels,
duplicate provenance, no query feedback from headers/memories, all sentence views,
native packet read-back, private-source admission, and explicit budget failure.

An initial broader runtime-integrity run passed 72 implementation assertions,
but its optional embedding calls could not reach Ollama in the restricted test
environment; those degraded startup paths are not embedding/product evidence.
A subsequent overly broad unified-retrieval invocation was interrupted after
the same dependency problem. Only the explicitly completed offline command in
`verification.json` is used for this change's verification result.

Known outstanding work from the previous live diagnosis remains: historical
human-message classification, state-desk chronology, native recall IDs without
Loom projections, topical tracker schema/timing, the native non-tool file motor
path, and verified action-return learning. The full-provider budget still
includes persistent history/system instructions outside Loom's packet counter.
Fresh native tool returns may also be present in provider history, as well as
the annotated current observation. This must be reconciled in that audit.

Sentence coverage is not guaranteed fact recall. Candidate admission limits,
repetition policies, entity/lexicon paths, relevance errors, and chunk boundaries
can still prevent a useful annotation. A document cursor, interrupted task
continuity, cross-chunk claims, current permissions, and actual outward behavior
require a manifest-verified live run before making any competence claim.

The next product experiment should read a real document through Helix, with a
previously ingested contradictory human report and an unrelated distractor,
place the claim beyond the fourth sentence, then interrupt and resume reading.
Receipts must join the real read/chunk, persisted source, passage nomination,
annotation, actual provider input and delivered conclusion. A privacy preference
plus explicit current permission is a separate case. No proxy score substitutes
for either experiment.
