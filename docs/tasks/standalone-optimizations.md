# Standalone performance implementation

- Branch: codex/standalone-optimizations
- Integration: main
- Baseline: d810557795c2af002da0d86cfa7797317f9af4c4 (0.1.5)
- Status: implementation and validation complete
- Updated: 2026-10-18, Europe/Bucharest
- Writer: desktop implementation chat; direct work, no delegation

## Scope and order

Implement the four measured opportunities in [the audit](standalone-optimization-audit.md):
incremental desktop projections, indexed immutable document/dependency structure,
native intermediate geometry with deliberate finalization, and active scheduling
separate from completed history. Preserve all confirmed editing, geometry, dependency,
undo/redo, cancellation, checkpoint and persistence contracts. Follow engineering guidelines.

## Acceptance and evidence

Use serial profiler/unrecorded comparisons, existing cube/Body gestures, synthetic
scaling and long-session cases, native parity, shared-contract tests, the full
development gate, actual GUI inspection and portable qualification. Do not claim
whole-app improvements from native microbenchmarks or sum inclusive profiler spans.
Review ownership separately from passing checks. No new product feature or version
number is specified; retain 0.1.5 and record the source revision of the delivered build.

## Current state and next action

Baseline source/native snapshot is preserved under ignored
build/standalone-optimizations/baseline.

Stage 1 is integrated: a bounded application ChangeJournal describes record/field
changes, SceneProjection caches scene metadata and parent choices, and desktop-owned
PropertyProjection objects notify individual QML fields while preserving curve/point
and outliner identities. Authored dataclasses are projected without repeated deep
serialization. Visual-layer arrays are prepared once per component geometry update.
RenderModel retains existing staged leases; picking changes with displayed results.

425 tests, lint and mypy pass. Primitive and curve interaction GUI acceptance pass;
loft/lattice screenshots were inspected. A transient undefined-to-bool warning in the
outline visibility binding was fixed. Serial ABBA open-Activity mouse drags (80 events
per normal/Ctrl gesture) measured baseline handler means 12.41-13.83 ms and candidate
5.21-5.97 ms. Both recorded comparison runs stopped successfully. The candidate pilot
capture retained all events and reported zero curveChoice model replacements. Complete
comparison artifacts: build/standalone-optimizations/stage1-comparison. These are stage
measurements, not final integrated results. PySide 6.12 exposes only QQmlPropertyMap's
deprecated constructor; Python emits a deprecation warning, while actual QML has no
warnings. This adapter is isolated in desktop/property_projection.py.

Stage 2 is integrated: snapshot-owned, immutable entity/control lookups and hierarchy/
dependency indexes reuse fully validated relationship structure across value-only
changes. Relationship changes still run complete validation and rebuild their graph.
Revision-only replacements reuse the entire index. Runtime indexes are excluded from
project serialization. Native attachment ordering is linear instead of repeated scans.
431 tests and configured mypy pass, including structural invalidation, identity
collisions, cycle classification, historical snapshot isolation and serialization.
The 1,024-SCP synthetic admission median is approximately 1.4 ms versus the audit's
86.8 ms. This measures admission without worker dispatch or GUI. Evidence and an
ordinary runtime profiler capture are in build/standalone-optimizations/stage2.

Stage 3 is integrated: explicit native geometry-only roots propagate through deformation,
joining and Simple Solidify. One finalization chooses accepted topology before building
spatial/render data. Existing prepared APIs remain available and unchanged. Drafts are
rejected by picking; no lazy render-thread work was introduced. A per-engine, locked
base cache is capped at 64 entries/32 MiB of accounted native storage plus record allowance;
it includes every base-shape input and releases its ownership on eviction/session close.
21 new checks cover prepared/deferred equivalence, transforms, closed curves, hooks,
lattices, thickness, loft/caps/join/import, cancellation and cache invalidation/lifetime.
The serial geometry-only comparison measures 1.8 -> 0.43 ms (482 vertices), 20 -> 4.2 ms
(4,034), and 87 -> 16.3 ms (16,258); the last large baseline trial rose to 130 ms, so final
qualification must report that variance rather than claim a precise whole-app speedup.
The runtime capture is build/standalone-optimizations/stage3/geometry.afprofile.zip.

Stage 4 is integrated: JobRegistry owns active ID/key/owner/port/output indexes and
separate history. Tick, admission, dependency waiting, cancellation, invalidation,
checkpoint, save, viewport polling and profiler snapshots use active work only.
Terminal records retain diagnostics and retry recipes when relevant, but release
snapshots, futures, native cancellation handles and execution/cleanup closures.
Undo captures a compact restart recipe before retirement, including dispatch revision.
Six new ownership/index/cleanup/restart tests pass. Synthetic 50,000-row history now
has approximately 0.0013 ms idle ticks (audit: approximately 33 ms). A real 5,000-job
soak completed both unrecorded and recorded with zero retained snapshots/cancellation
objects. Evidence: build/standalone-optimizations/stage4 (including soak.afprofile.zip).

Integrated checks: the development gate passed with 458 tests before the final ownership
guards; targeted tests pass for the added cancellation-close, finalized-asset and control
projection boundaries. Seven GUI suites pass (primitive, interaction, workshop, large
geometry, curve gestures, camera gestures, profiler gestures), with no QML warnings.
Actual lattice and Body/Hook screenshots were inspected. The 66,560-vertex/133,116-triangle,
1,000-point cage retained complete geometry during staging and passed picking/cancellation.

Serial ABBA GUI comparisons used 80 events per normal/Ctrl gesture, mouse and keyboard
transforms, Activity open/closed, with recordings separately paired. Dormant handler means
were 9.27-11.20 ms baseline and 3.99-4.94 ms candidate (approximately 54-58% lower).
Every Ctrl case hit all 80 expected targets; confirmation/cancellation/undo passed.
Candidate traces report no curveChoice model events. Native snapping remains separately
attributed. All captures completed export and report no collector losses. Candidate
captures retained every event; the two baseline Activity-open captures reached the
ring budget and evicted 34,009 and 17,583 oldest events respectively. Baseline trace
counts are therefore retained-window lower bounds; the unrecorded ABBA timings do
not have this limitation. This retention is explicit in the manifest/evidence.
See [machine-readable evidence](standalone-optimizations-evidence.json) for individual
trials, frame distributions, system load, geometry timings and collector counts.

Limits: the large-cage spot check improved accepted computation from 443 to 234 ms,
but edit commands still average 67 ms (baseline 74 ms); frame mean is 43 ms. This is a
single paired spot check, not an ABBA speedup claim, and it does not meet the soft
50-ms/30-FPS targets. General Python coordinate-to-presentation preparation for dense
cages remains a future measured optimization; no renderer/algorithm replacement is claimed.
The repeated geometry comparison measured 1.85-1.89 -> 0.42-0.44 ms at 482 vertices,
20.0-21.0 -> 4.20-4.27 ms at 4,034, and 91.7-92.6 -> 17.5-25.5 ms at 16,258.
The large-case variance prevents treating a single ratio as a universal speedup.

Ownership review: document indexes are immutable and snapshot-owned; the bounded journal
retains descriptions rather than documents. QObject projections are desktop-only. Native
drafts cannot enter Asset storage or picking, finalization does not mutate cached/published
meshes, and cache eviction preserves active owners. Coordinator indexes are lifecycle-owned,
removed before execution payload disposal; historical rows keep no native cancellation or
snapshot references. Restart recipes are captured before retirement. Qualified geometry
formulas, staged renderer leases and shared application policies remain intact.

Final qualification: tools/check.ps1 passes with **462 tests**, native build/CTest/style,
Blender-reference parity, Python/PowerShell checks, numerical checks and native doctor.
The added projection acceptance exercises a 128-point curve in 512 SCPs with the inspector
visible/hidden, stable point selection, undo and explicit evaluation. Its screenshot and
the relocated executable's rendered primitives were inspected. PySide constructor
deprecation warnings are the documented isolated adapter warning; QML checks are clean.

Portable packaging and relocation checks pass under a minimal PATH with developer
Python/Qt environment variables removed: import, attachments, all primitive/deformer
families, deletion, subdivision, saving/reopening, rendering, GUI and runtime profiling.
The optimized executable is dist/AnthroForge.dist/AnthroForge.exe. Its embedded source
revision is **74367907fee7453e0be652b36f56af5524b2f958**, tracked_changes=false. Later commits
add only qualification tooling/evidence. Version remains 0.1.5. Raw captures and binaries
remain local/ignored; the committed evidence includes portable and long-curve results.

All four requested optimizations are complete. Delivery uses the normal task-branch
merge/push to main; Git ancestry records the integration. The explicitly reported soft
responsiveness limit for dense cages is broader work, not a deferred part of these changes.

## Recovery

Normal Windows development setup applies. Measurements and raw captures stay under
build/standalone-optimizations; commit compact evidence with its provenance. The
baseline is reproducible from the named Git revision. Preserve unrelated __init__.py.
