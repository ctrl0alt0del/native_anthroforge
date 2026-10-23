# 0.3 headless expression and driver profiling

This is synthetic Linux evidence from 2026-10-23, not desktop responsiveness or
release acceptance. Baseline: `b42a7f1`. Candidate: the direct property lookup
change committed as `57c93ec` and recorded in CH-052. Native expression and geometry
algorithms are unchanged.

## Workload and reproduction

From the repository root, after building the native library:

```bash
source tools/cloud/environment.sh
uv run --no-sync python tools/shortcuts_profile.py
```

The tool records revision, platform, Python version and every timing sample in
ignored `build/shortcuts-profile/measurements.json`. The existing runtime profiler
writes `driver-paths.afprofile.zip` beside it. Baseline copies in this workspace
are `baseline.json` and `driver-paths-baseline.afprofile.zip`; the first candidate
samples reported below are retained as `direct-lookup-first.json` and
`driver-paths-direct-lookup-first.afprofile.zip`. A repeat at committed `57c93ec`
also passed all numerical checks with no reported event losses; its outputs use
the default filenames. Raw artifacts are local only. Linux 6.18.55 x86-64,
glibc 2.41 and Python 3.12.12 were used.

- Compilation: 25 independent cold compilations and 25 cached lookups of the same
  expression and typed symbols; the cached lookup must return the same owned program.
- Evaluation: 25 batches each of 1, 256 and 4,096 frames. Python frame packing,
  prepacked native ABI evaluation and total adapter calls are timed separately.
  Borrowed buffers remain owned throughout. Results match NumPy and the full adapter.
- Application: one length driver controls radius variables on 12 closed Parametric
  circles, each with 256 samples, plus one dependent Body. Twelve sequential edits
  wait for accepted work. Both an unrecorded session and a separately recorded
  session run. Formula readiness, all sampled radii, closure and accepted Body
  output are checked. No Qt module may be imported.

## Observations

A public `property.get` of one radius variable previously enumerated and labelled
all earlier properties, including generated curve points. cProfile reported
1,170,890 calls and approximately 250 ms for that single 256-point-curve lookup.
The candidate follows the requested path, reusing the discovery metadata and
read-only policy. The same probe reports 585 calls and approximately 1 ms, including
first-use import work. The candidate profile is `property-get-after.pstats`.
This removes unrelated catalogue traversal; full catalogue discovery is unchanged.

| Twelve-edit application workload | Baseline median | Candidate median |
| --- | ---: | ---: |
| Unrecorded command through accepted completion | 787.49 ms | 142.74 ms |
| Separately recorded command through accepted completion | 822.47 ms | 152.45 ms |

These are single before/after runs on a shared worker while native style analysis
was active, not a counterbalanced benchmark or a general speedup guarantee. Both
runs retain four compiled programs totalling 10,049 bytes, within the existing
128-entry/8 MiB limits. Both recorded sessions contain 168 Parametric path calls
and 156 expression evaluation calls, with no reported event losses. Setup creates
and supersedes jobs; total task counts can differ by scheduling interleaving.

Candidate microbenchmark medians in milliseconds:

| Frames | Packing | Native evaluation | Complete adapter |
| ---: | ---: | ---: | ---: |
| 1 | 0.00142 | 0.00117 | 0.00889 |
| 256 | 0.14494 | 0.03021 | 0.18470 |
| 4,096 | 2.52051 | 0.50235 | 3.13566 |

Cold compilation was 0.00992 ms; cached lookup was 0.00078 ms. Timings are measured
in separate loops, so their medians are not additive. They identify boundary costs;
they do not establish that the expression kernel is the application's bottleneck.
Recorded prepare/execute/publish totals and native boundaries remain available in
the archive. Nested inclusive durations must not be summed as wall-clock time.

## Contracts and remaining evidence

The direct resolver preserves eligible roots, excluded state, dimensions, integer
types, component bounds, transform semantics, labels and Parametric read-only
reasons. It rejects noncanonical positional aliases that discovery never exposed.
Descriptor equivalence is tested across Bezier, Parametric, lattice, segment-chain
and named tissue-field construction, alongside existing public property/formula tests.
No cache or additional retained document state is introduced.

The recorder reports its existing observation and memory-accounting limitations;
it cannot measure GPU execution or physical input-to-display latency. Full-window
gestures, original-addon geometry/attachment parity, Windows Qt/native viewport
and portable executable checks are now recorded in the
[Windows review](windows_review.md). The point-reference policy has since been confirmed
and qualified; the canonical 0.3.0 package also passes the portable checks.

## Windows full-window recording (local review, 2026-10-23)

The maintained `tools/shortcuts_workflow_acceptance.py` runs the full production Main
window offscreen: a 48-point XYZ arc/helix, radius driver, dependent Body, mouse
scrubs, commit, Undo and cancellation. The report also verifies late model discovery.
`20261023-090341-ab4635bc.afprofile.zip` retained all 42,546 received events (19.0 MB),
with no ring eviction, loss or skipped model watches; `complete=true`. 3,800 boundary
events were filtered outside the recording interval. Raw reports remain ignored.

| Recorded boundary | Calls | Mean | Maximum |
| --- | ---: | ---: | ---: |
| Input dispatch | 13 | 8.55 ms | 19.72 ms |
| driver.value command | 6 | 0.635 ms | 0.775 ms |
| Controller refresh | 18 | 12.28 ms | 18.87 ms |
| Native expression evaluate | 6 | 23.1 µs | 25.2 µs |
| Native Parametric path | 6 | 83.7 µs | 87.8 µs |

Inclusive times overlap and are not additive. This is a small integration workload,
not a production-assembly responsiveness guarantee or before/after speedup claim.
Profiler-owned costs include 240.7 ms activation, 182.7 ms recording bookkeeping and
817.3 ms inclusive drain time; these overlap other collector work and cannot simply
be subtracted. Software offscreen window presentation does not measure physical
display latency or GPU execution. Native 3D rendering was inspected separately.

An earlier capture and the first portable probe reported incomplete model coverage:
the observer counted every QObject against its model-watch budget. CH-057 documents
the diagnosis and repair; those incomplete reports are not the acceptance evidence.

The subsequent discovery review made the signal-name table immutable/reused rather
than allocating it for each inspected method. A repeat full-window capture
(`20261023-091312-025576be.afprofile.zip`) remains complete and records 75.4 ms activation.
Concurrent build/test load and the single trial prevent a controlled speedup claim.
