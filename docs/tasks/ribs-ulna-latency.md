# Ribs Top Radius / late Ulna update

- Branch: `codex/ribs-ulna-latency`; baseline `8dba5e0` on `main`.
- Status: investigation in progress, 2026-10-23. Direct work, background only.
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
