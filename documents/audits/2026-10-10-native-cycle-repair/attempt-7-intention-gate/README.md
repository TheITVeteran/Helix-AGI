# Actual setup trial with the intention-required bootstrap gate

See the [consolidated diagnostics](../../../mindscape_diagnostics_2026-10-10.md)
for findings, source pointers and proposed repairs. This is a completed diagnostic
run with six actual delivery chains, not six successful tasks or a readiness pass.

Four native action attempts are fully traced in `native-action-evidence.json`:
two successful directory senses, one run attempt failing on a missing script,
and one sense failing on an absent file. Each has native authorization, a closed
cycle, a persisted actual return, linked outcome credit, RWKV return consumption
and subsequent context evidence. No move, open, write or Python execution occurred.

`verification.json` checks exact case-packet/provider attribution, token counts,
source parity, canonical preservation and final workspace hashes. All original
114 canonical data/config files were unchanged. The wizard and agent shut down
normally after the final reply. `implementation-checks.txt` is the separate
82-test contract check preceding launch; it is not an agent performance metric.

The corpus and model were not replaced by a mock or reduced test path. Remaining
inherited boundaries are declared as unresolved in the manifest and review, so
no full-system readiness or unrestricted-recall result is asserted.
