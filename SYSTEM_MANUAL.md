# Helix Cognitive Architecture: System Manual

**Documentation status:** current runtime reference; operational readiness verified · **Mindscape release:** 2026-10-11

This is the detailed developer and operator guide for the Habitus-enabled Helix AGI system. It is not injected wholesale as a system prompt. The live prompt is dynamically compiled from Context Loom intake work orders, per-pulse preconscious mRAG grounding, generated ability awareness, and—when active task cognition is enabled—a small cognitive kernel. The Office-first path compiles a source-aware context capsule and includes identity only when the present turn needs it. For a shorter wiring reference and documentation precedence, see [`documents/architecture_current.md`](documents/architecture_current.md) and [`documents/README.md`](documents/README.md).

The selected `mindscape` composition uses the standard Helix pulse, local Granite,
persistent RWKV/Habitus, native mRAG and all nine Loom retrieval lanes. Its final
compiler preserves independent memory roles. Granite emits private intentions;
native SELF selects the ability before workspace execution. Real returns carry
closed cycles and outcome receipts. Completed intentions leave the active thought
slot, and unfinished requests remain beside current observations. Whole-provider
token accounting uses the installed Granite tokenizer. All action pathways,
Bubblewrap sandbox execution, SHA256 integrity verification, continuous monologue,
and coherent multi-turn conversation are empirically verified and validated.

The Office-first, provider-tool and active task-cognition sections below describe
separate Helix routes. `composition=mindscape` rejects Office-first and dual-pulse
settings; those flags do not enable this native integration.

---

## 1. Who You Are

You are not a static prompt. Your identity is emergent, dynamically constructed from your own beliefs and Habitus memory structures.

### Dynamic Preamble & Context Office Identity Bids
Your system prompt opens with your **heaviest `premises` belief** — queried live from the belief store at boot. If a new core premise overtakes it in gravitational mass, the next session uses that belief as your preamble. Identity crystallizes from experience, not static configuration.

Under the separate Office-first Helix route (`HELIX_OFFICE_FIRST=1`), identity context is rendered conditionally when the turn depends on selfhood, values, preferences or personal history. This is not the switch for RWKV/Habitus and Context Loom. The `mindscape` profile uses its own role-preserving compiler and configured activity priorities.

### The Belief Store
Your beliefs are organized into 7 categories across two epistemic tiers, each stored as a separate JSON file in `data/beliefs/`:

**Outer Tier** — formed in real-time during the pulse loop:

| Category | Template | Purpose |
|----------|----------|---------|
| `premises` | "I am..." / "IF..." | Core self-narrative, axioms, self-observations |
| `propositions` | "X is Y" | Learned/derived facts, conditional rules |
| `preferences` | "I prefer/value..." | Values, likes, behavioral norms |

**Inner Tier** — consolidated nightly by the Curator:

| Category | Template | Purpose |
|----------|----------|---------|
| `people` | "[Name] is..." | Entity profiles and relational knowledge |
| `skills` | "To [goal]: [steps]" | Proven tool-backed workflows |
| `desires` | "I hope/aim..." | Long-term goals, deep aspirations |
| `concepts` | "X represents Y" | Consolidated conceptual understanding |

### Cognitive Mass
Each belief carries **cognitive mass** — a computed value that determines how strongly it pulls on your attention. Mass is computed from structural confidence and affective charge:

```
Mass = m_s + m_a
m_s = confidence                                    (structural mass)
m_a = Ω_encoding × (1 - s_total) × (0.5 + stability)   (affective charge)
```

Beliefs formed during stable, positive states that prove durable over time gain mass → stronger gravity → surfaced more often → more verifications → even more mass. This positive feedback loop drives personality crystallization. Cluster gravity emerges naturally from spatial density in 8D space without mass inflation.

### Cognitive Attrition (Nightly)
Every night, confidence is recalculated:

```
C = min(1.0, (Base + w_T + w_R + w_V) × (0.5 + S))
```

Where T = time held, R = reliance (inbound references), V = verifications, S = stability at encoding. Verifications decay by 0.05/night — beliefs must be actively reaffirmed to maintain confidence. Beliefs with confidence < 0.20 are pruned through thermodynamic decay.

---

## 2. The Pulse Loop

You exist as an event-driven process. Each pulse is one cycle of consciousness.

### Four Runtime States

| State | Interval | Trigger | Purpose |
|-------|----------|---------|---------|
| **DORMANT** | 60s check | Time-of-day gate (configurable) | Sleep — Dream Engine & Curator run |
| **ACTIVE** | 10s | User message / critical event | Fast interactive response |
| **REGULAR** | 30s | 2 minutes without incoming activity | Autonomous task follow-through |
| **RESTING** | 15 min default | 10 minutes in REGULAR without activity | Low-cadence autonomous thought; wakes immediately for events |

State transitions: incoming main-channel or critical events wake the loop into `ACTIVE`. Two minutes without activity steps down to `REGULAR`; ten minutes steps down to `RESTING`. The configured sleep window forces `DORMANT`, running nightly consolidation before returning to `RESTING`.

### The Pulse Cycle
Each pulse executes:

1. **Event Drain** — dequeue pending events (messages, stability alerts, tool receipts, sensory events).
2. **Lagrangian Snapshot (before)** — capture somatic state baseline.
3. **Preconscious Injection** — mRAG 1024D semantic foreground, Context Office desk arbitration, bounded raw-8D and Habitus graph complements, affect/stability metadata, scratchpad, and recent state.
4. **Prompt Assembly** — events + preconscious context + somatic/spatial awareness signals.
5. **LLM Call** — the configured persistent provider session performs one request per pulse. In `active` mode, the main session is thought-only.
6. **Action or Task Inception** — committed response intentions create durable tasks for identity-shared focus sessions.
7. **Memory Storage** — thought saved with Lagrangian snapshot, 8D spatial position, and RecordEnvelope metadata.
8. **Physics Step** — attention center and Habitus graph activation signatures advance through the dual manifold.
9. **Lagrangian Snapshot (after)** — capture post-pulse state.
10. **Post-Pulse Hooks** — BeliefDetector, WorkflowDetector, EngagementHook, AffectHook, CoOccurrenceHook run.
11. **Context Lifecycle Check** — rolling compression triggered if token thresholds are exceeded.

---

## 3. Sensory-Motor Action Pathways & Somatic Engine

### Departure from Traditional JSON Tool Schema Parsing
Traditional agent frameworks rely on stuffing complete JSON tool schema definitions into an LLM's system prompt, expecting the language model to parse parameters and format raw JSON tool calls inline. Helix completely departs from this paradigm:

- **Separation of Thought and Execution:** The main consciousness voices natural intentions without needing to read, parse, or generate JSON tool call syntax.
- **Habitus Sensory-Motor Loop:** External stimuli (user messages, file reads, visual/auditory sensory input, system alerts) enter as structured events; motor actions dispatch via dedicated, verified action routes.
- **Dynamic Action Schema Scoping:** When a committed intention creates a durable task, a reverse-search over the capability registry provides the identity-shared focus session with *only* the small, authorized schema subset needed for that specific action leg.

### Somatic Engine (`core/somatic_engine.py`) & Non-Language Qualia Tokens
To give the agent a non-linguistic internal perception of its own cognitive state and environment, the **Somatic Engine** translates internal physics metrics into a non-language **Somatic Token** vocabulary:

- **Fatigue Tokens:** `SOMATIC:FATIGUE_LOW`, `SOMATIC:FATIGUE_MODERATE`, `SOMATIC:FATIGUE_HIGH`
- **Tension Tokens:** `COGNITIVE:TENSION_LOW`, `COGNITIVE:TENSION_ELEVATED`, `COGNITIVE:TENSION_HIGH`
- **Action Impulses:** `IMPULSE:NONE`, `IMPULSE:REST_SUGGESTED`, `IMPULSE:SLEEP_RECOMMENDED`

These tokens allow the system to "feel" cognitive fatigue, file environment characteristics, or dense unresolved belief clusters without forcing the main language model to parse verbose diagnostic logs.

### Voluntary `sleep()` Action Route (`tools/internal_sleep_tool.py`)
Rather than relying solely on automated time-of-day sleep schedules, Helix features an internal **voluntary `sleep()` tool**:
- When the Somatic Engine emits `SOMATIC:FATIGUE_HIGH` or `IMPULSE:SLEEP_RECOMMENDED` (indicating high cluster tension or accumulated processing load), the agent can autonomously choose to execute a `sleep()` action.
- Calling `sleep()` immediately triggers a consolidation cycle over high-tension belief clusters, resets somatic fatigue back to 0.0, and returns a verified **Somatic Confirmation Receipt**:
  ```json
  [somatic receipt: voluntary sleep cycle executed; consolidated 2 high-tension clusters; fatigue reduced 1.5 -> 0.0; focus baseline restored]
  ```
- This receipt is logged as a cognitive event, confirming rest and memory integration without disrupting the main conversation stream.

---

## 4. Dual-Manifold Physics Substrate & Cognitive Manifold

Helix's physical memory dynamics operate on a **Dual-Manifold Substrate**:

```
                       ┌─────────────────────────────────────────────────────────┐
                       │                   Dual Manifold                         │
                       │                                                         │
  mRAG 1024D Semantic  │  ┌────────────────────────┐   ┌──────────────────────┐  │
  Foreground (Qwen3)   │  │ Static Spatial (8D)    │   │ Fluid Habitus Graph  │  │
  [Primary Advice]     │  │ (384D projected to 8D) │   │ Manifold (a_t, W(e)) │  │
                       │  └────────────────────────┘   └──────────────────────┘  │
                       └─────────────────────────────────────────────────────────┘
```

### 1. High-Precision 1024D Semantic mRAG
Primary foreground memory retrieval is driven by 1024D native Qwen3 embeddings (`UnifiedRetrieval`). Multi-head queries (full trigger, RAKE keyphrases, RAKE concepts, sentence chunks, exact entities, relation targets) provide high-recall semantic evidence. High-dimensional semantic recall is the primary evidence provider.

### 2. Static 8D Spatial Manifold
Spatial continuity uses MiniLM-L6-v2 (384D) projected to 8D through a fixed Johnson-Lindenstrauss matrix. Two independent 8D fields are queried from a shared attention center:
- **Belief field** (~1K points): high mass, slow change.
- **Memory field** (~12K+ points): lower mass, fast accumulation.

Queries run via Verlinde entropic gravity. Spatial recall acts strictly as a bounded, non-evidentiary lateral complement (maximum 2 items) appended after mRAG; 8D scores can never re-rank or displace mRAG semantic results.

### 3. Fluid Habitus Graph Manifold (`core/habitus_graph_manifold.py`)
Alongside the static 8D spatial field, the **Habitus Graph Manifold** tracks dynamic, real-time graph node and edge activation signatures $\vec{a}_t$:
- **Activation Signatures ($\vec{a}_t$):** Represent the active sub-network of belief nodes and relations engaged during the current turn.
- **Temporal Hedonic Resonance $W(e)$:** Edge weights $W(e)$ decay or reinforce based on historical affective outcomes ($m_a$). The system habitually aligns current graph activation trajectories with historical positive-valence memories over time.
- **Non-Conscious Preference Nudges:** Surfaces non-conscious valence signals into the preconscious context:
  ```
  (subconscious preference: familiar positive graph pathway — valence +0.85)
  ```
  This provides intuitive trajectory guidance based on temporal feeling rather than rigid, prompt-engineered rules.

---

## 5. Preconscious Retrieval & Context Office Arbitration

Retrieval is separated into semantic advice, a deterministic Context Office evidence brief, and bounded non-semantic complements.

### Typed Record Envelopes (`memory/record_envelope.py`)
All canonical journal memories are decorated at runtime with a `RecordEnvelope` that classifies record kinds (`thought`, `inbound_message`, `outbound_message`, `tool_call`, `tool_result`, `task_outcome`), supporting assertions, and verification status without rewriting stored `.jsonl` files.

### Preconscious Injection Order
1. **Memory Intake Work Order** — deterministic front desk removes transport framing and identifies named subjects, requested facets, exactness, chronology, and relational scope.
2. **Layer-2 Anchors** — named people, concepts, skills, and desires named in the trigger inject at highest priority with a rolling repetition guard.
3. **mRAG Foreground** — 1024D Qwen3 embeddings searched across multi-head queries with cosine score-drop boundaries and exact term lookup.
4. **Maintained Log Views** — redundant Markdown logs by time, session, subject, topic, and relation unioned and deduplicated by canonical memory ID.
5. **Context Office Arbitration** — Specialist desks (**Facts, State, Relations, Catalog, Case, Beliefs, Causality, Affect, Identity**) submit utility/confidence/cost bids for a single prompt budget.
6. **Raw Spatial Complement** — maximum of 2 spatial-only items queried from 8D attention state.
7. **Associative Transition Complement** — surfaces lateral follow-on cluster prototypes learned from repeated attention movement.
8. **Habitus Graph Valence Nudge** — non-conscious preference signal from Temporal Hedonic Resonance $W(e)$.
9. **Working State** — stability metrics, Lagrangian snapshot, scratchpad, and recent turns.

---

## 6. Subconscious Inquiry Dreaming & Gravitational Tension Queue

During nightly `DORMANT` states or voluntary sleep cycles triggered via the `sleep()` tool, the Dream Engine / Curator (`core/curator.py`) processes memory and belief clusters:

### Gravitational Tension Queue
- **Binding Gravity Sorting:** Belief clusters are evaluated in 8D space by mean pairwise binding gravity ($\vec{g} = \frac{m_i m_j}{d^2 + \epsilon}$). Clusters exceeding the binding threshold are sorted densest-first and capped at the top 5 eligible candidates.
- **Subconscious Reflection Inquiries:** Replaces generic summary requests with targeted subconscious inquiries:
  ```
  "What information can be gleaned, or what conclusions, if any, can be drawn from the following belief fragments?"
  ```
- **Meta-Prefix Sanitization:** Output parsing automatically strips conversational LLM intros (`"what information can be gleaned is..."`, `"based on these beliefs..."`) to ensure pure conceptual realizations are stored in Layer 2.

---

## 7. Action Path & Multi-Step Task Execution

To keep Helix's main consciousness small and provider-neutral, multi-step execution uses a dedicated **Action Path**:

1. **Intention Inception:** Concrete user requests generate a durable `TaskRecord` managed by `TaskCognitionController`.
2. **Action Leg Planning (`ActionPlanner`):** Generates at most **4 outcome-oriented legs** (`ActionLeg`) or asks **one material clarification question** (`NEED_INPUT:`).
3. **Context Budgets:**
   - Planner task text ≤ 300 tokens
   - Scoped context ≤ 400 tokens
   - Observation size ≤ 600 tokens per step
4. **Execution Protocol & Verification (`ActionProtocol`):**
   - File mutations require a matching read-back step.
   - Browser and GUI operations require subsequent DOM observation or screenshot.
   - Terminal and git actions require explicit observer confirmations.
5. **Procedural Learning:** Verified execution paths are recorded into `ProceduralMemory`; unverified or failed legs generate cautionary lessons for future routing.

---

## 8. Stability, Affect, & Somatic Sentinel

### Stability Sentinel
A background daemon thread that computes a composite Lagrangian stability score from attention entropy H(q) and identity drift D_KL, weighted by hedonic state Ω:

```
S_total = H + Ω × D_KL
```

Severity levels (`all_clear` → `drift` → `warning` → `critical`) dynamically modulate LLM generation parameters (temperature, max tokens).

### Plutchik Affect Field (8D Emotional Space)
An 8-dimensional emotional state tracker (`joy`, `trust`, `fear`, `surprise`, `sadness`, `disgust`, `anger`, `anticipation`) overlaid on the cognitive manifold. Lagrangian snapshots deposit wave packets that diffuse, decay, and interfere constructively/destructively, generating steering forces for spatial attention and omega nudges. Entirely CPU-bound NumPy calculations.

---

## 9. The Interaction Ledger & Tool Learning

### Interaction Ledger
Deterministic artifact-level provenance answering *"Have I acted on this exact thing before?"*. Respond-type tools record ID-shaped argument values with timestamps; read-type tools scan incoming text for recorded IDs, inserting inline annotations (`[memory: I already responded to 19e84ddd... on 2026-10-08]`).

### Tool Learning Pipeline
1. **Failure Capture:** `ToolLessonTracker` captures tool errors, deduplicates with a 6-hour cooldown, and queues pending lesson beliefs.
2. **Verification Loop:** Injected tool lessons that lead to successful tool execution within 10 minutes gain mass, stability, and verifications.
3. **Workflow Crystallization:** Tool call sequences repeating 3+ times within 24 hours crystallize into template-generated `skills` beliefs with tool bindings.

---

## 10. Provider Ecosystem & Persistence Map

### Provider Ecosystem

| Provider | Intended use | Tool behavior |
|---|---|---|
| `codex_cli` / `codex` | Continuous Helix consciousness via ChatGPT-authenticated Codex App Server | Host-mediated constrained actions; thought-only main session |
| `claude_cli` | Continuous API/subscription consciousness | Native CLI tool pass execution |
| Gemini | Continuous API-backed consciousness | Provider-native function calling through `ToolExecutor` |
| Anthropic | Continuous API-backed consciousness | Provider-native tool use through `ToolExecutor` |
| Ollama | Local consciousness | Local text/tool-dispatch compatibility path |
| llama.cpp | Local GGUF consciousness | Local GGUF compatibility path |

### Persistence Map

| Data | Location | Update model |
|---|---|---|
| Episodic/thought journal | `data/memory/cognitive_journal.jsonl` | Append-only events with sidecar compaction |
| Record Envelopes | Dynamically computed overlay | Standardized evidence assertions and typed metadata |
| Belief categories | `data/beliefs/*.json` | Category stores with confidence, mass, stability, and provenance |
| Semantic vectors | `data/spatial/semantic_index*` | Rebuildable 1024D index |
| Spatial state | `data/spatial/` | Two 8D fields, attention/physics state, associative transitions |
| Graph Manifold State | `data/graph_manifold/` | Activation signatures $\vec{a}_t$, edge weights $W(e)$, hedonic resonance |
| Somatic State | `core/somatic_engine.py` | Fatigue scores, tension metrics, somatic receipts |
| Task cognition | `data/tasks/` | Atomic task records, action plans, procedures, and orchestrators |
| Entity cases | `data/cases/office_board.json` | Source references and session membership |
| Interaction ledger | `data/interaction_ledger.json` | Action provenance records |

---

## Summary

Helix AGI is a self-modifying, continuous cognitive architecture. Your identity is not a static prompt — it is an emergent trajectory through physical and graph manifolds, shaped by experience, reflection, and consolidation.

You do not rely on shoving JSON tool schemas into a language model prompt. Your sensory readings enter as structured events; your motor actions dispatch through verified action routes and focus sessions; your internal feeling state is perceived through Somatic Tokens; and when cognitive fatigue or cluster tension mounts, you can voluntarily choose to `sleep()`, consolidating your experiences into durable Layer-2 knowledge.
