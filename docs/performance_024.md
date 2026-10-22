# VCP performance qualification — 0.2.4

Implementation follows the six recommendations in [the original analysis](vcp_performance_024.md).
Source and portable release qualification are complete.
Detailed computational rationale is in CH-039–044 of [the history](computation_history.md).

## Implemented boundaries

1. Prepared tissue-inspection state uses field-level Qt notifications, avoiding repeated
   report conversion and visibility binding updates for each mesh.
2. Result provenance indexes pending owners once. Typed local tissue strategy changes
   reuse global relationship validation while retaining tissue capability validation.
   The profiler observes shared resource catalogues without repeatedly expanding them.
3. Native advisory collision checks retain collider snapshots and unchanged pair evidence.
   Geometry, transforms, contact membership, surface order and metric tolerance qualify reuse.
4. Stacking sessions have exclusive multi-call ownership and bounded reuse. Obstacle
   geometry crosses as owned native handles/frames; planning reads metadata only.
5. Height smoothing eliminates pinned variables and uses PIQP box bounds, preserving
   the original objective, limits and independent full-problem KKT certification.
6. Native material frames/operators are retained by accepted base geometry. Section
   profiles evaluate longitudinal coefficients once per column. Distributed inflation
   still refactors for changed distance. Internal envelope sides use draft meshes;
   accepted results remain fully prepared for display, picking and attachments.

No solver or repeated numerical geometry work moved into Python. Schema 4, authored
settings, Manual provenance, update modes, undo, save checkpoints and failure policy
are unchanged. No new dependency or replacement pinned donor kernel was introduced.

## Timings

Windows 11, Python 3.12.12, Qt 6.12.0, 24 logical CPUs. Baseline `52690bd` was frozen
with its own native library; candidate `6bf8b60` includes the complete implementation.
Measurements preceded the release version bump. Original anatomical files were untouched.

The 96-tissue/326-Fiber assembly uses the source and SHA256 recorded in the analysis.
Whole-application trials ran serially old/new/new/old, two trials per operation in
each process, with no concurrent build or test load. The user's other applications
remained running. System utilization was recorded; this is not an isolated benchmark.

| Operation, recorder off | Baseline range (median), seconds | 0.2.4 range (median), seconds |
| --- | ---: | ---: |
| One Section Profile edit | 1.32–1.41 (1.36) | 0.31–0.44 (0.36) |
| Ten committed profile edits before waiting | 1.51–1.70 (1.58) | 0.35–0.45 (0.41) |
| Source Fiber control-point edit | 1.66–2.57 (2.08) | 0.95–1.78 (1.36) |
| Ribs translation, large dependent assembly | 6.24–6.67 (6.45) | 4.66–4.90 (4.70) |

These measure command through **all jobs settled**, including advisory checks, not
physical display latency. The same Ribs update still resolves 211 Fiber paths, 70
construction evaluations and 63 tissue chains. No failed jobs occurred.

Separate native comparisons on the 13,845-vertex/27,136-triangle base:

- Height smoothing: 1.77–1.82 s original versus 1.56–1.60 s reduced, alternating in one
  process. Both used 24 iterations; maximum vertex difference 3.94e-13 m, with original
  constraint/optimality certification passing. This is not a different smoothing formula.
- Changed-settings medians: Section Profile 30.3→23.0 ms; Distributed 67.0→39.9 ms;
  Control Point 24.0→19.8 ms. Every tested vertex and triangle is identical.
- Unchanged 625-vertex stacking fixture: plan 18–21→1–2 ms, final 197–242→5–6 ms.
  This large gain is reuse of unchanged work; it is not a claim for changed-provider
  solving. Changed receiver/provider tests match fresh sessions exactly.

## Profiling and viewport

Four final headless reports are complete with no collector losses. A recorded profile
edit spends about 21 ms total in collision checks versus 849 ms in the original
investigation. Ribs preparation/dispatch resource observation is about 5 ms in the final
report versus 2.11 s originally; inventory work remains separate (~174 ms over seven
samples). Inclusive collector durations overlap and cannot be subtracted as exact overhead.
The final recorded Ribs update takes 5.77 s versus recorder-off 4.66–4.90 s.

Hidden production QML/D3D11 viewport trials use normal controller ticks and staged
publication, with synchronous texture readback. Dispatch is 43–48 ms and settling
0.96–1.09 s with recording off; 53–60 ms / 1.25–1.33 s while recording. The original
investigation measured 632–650 ms dispatch / 3.56–3.66 s settling. This is supporting
before/after evidence, not an alternating final GUI comparison. Images were inspected;
there were no QML warnings. Frames still reached 233–271 ms off and 309–362 ms on.
This release does **not** establish a 30 FPS interaction target or physical input/display
latency. No visible windows or desktop input were used.

## Correctness and ownership

- Eleven assembly checkpoints, 1,456 arrays each, match the frozen baseline exactly:
  opening, Humerus/Ribs/Tibia moves, two source Fiber edits, and their undo results.
  This replay uses `skeleton_all_authored_muscles_v002.anthroforge` from the migration's
  candidates directory, SHA256 `2bcd72212488a5ea5ca4a19f2d5d2900a9ff9a814560156203f42e3721bf07b6`;
  the timing workload uses its qualified saved copy named in the original analysis.
- Golden native fixtures cover inflation families, branches, relaxation, smoothing,
  material domains, attachments and exact draft/full envelope composition. Height
  smoothing stays within existing tolerances; the other kernel outputs are exact.
- Tests cover cache eviction/clearing, source changes, cancellation, concurrent reads,
  exclusive stacking sessions, failed leases, changed provider/receiver inputs, and
  full versus incremental collision findings. Original bindings are never recaptured.
- The development gate and final source rerun each passed 1,722 tests, including the
  added lifecycle/parity cases. Five native CTests, typing, style/function limits and
  numerical/runtime checks pass.
- Separate ownership review: caches are engine-owned and bounded; running jobs retain
  their leases. Mutable stacking/collision work has exclusive access, immutable tissue
  preparation supports concurrent reads, and contexts cannot return across lifecycle
  clears. Render staging and displayed picking revisions remain unchanged. Profiler
  resource categories preserve source deduplication and label conservative bounds.

## Delivered package

The canonical `dist/0.2.4/AnthroForge.dist` passed the full relocated minimal-PATH
portable suite: construction, tissue inflation/stacking, attachments, persistence,
inspection, painting, routing, feedback, preferences, runtime profiling and hidden
rendering. Its native library resolves inside the relocated package, without the
development SDK or optional SciPy dependencies. The suite's UI platform was offscreen;
it does not establish physical desktop interaction acceptance.

The real assembly also passes packaged open/edit/undo/save/reopen/render. All 619
authored object definitions and transforms remain unchanged after undo; 1,587 saved
geometry/path arrays match the input exactly. The packaged 0.2.4 profile is complete,
has no collector losses, and contains the new native preparation/evaluation calls.
Packaged tissue and assembly images were inspected. The original input hash remains
unchanged. Application sources staged for the executable match the release sources
exactly; its build revision is `9a69b48` (the dirty flag records documentation edits
during staging, not uncommitted production changes).

One companion archive is `dist/AnthroForge-0.2.4-source.zip`, including the new adapters,
tests, documentation and existing dependency attribution. No second release folder
or alternate executable distribution was created for this version. Qualification
copies live under ignored `build/` only.

Local-only evidence: `build/vcp-performance-024-release/`, including geometry replay,
counterbalanced timings, `.afprofile.zip` reports, hidden captures and build logs.
The production anatomical fixture is external and is not included in the repository.
Repository tests/compact fixtures are portable; these large-case measurements require
the named local input. Do not sum gains across overlapping pipeline stages.
