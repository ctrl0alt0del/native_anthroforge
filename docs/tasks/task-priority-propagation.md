# Dependency priority propagation

- Task branch: `codex/task-priority-propagation`
- Integration branch: `main`
- Starting revision: `e7ba40b`
- Status: source verified; full gate and portable qualification in progress
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
FIFO, replacement/retry, Manual inputs and exclusive writers; 30 existing scheduler
regressions pass. Architecture/function-limit checks and five native CTests pass.
Full gate and portable qualification remain pending. Runtime source is `b7704f7`.
Canonical `dist/0.3.0/AnthroForge.dist` rebuilt successfully; full portable and actual
assembly checks are running. Logs are `build/task-priority-{gate,package,portable,packaged-assembly}.log`.

The first experiment propagated urgency but still used replacement creation time to
break ties; it retained the delay (2.07 s). The coherent correction also uses the
preserved logical queue age. The final actual-assembly headless run dispatches Ulna
within 13.6 ms of observed readiness, with one control-pose job intervening rather than
179 tissue/Fiber/construction jobs. Final geometry, attachment and desktop evidence is
recorded below. Raw artifacts include the rejected first attempt; it is not the delivered
implementation. Preserve unrelated root `__init__.py`.

## Next actions

1. Finish full development gate and canonical portable build/checks.
2. Exercise the actual Ribs edit in the packaged app and inspect hidden saved rendering.
3. Finalize documentation/source archive, then validated merge/push.

## Recovery inputs

Source: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
SHA256 `308c216c85d9458d83e163bc3ed2ab85338bccd3adeb496981ffe35ec8275dac`.
Baseline reports: ignored `build/ribs-ulna-latency/`. Reproduction tools are
`tools/probe_ribs_ulna_latency.py` and `tools/probe_ribs_ulna_desktop.py`;
do not use their diagnostic `--priority-probe` for production verification.
New evidence belongs under `build/task-priority-propagation/`.

## Qualification checkpoint

- Final source `b7704f7` and baseline `e7ba40b` both
  pass actual-assembly edit/undo/redo/save/reopen. All 625 geometry/path/pose hashes
  and all 914 attachment/reference/field-content hashes agree exactly; attachment
  hashes also agree before/after the edit. All 1,347 saved mesh/path/attachment resource
  buffer bundles also match, including tissue stages and material provenance. Native
  path data is hashed, not handle addresses. Original source remains unchanged.
- Indexed reverse lookup reduces measured priority policy cost from 1.77 s cumulative
  to 0.57 s in the headless workload. The scheduler skips ranking when workers are full.
- Final desktop comparison is below. Reports retain the entire interval (512 MiB) but
  reject 63 baseline/74 final oversized metadata events; they are explicitly incomplete.
  Task/model sidecars preserve the observations. Headless traces have no evictions or
  oversized losses. Full Qt/QML collection is excluded due to its previously measured
  perturbation; shared UI/task/native boundaries remain recorded.

| Trial | Radius accepted | Ulna accepted | Ulna ready queue wait | Ulna viewport model |
| --- | ---: | ---: | ---: | ---: |
| Baseline headless 1 | 3.577 s | 5.199 s | 1,565 ms | n/a |
| Baseline headless 2 | 5.219 s | 7.373 s | 2,083 ms | n/a |
| Final headless | 1.225 s | 1.312 s | 13.6 ms | n/a |
| Baseline desktop, application profiler | 45.715 s | 77.613 s | 31,228 ms | 77.919 s |
| Final desktop, application profiler | 3.379 s | 4.803 s | 670 ms | 5.174 s |
| Final desktop, recording off | 2.342 s | 3.683 s | 647 ms | 4.137 s |

Headless trials interleave baseline/candidate order on the same PC; all profiling trials
are serial with no concurrent build. Background user processes/load were not controlled,
and timings vary: this demonstrates removal of the queue inversion, not a universal
throughput factor. The remaining desktop gap includes two earlier control-pose jobs and
expensive UI refresh between ticks. Workers are not preempted. Ulna still correctly
depends on Radius's pose and its formula. This fix does not claim to repair UI refresh.
Accepted timings use command start; viewport-model and recording-off timings use the
probe start immediately before command/profiler activation. Offscreen evidence does not
establish physical display latency or human interactive acceptance.

Final headless policy cost: 469 calls, 565 ms cumulative, 6.13 ms maximum. Final desktop:
314 calls, 477 ms cumulative, 5.51 ms maximum. These instrumented costs include observer
effects and must not be subtracted as an exact overhead tax. All desktop final hashes
match baseline, and there are no job errors or QML warnings.

Raw final inputs: `baseline-2/`, `final-headless/`, `desktop-baseline/`, `desktop-final/`,
`desktop-unrecorded/` under the evidence directory above. `resource-equivalence.json`
records saved buffer equality. `tools/check_ribs_ulna_portable.py` qualifies the same
control plus history/reopen in the packaged executable.
