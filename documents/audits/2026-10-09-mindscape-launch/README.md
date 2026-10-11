# Local mindscape launcher: initialization and recovery audit

The configured launcher loads Helix, native mRAG/Context Office, MightyMem's
Habitus graph and cortex, RWKV, and Context Loom. First gestation, persistent
synchronization and exact joint-state restoration were exercised. **Complete
agent readiness is not established:** the observed acknowledgment remained a
thought, and non-tool filesystem movement/sensing remains unwired by this adapter.

These are unscored implementation and integration diagnostics. They do not
measure recall, learned motor competence, training quality or task performance.
Inherited context, retry, retrieval and orchestration boundaries remain open
for audit; the [diagnostic scope](diagnostic-scope.json) records that limitation.

## Exact composition

Application: this checkout, commit
`d78de2707dd44c7d88b41f57f67844255e42e952` plus the recorded working tree.
The entry point remained `main.py -> setup_helix -> standard PulseLoop`.
The new adapter is an explicit integration, not a claim to have recovered an
older saved unified agent. Previous source changes in SYSTEM_MANUAL, Curator
and the architecture documentation were preserved.

The native package source is `/home/nemo/MightyMem`. RWKV uses the pinned
`RWKV/RWKV7-G1j-1.5B-20260831@2c18b29ab7fbece25ff6112281eea0fa41fcb30f`
checkpoint, with 1,527,668,736 parameters and an 18,016,166-parameter Habitus
cortex. The native joint bridge runs on CPU. Foreground and auxiliary language
use local `granite4.1:3b`; semantic retrieval uses local
`qwen3-embedding:0.6b` at 1024 dimensions. The existing 8192-token foreground
configuration is now passed to the actual provider. Transformers was repaired
from 5.11 to 5.17 after reproducing the pinned checkpoint's cache-API error.

The [current product manifest](product-composition.json) records source hashes,
model identity, configuration, stores and all nine Loom lanes. The
[isolated runtime manifest](isolated-runtime-composition.json) records the
actual composition used for the dashboard-message diagnostic. Historical
projection does not replay memories as new human feedback. RWKV gradient
training is disabled; this adapter does not invoke the standalone native
learning or motor-emission loop.

## Observed checks

| Check | Observed result | Evidence |
|---|---|---|
| Existing-state startup | Normal `main.py --check-setup` exited 0; 120 canonical corpus records entered native Habitus and Loom | [Setup receipts](product-setup-receipts.jsonl), [startup log](product-setup.txt) |
| Persistent indexes | 120 records and projection markers, 1042 record/entity links, 51990 entity edges | [Read-back verification](verification.json) |
| Canonical preservation | All 13 original memory/belief files kept their exact SHA-256 values | [Before/after hashes](verification.json) |
| Restart | Exact native numeric tensors and saved weights; zero additional records or graph indexing on repeated sync | [Native restore receipts](product-joint-events.jsonl), [final startup log](product-final-resume.txt) |
| First gestation | Fresh native state was checkpointed before canonical synchronization | [Gestation receipt sequence](fresh-gestation-receipts.jsonl), [manifest](fresh-gestation-composition.json) |
| Real incoming pulse | Production dashboard queue consumed the message; pulse 2 processed 28 RWKV tokens, changed recurrent state, ran mRAG/Context Office and Loom, returned Granite text, and saved a joint checkpoint | [Full pulse receipts](isolated-runtime-receipts.jsonl), [runtime log](isolated-runtime.txt) |
| Delivery | No outbound dashboard entry; generated acknowledgment remained in the thought stream | [Dashboard read-back](isolated-dashboard-messages.json) |
| Graceful launcher stop | SIGTERM followed by normal exit 0 and “Helix offline”; the completed pulse checkpoint was already saved before this signal | [Signal receipt](shutdown-request.json), [runtime log](isolated-runtime.txt) |
| Corrupted checkpoint | Corrupting only the isolated pointer hash caused exit 1 with `joint checkpoint manifest hash mismatch`; no replacement gestation occurred | [Integrity result](corrupt-checkpoint-result.json), [failure log](corrupt-checkpoint.txt) |
| Recovery | Restored the original pointer, then successfully reopened the saved pulse state | [Post-corruption restore receipts](after-corruption-joint-events.jsonl), [restart log](after-corruption-resume.txt) |
| Implementation checks | 18 checks passed; selected Python compilation, wizard import, shell syntax, dependency consistency and diff whitespace checks passed | [Validation log](implementation-checks.txt) |

## Scope and reproduction

The isolated runs used a mount namespace with the same absolute application
entry point and source files. Only state/config/log/credential locations were
redirected. Cloud and external messaging credentials were absent. Source and
model files were read-only. No mock model or reconstructed agent loop supplied
the pulse outputs. The setup-only checks over the real lived corpus did not
start communication services or passive sensors.

`namespace-setup.sh`, `namespace-check.sh` and `namespace-run.sh` preserve the
actual launch commands. Their original state directory is
`/tmp/helix-mindscape-launch-20261009-6ul5rvk5`; model and neural checkpoint
binaries are not copied into this audit. Receipts retain timestamps because
pulse numbering restarts per process. Earlier entries in the isolated receipt
log describe preceding diagnostics; the final runtime manifest identifies the
last normal agent launch. The corruption check only modified its isolated
pointer and restored it in a `finally` block.

The complete inherited-limit audit, response delivery repair, non-tool PDF and
Markdown sensing/action pathway, continual-learning policy and sustained-run
validation remain open. No product benchmark score or unattended-readiness
claim follows from this report.
