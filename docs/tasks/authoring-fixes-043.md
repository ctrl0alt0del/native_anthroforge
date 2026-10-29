# Authoring parity fixes — 0.4.3

- Branch: `codex/authoring-fixes-043`; integration: `main`.
- Baseline: `31e9138f`; writer: local direct work, no delegation.
- Status: complete; 0.4.3 qualified for integration into `main`.

## Authorized outcome

Implement the confirmed [authoring contract](../authoring_043.md), closing audit A1–A4:
resolved editing queries, candidate images/numerical inspection, contextual queries,
and literal JSON arguments. Recovery/project-library and feedback services remain out
of scope. Preserve calculation algorithms, attachments, undo, schema 9 and source files.
Follow engineering guidelines and 15-line functions. Background/offscreen testing only.

## Sequence and recovery

1. Contracts and regression fixtures.
2. Shared component read model; desktop integration and paging.
3. Candidate adapters, capture lifetime, geometry paging and isolated scene rendering.
4. Domain choice/effective-state queries and desktop integration.
5. JSON Pointer literal paths; transport compatibility.
6. Full gate, production profiling, visual/offscreen and portable qualification; release.

Use `uv run --no-sync`. Native build:
`C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native`.
Set `AF_NATIVE_BUILD` and `ANTHROFORGE_NATIVE_LIBRARY` consistently. Temporary outputs:
`build/authoring-fixes-043`; isolate preferences there. Preserve unrelated `__init__.py`.
Checkpoint/push coherent increments and validated merge under standing repository workflow.

## Acceptance

Paired UI/API controls and effective-state results; immutable preview geometry and images;
stale/cancel/release/export retry; JSON references/literals; unchanged geometry/bindings/
history; native resource release; 96-muscle profiling; full development and portable gates.
Deliver one `dist/0.4.3/AnthroForge.dist` and companion source archive only after qualification.

## Research

Existing shared helpers and native borrowed buffers are authoritative. Reviewed official
[Qt model/view](https://doc.qt.io/qt-6/model-view-programming.html) and
[RFC 6901](https://www.rfc-editor.org/info/rfc6901/) for adapter separation and pointer syntax.

Checkpoint: shared component buffers and `editing.inspect` now serve the desktop editor.
Moved-Fiber paired UI/API regression, immutable buffer ownership, bounded paging and
changed-revision rejection pass (31 targeted runtime tests; architecture and focused mypy
pass). Queries preserve authored data/history. No release qualification yet.

Remaining: broaden restriction/provenance coverage (junctions, driven controls, fields),
then implement candidate capture/render/export, contextual queries and JSON literals.
Full gate, production profiling and packaging remain pending.

Candidate checkpoint: all eight source adapters now capture retained resources. Numerical
paging, canonical connectivity, stale/cancel/replacement/release, export retry and the
six additional candidate-family probes pass (12 tests; 14 including architecture).
Full core/application/native mypy passes (636 modules). One hidden GPU surface capture
was visually inspected; broader multi-angle/production evidence remains pending.

Development rendering exposed mixed native DLL directories: the engine used the qualified
build while Qt loaded the obsolete build/dev viewport. Desktop runtime now honors
AF_NATIVE_BUILD when unbundled, matching the existing build/package tools. The repeat
renders the actual candidate. Packaged runtime still prioritizes its bundled libraries.

Next: contextual queries and JSON literals; finish A1/A2 edge coverage and full qualification.
No 0.4.3 release or main merge yet.

Contextual queries and JSON literals implemented: exact preparation/reference tokens qualify
assembly and skeleton mapping choices; surface-role and skin defaults/effective queries are
shared with desktop. RFC6901 literal subtrees retain legacy substitutions elsewhere and
validate paths before command invocation. Component reads now report driven/junction
restrictions and explicit deformer weights. Latest focused checks: 45 passed; typing passed
after component bool annotations. Optional prepared skin appears in candidate comparisons.

Remaining qualification: stronger capture/export ownership and Qt-free probes, production
paging/memory/profile measurements, multi-angle render evidence, full gate and portable build.

Qualification follow-up: the first complete suite found a lost LATTICE category alias and
two old tests calling the removed private component reader. Restored LATTICE/GEOMETRY aliases,
and migrated those tests to the shared reader. Follow-up 33 tests passed. Full gate is being
repeated after these changes; the initial run was not a pass (2,812 passed, four failed,
including a function-length check caught while the qualification script was being written).

The actual 96-muscle assembly exposed an older shared-preview validity bug: formula/driver
ports were rejected because their owners are not scene objects. Diagnostic showed all
captured revisions equal, and the document unchanged. Validity now delegates all port kinds
to the existing revision resolver; missing/changed ports still invalidate. No numerical
algorithm changes. A driver-backed preview/staleness regression and production SCM preview
pass. Capture resources now appear under inspection_capture in existing profiler ownership.

Production run (source hash unchanged): 349 component targets, 29,199 rows / 352 pages;
median 2.03 ms, p95 2.85 ms, maximum 4.32 ms per 256-row page. Captured geometry: 98,648 rows,
48 pages, median 0.114 ms, maximum 0.497 ms. Thirty captures retain exactly one API snapshot;
initial 5.23 ms, subsequent about 2.4 ms. Two split-view exports took 2.61/2.21 s including
isolated render startup. Front/oblique SCM images inspected. System busy fraction 14.6%;
single diagnostic run, not a controlled speedup claim. No Qt imported into numerical process.
Evidence: build/authoring-fixes-043/production, plus source-portable mirror image/data test.
Export lease retirement, canonical buffer round-trip and separate Qt-free subprocess pass.

Repeated development gate passes: 2,819 tests, six native CTests, Python/PowerShell/native
style, typing, numerical checks and doctor. Subsequent focused tests cover complete driven
component/weight restrictions and Manual Fiber provenance; final full-suite repeat pending.
Desktop live layer render versus isolated exported render: exact pixels for Split/front;
maximum one 8-bit color level for Overlay/oblique, same layer IDs/camera, hidden windows only.
Executable JSON example passes. Local links checked. Source inspection/runtime ownership
review complete: application owns resolution/policies, core immutable records, transport
literal decoding, native existing transforms, desktop render-only adapter. No new pool,
geometry evaluator, duplicated property writer or project-schema change.

0.4.3 version is staged for canonical package qualification. Portable release/merge still pending.

## Final qualification — 2026-10-29

The preceding checkpoint notes preserve their original pending status. Final runtime
revision: `ce08feb6`; packaged metadata records a clean tracked tree at that revision.
The full suite repeated after the final Manual-state and restriction changes passes:
**2,821 tests**, 385.91 seconds. The earlier complete development gate also passed six
native CTests, native/Python/PowerShell style, numerical checks and native doctor; final
typing passes across 643 modules. One extra test invocation failed at collection because
`pytest` was invoked directly without the repository on the module path. The documented
`python -m pytest` invocation above passes; no product change was needed.

The relocated executable passes **all 36 portable workflow groups** with a minimal PATH
and its bundled native library. This includes the new queries, literal JSON names,
historical path/mesh captures, exact canonical buffers, and image export after candidate
cancellation. The packaged mirrored Before/After image was visually inspected. Evidence:
`build/authoring-fixes-043/portable/portable-check.json` and `candidate.afinspection.zip`.
No visible test windows or desktop input were used. Hidden QQuickRenderControl pixels
and offscreen UI checks do not establish hands-on interactive acceptance.

Final production profile: `build/authoring-fixes-043/production-final/production.afprofile.zip`.
The 96-muscle source remains byte-identical (SHA256
`86c08109700bb6e12de807dca8ef93ba37efe33f0a60dc3c2a87a71cc87be554`), and document/history
state is unchanged. The numerical process imports no Qt. Measurements:

| Work | Evidence |
| --- | --- |
| Component paging | 349 targets, 29,199 rows / 352 pages; median 2.36 ms, p95 3.15 ms, maximum 4.11 ms per page. |
| Geometry paging | Exact reconstruction of 98,648 rows / 48 pages; median 0.115 ms, p95 0.449 ms, maximum 0.567 ms. |
| Capture ownership | Thirty captures retain one API snapshot; median 3.94 ms. Independent export leases survive API release and retire afterward. |
| Rendering/export | Front/oblique SCM reports: 2.27 / 2.21 seconds including isolated renderer startup. |
| Native geometry memory | Peak unique 633,647,378 bytes across the loaded assembly/caches; 2,157,736 bytes attributed to shared inspection resources, zero unattributed bytes. Owner totals overlap and must not be summed. |

System busy fraction was 12.65%; other processes and thermal state were uncontrolled.
These are diagnostic measurements, not a controlled speedup claim. Paired live desktop
and isolated export scenes use identical layer IDs/cameras: Split/front pixels match
exactly; Overlay/oblique differs by at most one 8-bit color level. Both were inspected.

Ownership/coupling review is separate from the tests: shared application services own
resolution and eligibility; immutable records retain resource owners; exports use the
existing coordinator; JSON literals stay in transport; Qt remains in presentation.
No numerical algorithm, worker pool, schema, attachment policy or undo contract changed.
Documentation links and the executable JSON example pass. Recovery/library and feedback
operations remain outside A1–A4, as agreed.

Delivery: one `dist/0.4.3/AnthroForge.dist`, with the companion
`dist/AnthroForge-0.4.3-source.zip`. The unrelated root `__init__.py` is preserved and excluded
from the source archive. Release documentation is refreshed without changing the qualified
runtime; subsequent commits contain documentation only.
