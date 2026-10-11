# Boundary audit in progress

This inventory is implementation evidence, not a product score or an approval of
the inherited settings. The active setup trial diagnoses a specific context and
action handoff. It cannot establish exhaustive recall or full launch readiness.
The configuration manifest records this limitation before execution.

| Boundary | Current source and behavior | Status |
| --- | --- | --- |
| Foreground context | `core/mindscape.py`, `llm/ollama_tokens.py`: selected 8192-token context; installed tokenizer counts complete system, dialogue and packet; length/pruning fails explicitly | Physical boundary; exact per-request receipts required |
| Private and visible generation | `llm/providers/ollama_provider.py`: no `num_predict`; thinking disabled; one private intention or message per generation | No shared hidden-thinking allowance |
| Action continuation | `core/mindscape.py`: actual return wakes next pulse; no action-round ceiling | Multi-step completion still requires outcome verification |
| RWKV input batching | 128 tokens per compute batch; all input tokens consumed | Batching, not truncation |
| mRAG selection | `core/preconscious.py`: local 20 items, spatial K12, spatial and associative reserves | Inherited selection policy; no documented physical requirement yet |
| Unified retrieval | `core/unified_retrieval.py`: default 12 items, typed reserve 3, episode complement 2, thought limit 2; effective budget min(15 times average item size, 15 percent of context) | Can exclude evidence before Loom admission; unresolved |
| Semantic candidates | `memory/mrag/semantic_lane.py`: profile-dependent head counts, derived query limits, 30–60 candidate pool at 10 percent of corpus, per-head K | Inherited search policy; whole-sentence coverage does not remove these limits |
| Query slicing | `core/preconscious.py`: several spatial queries use the first 500 characters; combined tool events use 6000 characters | Undeclared semantic loss risk; needs a native-path fix and receipts |
| Dialogue compression | `core/pulse_loop.py` selects a 50 percent trigger and 80 percent emergency (the compressor constructor alone defaults to 65 percent), two protected head messages, 20 percent summary target and tail-retention rules | Verified in setup-run initialization; complete input now reaches summarizer and failure preserves originals; inherited thresholds still require review |
| Provider retry | `llm/providers/ollama_provider.py`: `HELIX_OLLAMA_MAX_ATTEMPTS`, default 4 | Configurable but arbitrary default remains; no readiness approval |
| Static belief selection | `core/pulse_loop.py`: premise/proposition item and estimated-word budgets before exact provider accounting | Can discard belief context independently of the physical boundary; unresolved |
| Native graph traversal, lane nomination, curator and dashboard retention | Further path-specific inventory required | Not yet audited; no unrestricted operation claim |

Do not interpret a successful bounded diagnosis as validation of these policies.
Changing them requires tracing the active path and preserving whole evidence and
explicit physical-boundary failures, rather than copying larger arbitrary values.
