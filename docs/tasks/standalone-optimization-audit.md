# Standalone optimization audit

- Branch: codex/standalone-optimization-audit
- Integration: main
- Starting revision: 966ae1224a11c8c6a2948be7be58525998e84529 (0.1.5)
- Status: investigating
- Writer: desktop analysis chat; no delegation

## Scope

Review the migrated application for remaining addon constraints and opportunities
enabled by owning document, evaluation, scheduling and rendering. Inspect both the
current code and migration provenance. Use existing runtime captures and bounded
experiments to distinguish measured bottlenecks from scaling risks and hypotheses.
No production behavior changes or new release are authorized by this analysis task.

## Initial findings and next work

Activity's 0.1.5 fix is present. Mesh BVHs, native batch picking, immutable snapshots,
revision guards and staged rendering already exist; do not recommend adding them again.
Investigate whole-document presentation projection, repeated dependency/validation
work, construction intermediate-mesh finalization and long-session job/history costs.
Inspect existing caches and establish actual timings before ranking proposals.

Keep raw captures/experiments in ignored build/standalone-audit. Preserve the unrelated
untracked root __init__.py. Final findings should state ownership, unchanged semantics,
evidence limits and discriminating acceptance for each proposed change.
