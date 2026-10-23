# Ribs Top Radius / late Ulna update

- Branch: `codex/ribs-ulna-latency`; baseline `8dba5e0` on `main`.
- Status: queue priority inversion reproduced; desktop overhead comparisons in progress,
  2026-10-23. Direct work, background only.
- Request: set Ribs Top Radius to 3 in the migrated 96-muscle assembly and use the
  profiler to distinguish necessary dependency ordering from unnecessary delay.
- Source: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
- Preserve the source and unrelated root `__init__.py`. No production behavior changes
  are part of this investigation. Diagnostic outputs belong under `build/ribs-ulna-latency/`.

Trace the actual shortcut, Ulna's declared prerequisites, queue eligibility, worker
execution, publication and desktop presentation. Compare against other bones and tissue
jobs; verify any proposed cause with a discriminating experiment. The prior attachment
fix kept invalidated Ulna jobs alive, but did not establish optimal update ordering.

Official reference: [Perfetto scheduling latency](https://perfetto.dev/docs/data-sources/cpu-scheduling)
distinguishes waiting for eligibility from waiting to execute. Use the application's
existing task/native profiler; supplement missing dependency-wait evidence in diagnostic
tooling without claiming headless timings establish physical viewport latency.

## Observed cause

The saved `Ribs Top Radius` driver is `95809822-bcd3-4dfe-8985-6980772eb699`;
the baseline value is 0.9829999208450317. The experiment sets it to exactly 3.
Ulna (`SCP_15`) has a real dependency: formula
`fa9fe611-0e21-4b76-893a-c0c5fe096363` reads Radius world X scale and drives Ulna
local X scale. It must resolve after Radius's updated pose.

Two monitored headless runs demonstrate additional unnecessary waiting:

| Milestone, seconds after driver command | Run A | Run B |
| --- | ---: | ---: |
| Radius pose publication | 3.655 | 3.630 |
| Ulna formula publication | 3.667 | 3.642 |
| Ulna observed ready, no active blockers | 3.674 | 3.648 |
| Ulna starts | 5.236 | 5.197 |
| Ulna publication completes | 5.276 | 5.242 |

Ulna's native job execution takes 0.45–0.57 ms; its publication (including downstream
registration) takes about 36 ms. The **1.55–1.56 s runnable queue wait** is neither
geometry computation nor required dependency ordering. During that wait, 76 Fiber
jobs, about 19–20 jobs in each of four tissue phases, and 23 construction jobs dispatch.
An initial run without queue observation reproduces the same ordering and comparable
gap, so the diagnostic observer did not create it.

The desktop observation confirms the priority mismatch: Ulna's replacement pose job
has `priority=10, interactive=False` (effective rank 10); all the intervening jobs have
`priority=10, interactive=True` (rank 110). `TaskCoordinator.queued()` sorts by this rank
and then creation time; `_dispatch()` has two workers and stops admission when full.
`construction_tasks.propagate_result()` requests follow-up SCP poses with the default
noninteractive flag. `path_tasks.schedule()` and construction/tissue scheduling mark
Live consumer work interactive. The queue does not inherit urgency through prerequisite
relationships. This is a shared scheduling-policy problem, not an Ulna-specific kernel.

## Discriminating experiment

The tool-only `--priority-probe` sorts ready candidates so pose/formula work is considered
first. All production dependency, cancellation, reservation and publication checks remain
in place; no native algorithm changes. This is a diagnostic intervention, **not the
proposed production implementation**.

In two runs, Radius publishes at 1.46–1.47 s and Ulna at 1.52–1.53 s. Ulna starts about
4–5 ms after its required formula finishes; no sustained unblocked waiting is observed.
All 625 object geometry/path/pose fingerprints match the normal-priority run exactly.
The whole edit settles in about 6.4 s versus about 7.1 s, but these are serial diagnostic
runs under uncontrolled desktop load, not a formal throughput benchmark.

## Profiler limitation discovered

The full-QML desktop recording generates about 5.7 million events in 140 s. Its bounded
ring evicts the initial command and most events; the report is explicitly incomplete.
Collector drain inclusive time is about 98 s, decode inclusive time about 44 s, and event
recording about 45 s. These overlap and must **not** be summed or subtracted as exact
overhead. Its queue observations verify the same ordering, but its wall times are not
normal application performance. Compare full desktop with the Qt collector absent and
recording off before making a desktop latency claim.

Local outputs: `build/ribs-ulna-latency/`; reproducible tools are
`tools/probe_ribs_ulna_latency.py`, `tools/probe_ribs_ulna_desktop.py`,
`tools/ribs_ulna_queue_probe.py`, and `tools/summarize_ribs_ulna_latency.py`.
No production source or source project has been changed.
