# Python/native algorithm boundary audit

- Task branch: `codex/native-boundary-audit`
- Integration: `main`
- Starting revision: `7c55151999d043269d09a417623e6ac73e92302c`
- Status: implementation and qualification complete; ready for normal integration
- Writer: desktop, direct work; 2026-10-18 Europe/Bucharest

## Outcome

Audit migrated standalone algorithms and remove unnecessary Python numerical loops.
Explain the existing Python choice from actual implementation and original stack
decision. This is not a whole-application rewrite or migration of future skin/fiber tools.

## Findings and ownership

The current C++ library already owns attachment capture/propagation, curves, loft/body
construction, Hook/Lattice/Solidify, spatial queries and transforms. The standalone has
no Blender runtime dependency. Python owns immutable records, commands, transactions,
scheduling, validation, persistence and Qt adapters by the original stack decision.

Confirmed remaining boundary problems: influence inversion/membership masking in
`native/construction.py`; display curve/cage connectivity and cubic query packing in
Python; per-point native transform dispatch in `desktop/authoring_actions.py`.
Move geometry preparation to batched C++ APIs and group point transforms by target.
Preserve membership, curve ordering/closing, transforms, snapshots, undo and native
cancellation. Keep constant-size UI calculations and record/identity operations in
Python. Dense UI projection costs require separate evidence, not a claim that these
small kernels alone eliminate the previously measured dense-cage latency.

## Implemented checkpoint

Added native influence evaluation (default influence requires no allocated weight
array), display polyline/cage connectivity and cubic query packing. Grouped selected
point conversion by target frame while preserving input order and command semantics.
Native construction/Blender parity tests pass (143); focused preparation, curve-query,
gesture and architecture tests pass (55). The development gate passes with 487 tests,
native build/CTest/style, mypy, formatting/lint, numerical dependencies and native doctor.
The first gate caught a missing new adapter parameter annotation, now fixed. Existing
QQmlPropertyMap constructor deprecation warnings remain isolated to that adapter.
GUI primitive creation/editing, imported-vertex weights, base Hooks, insertion/snapping,
selection, undo and camera gesture acceptance pass without QML warnings. Runtime
profiler gesture qualification passes five captures, including recording boundaries
during normal/Ctrl drags, cancellation, undo and Activity open/closed. Curve/handle
colors and deformed cage/loft display were visually inspected.

Portable packaging and relocation checks pass under a minimal PATH without developer
Python/Qt settings: headless import, attachments, primitives/deformers, deletion,
subdivision, save/reopen, rendering, GUI and runtime profiling. Executable:
`dist/AnthroForge.dist/AnthroForge.exe`, version 0.1.5, packaged source
`42af2d9eb8abeb4beb7d94db58de767e818bc37d`, tracked_changes=false.

Serial ABBA, 25 unrecorded calls per case per leg, identical rounded output hashes:

| Preparation workload | Before median ms | After median ms |
| --- | ---: | ---: |
| 100,000-point default Hook | 0.740–0.749 | 0.588–0.605 |
| 100,000-point weighted/restricted Hook | 4.099–4.260 | 3.122–3.141 |
| 1,000-point cage display lines | 0.776–0.788 | 0.545–0.558 |
| 1,000-point closed curve query packing | 1.614–1.641 | 0.571–0.572 |
| 1,000 selected points, coordinate conversion | 22.379–22.968 | 1.116–1.165 |

The last experiment intercepts command publication to isolate preparation; it does
not establish full multi-point gesture speed. Each leg also exports an ordinary
runtime report; [compact evidence](native-boundary-audit-evidence.json) records timings,
output checksums and native calls. Source snapshots/reports remain local ignored data.

## Audit coverage and remaining Python

Inspected production Python arithmetic/array operations and loops, the native ABI and
its callers, addon attachment-kernel provenance, Blender primitive provenance, and
the original stack decision. Existing native owners cover mesh import/triangulation,
bounds/BVH/normals/render buffers, attachment capture/propagation, matrices and point
transforms, Bézier handles/sampling/frames/subdivision/nearest queries, lofts/bodies,
curve deformation, Hooks, custom falloff, lattices/resizing, and Simple Solidify.
There is no standalone Python solver, optimizer iteration or Blender API fallback.

Remaining Python array work is authored-record packing, stride/column layout conversion,
mode-flag normalization, validation, and serialization. Document dependency traversal,
reference/membership identity mapping, command edits, scheduler state and UI projection
are application logic. Fixed-size arithmetic remains for 3D UI offsets, fitted bounds,
TRS values and matrix validity. Moving each scalar operation to a separate native call
would not create useful batching. Per-point Qt records and multiple document updates
are still a potential scaling cost; this task does not claim those costs are eliminated.

The original choice of Python was reuse of application/authoring contracts and development
convenience. Neither Qt, headless execution nor AI requires it. The current geometry
engine is usable without Python through its C ABI; the document/command application
core is still Python. A full C++ document/UI backend would require migrating those
contracts and their persistence/history/scheduling behavior, not just replacing kernels.

Later anatomy algorithms have not been copied into the standalone yet. In particular,
the addon's `core/warm_start/arap.py` still has a Python optimization loop; that is future
migration work, not an algorithm currently executed by this application. Its entire
retained loop must become C++, consistent with the existing engineering rules.

Official references: [Qt C++ models](https://doc.qt.io/qt-6/qtquick-modelviewsdata-cppmodels.html),
[Qt performance guidance](https://doc.qt.io/qt-6.12/qtquick-performance.html),
[ctypes native calls](https://docs.python.org/3.12/library/ctypes.html).
CDLL releases the GIL during native calls; Python preparation still has its own cost,
and a synchronous native call still occupies the calling UI thread.

## Verification and ownership review

Commands: `tools/check.ps1`; `uv run --no-sync python tools/native_boundary_audit.py
<output>` in serial baseline/candidate/candidate/baseline processes; GUI tools
`primitive_acceptance.py` (ordinary and `--interaction`),
`curve_interaction_acceptance.py`, `view_gesture_acceptance.py`,
`profiler_acceptance.py`; `tools/package.ps1`; `tools/check_portable.py` against
`build/native-boundary-audit/portable relocation/AnthroForge.dist/AnthroForge.exe`.

Direct ownership review, separate from test results: one native influence owner serves
Hook and Lattice; display/query preparation is Qt independent; Python adapters own
buffer lifetime and record packing. Existing C ABI operations remain compatible.
Geometry semantics are unchanged, including explicit-empty membership, invert without
weights, cyclic curves, degenerate grid axes, negative/nonuniform transforms and safe
cancellation. Grouping respects target identity and preserves input order; conversion
finishes before document edits. No parallel scheduler, document representation or
rendering framework was introduced. Remaining UI record costs are explicitly scoped
above, not hidden behind the numerical-kernel results.

## Integration

Implementation and required checks are complete. Merge and push normally to main;
Git ancestry identifies integration. Raw captures, source snapshot, logs and portable
outputs are local/ignored; compact evidence and reproducible tooling are tracked.

Preserve unrelated root `__init__.py`. Captures/builds stay in ignored
`build/native-boundary-audit`; compact evidence will be committed. Prior optimization
results remain in `docs/tasks/standalone-optimizations.md`.
