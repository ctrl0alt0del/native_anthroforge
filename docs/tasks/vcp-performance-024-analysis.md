# VCP performance analysis for 0.2.4

- Status: investigating; no production behavior changes authorized or made
- Branch: `codex/vcp-performance-024-analysis`
- Baseline: `ae9eaab52f8ebc96488a53a57cbe06255bb8aca3` (qualified opening optimizations)
- Scope: measure VCP editing, numerical kernels, Python/native transfers, dependency
  work and publication; recommend evidence-backed optimization order for 0.2.4.
- Preserve original projects, numerical contracts and the canonical 0.2.3 package.
  All GUI checks remain background/offscreen. Direct work; no subagents.

## Initial findings and method

The numerical tissue kernels already run in C++; Python owns phase orchestration,
settings packing and accepted-state publication. The 96-tissue migrated assembly has
94 Section Profile and two Control Point tissues, all with stacking disabled,
smoothing Off and relaxation None. Additional fixtures are required to assess those
paths. Do not infer whole-VCP performance from this assembly alone.

Use the existing runtime profiler for job/native/publication attribution, serial
recorder-off timings for real elapsed cost, and targeted Python diagnostics for
unattributed work. Deterministic profiling exaggerates Python relative to native
calls; use it to locate work, not to claim cross-language speedups.

Temporary probes and raw evidence belong in ignored `build/vcp-performance-024/`.
Consolidate conclusions in `docs/vcp_performance_024.md`, with measured findings,
hypotheses, existing capabilities, risks and acceptance experiments separated.

## References

- [Qt Quick performance guidance](https://doc.qt.io/qt-6.12/qtquick-performance.html)
- [Python profiling limitations](https://docs.python.org/3.12/library/profile.html)

## Next steps

1. Measure actual assembly edits and native tissue fixtures.
2. Inspect hot ownership boundaries and migrated kernels; test bounded alternatives.
3. Record prioritized findings and unmeasured limits; validate documentation and push.
