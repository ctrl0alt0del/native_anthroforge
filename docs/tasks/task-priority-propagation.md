# Dependency priority propagation

- Task branch: `codex/task-priority-propagation`
- Integration branch: `main`
- Starting revision: `e7ba40b`
- Status: in progress
- Active writer: desktop /root
- Last updated: 2026-10-23

## Outcome and acceptance

Correct the coordinator priority inversion measured in
[Ribs to Ulna investigation](ribs-ulna-latency.md). Repeat Ribs Top Radius = 3
on the 96-muscle assembly; Ulna must dispatch promptly after its Radius/formula
prerequisites, with identical accepted geometry, poses and attachment references.
No numerical or anatomical behavior changes; no per-object or per-kind whitelist.

## Ownership and approach

The coordinator owns causal scheduling intent and transient priority inheritance.
Retain request urgency/age across publication, replacement, coalescing and automatic
retry. Keep that intent separate from interactive execution/debounce hints and from
each destination's workspace priority. Recompute inherited rank from active dependency
contracts, withdrawing donations when consumers finish/cancel. Preserve reservations,
dispatch capture, stale-result rejection, checkpoints and transactions.

Reference: [Linux priority inheritance](https://www.kernel.org/doc/html/latest/locking/rt-mutex.html)
describes transitive temporary boosts and equal-priority FIFO. This application uses
declared job prerequisites, not OS locks; its fixture establishes effectiveness.

## Current state and verification

Coordinator policy and lifecycle integration implemented. Thirteen deterministic regressions
cover transitive donation, withdrawal, cycles, workspace scope, follow-ups, same-cause
FIFO, replacement/retry, Manual inputs and exclusive writers; 30 existing scheduler regressions pass.
Architecture/function-limit checks pass. Full qualification remains pending.

The first experiment propagated urgency but still used replacement creation time to
break ties; it retained the delay (2.07 s). The coherent correction also uses the
preserved logical queue age. Two actual-assembly runs now dispatch Ulna within 20–41 ms
of observed readiness, with one/two control-pose jobs intervening rather than 176 tissue,
Fiber and construction jobs. Final geometry and attachment comparisons, desktop evidence,
gate and packaging remain to be completed. Raw artifacts include this rejected attempt;
do not describe it as qualified. Preserve unrelated root `__init__.py`.

## Next actions

1. Implement shared rank policy and lifecycle integration; deterministic regression tests.
2. Run headless and offscreen desktop fixture comparisons with profiler evidence.
3. Development gate, canonical portable build/checks, documentation, validated merge/push.

## Recovery inputs

Source: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
SHA256 `308c216c85d9458d83e163bc3ed2ab85338bccd3adeb496981ffe35ec8275dac`.
Baseline reports: ignored `build/ribs-ulna-latency/`. Reproduction tools are
`tools/probe_ribs_ulna_latency.py` and `tools/probe_ribs_ulna_desktop.py`;
do not use their diagnostic `--priority-probe` for production verification.
New evidence belongs under `build/task-priority-propagation/`.

## Qualification checkpoint

- Final source (`bb78102` plus indexed priority edges) and baseline `e7ba40b` both
  pass actual-assembly edit/undo/redo/save/reopen. All 625 geometry/path/pose hashes
  and all 914 attachment/reference/field-content hashes agree exactly; attachment
  hashes also agree before/after the edit. Native path data is hashed, not handle addresses.
- Indexed reverse lookup reduces measured priority policy cost from 1.77 s cumulative
  to 0.57 s in the headless workload. The scheduler skips ranking when workers are full.
- Serial offscreen QML app-only profiling before this cost refinement: Radius displayed
  at 46.04 s baseline vs 2.49 s candidate; Ulna 77.92 s vs 3.50 s. All final shapes match.
  Reports retain the entire time interval (512 MiB) but reject 63/66 oversized metadata
  events; they are explicitly incomplete. Lifecycle/model sidecars preserve observations.
- Final-cost desktop verification, recording-off checks, full gate and package pending.
