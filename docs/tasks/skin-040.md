# Skin migration 0.4.0

- Task branch: `codex/skin-040`; integration: `main`.
- Starting revision: `6260864` (qualified 0.3.7 UI workbench).
- Status: foundations implemented; full skin workflow remains in progress, not merge-ready.
  Schema 7, immutable skin resources, shared settings commands and vertical inspector exist.
  No envelope/topology/deformation/fitting/export pipeline is connected yet.
- Last updated: 2026-10-26, Europe/Bucharest.
- Direct work, no subagents. All execution/validation must remain background/hidden.

## Outcome and acceptance

User requests moving existing addon skin functionality into the standalone app for
0.4.0, including calculating fitted bones/weights to reproduce shortcuts. Preserve
anatomy, geometry/attachment behavior and the existing engineering,
checkpoint/push and single-distribution rules. No runtime changes are made yet.

## Decisions and relevant files

- [Specification](../specification_040.md) and [implementation plan](../implementation_040.md)
  are confirmed. Schema 7 retains readers 4–6; stale export offers explicit accepted/update/cancel.

- [Migration inventory](../skin_040_inventory.md) records production code owners,
  settings, current-versus-legacy behavior, numerical porting work and future evidence.
- Addon source `fae36aba1b208676cf21d7c4a78a20d5b1f68c66`; inspected skin paths clean.
- Full current skin pipeline plus shortcut-to-bone fitting is in scope.
- Confirmed delivery priority: reproduce existing addon behavior first, then improve it
  in later work. Preserve algorithms/defaults/supported cases while adapting ownership
  to the standalone architecture; keep proposed enhancements separate from migration.
- Export starts with OBJ, preserving quads; keep a narrow, extensible format interface.
  OBJ does not serialize rigs. Retain fitted data/preview in the project.
- Add Skin to the existing right inspector and arrange Shape / Shortcuts / Inspect /
  Skin vertically on its left edge. This replaces the proposed separate Skin mode.
- Reuse the coordinator, native geometry/material contracts, brushes, Issues, profiler,
  immutable results and workbench; no Blender runtime or duplicate scheduling system.
- Current addon publishes usable quality-warning geometry. Older hard-rejection prose
  is superseded by actual `core/mesh_issues.py` and its callers.
- Bone fitting is untracked local addon work; its source fingerprints and actual public
  versus authoring-only contracts are recorded in the inventory. Do not attribute it to
  the clean source commit or claim existing qualification of its standalone port.

## Current state and verification

Read panels/operators, model/settings, field/gap kernels, topology/guide preparation,
reference/LE/FAST/contact code, bone sampling/fitting/preview/publication and existing
fixture/test names. Checked official
upstream APIs. No runtime/parity/GUI qualification or geometry acceptance performed.
Initial source qualification: six addon bone-fitting tests and 21 deformation tests
pass under the standalone Python 3.12 environment using the existing addon native DLLs.
These establish source controls only, not rebuilt-native or application parity. Matching
`pytetwild==0.4.2` and `pyinstantmeshes==1.0.0` import in this environment.
Source controls also pass 35 skin/gap/tile and 40 topology tests. These use addon binaries,
not a rebuilt standalone skin kernel. Source DLLs/projects were not modified.
Foundation contracts: 17 targeted tests passed. First broad run: 2,256 passed and one
expected-version test failed because it still rejected newly supported schema 7; corrected
its unsupported version to 8. Broad rerun: 2,258 passed. Ruff/mypy and function limits passed
for foundations. Offscreen skin tab navigation, decimal setting and Undo checks pass;
font-enabled capture inspected at `build/skin-040/ui/skin-settings.png`.
Native coarse fields now build in the existing library: raster, Euclidean distances,
26-connected exterior, quantized collagen and combined envelope. Twelve comparisons
against unmodified addon modules at resolutions 16/32/48 agree within roundoff (1e-12 gate).
Seven initial native-adapter/architecture tests passed; native CTests 5/5.
Local parity detail: `build/skin-040/field-parity.json`; rerun with
`tools/check_skin_fields.py <addon-root>`. Full settings and remaining pipelines still pending.
Gap kernels are pinned with hashes under `native/migration/skin` and compile privately
without OpenMP. Owned gap-scene sampling passes source gap-policy/winding/same-owner cases.
MC33 C++ extraction is qualified against scikit-image 0.25.2: 6,344 initial cases exact
in vertices and faces, including binary/ternary cubes and 33-cubed random tiles. Source
subset pinned with both licenses under `native/vendor/bioimage-cpp`. Current native and
adapter checks at that checkpoint: five CTests and 17 focused Python tests passed.
Native reconstruction now connects the field and gap kernels through protected-grid
preparation, bounded tiled extraction, native stitching, support filtering and eight
constrained Taubin iterations. Cube, separated-cubes and overlapping-cubes source controls
match vertices/connectivity exactly. `build/skin-040/envelope-review.png` visually inspected:
coarse-fixture protrusions occur in both addon and port, so parity is not shape acceptance.
Running cancellation inside native tile preparation passes and does not poison reuse.
The five-finger source-control experiment was stopped after more than 45 CPU-minutes
inside the addon, before reaching the standalone phase. No performance/geometry result
exists for that fixture. Log: `build/skin-040-digits-parity.log`. Do not restart blindly:
add progress/timeout diagnostics first. Its invocation was
`check_skin_envelope.py <addon> <digits_blend.capture.npz> Thumb,Index,Middle,Ring,Little build/skin-040/digits`.
Native material binding capture is connected through the source scene. Typed SkinStage
records own stage-buffer resources; save/read retain them and reject checksum corruption.
Fourteen binding/foundation/architecture tests passed at the binding checkpoint.
Native diagnostic bundles now retain quality, gap coverage, source intersections and
removed-component counts. Named decoding distinguishes unavailable checks from clean
findings. Eight envelope/architecture tests pass; mypy (442 files), Ruff and format pass.
The three source controls also match all six binding arrays exactly, including retained
source/triangle identities, barycentrics, weights, offsets and support. Contributor capture,
coordinator/publication and complete UI remain pending. No production skin acceptance.
Next integrated checkpoint: batched C++ contributor transforms/assembly, reflected winding,
source indices and absolute gap distances; source-selection policy suppresses fibers represented
by accepted tissue without consulting viewport visibility. Sixteen foundation/capture tests
passed. Instant Meshes file API produces 246 actual quads on the dependency cube; its array
API silently triangulates on readback and is not suitable here. PyTetWild produces 2,844 tets
with one thread. These are executable dependency probes, not anatomical qualification.

Envelope build now has a shared command (`skin.envelope.build`), native worker task, dispatch
observations, owned binding/source arrays, coherent undo, and persistence. Three integrated
job tests pass at resolution 24; production default remains 220. The latest broad run before
this job integration passed 2,286 tests (175 seconds). Topology, final deformation, fitting,
OBJ, generation viewport display and complete Issues integration remain unfinished.

Skin settings UI now includes symmetry plane, proxy resolution, constraint strength and FAST
handles. Offscreen decimal/integer edits, vertical navigation and Undo pass. The radius
question is pending: a separate physical `fiber_radius` defaults to 1 mm while workspace
display radius stays independent (announced implementation assumption, not a user answer).
This capture uses the existing native tube constructor; anatomical/Blender tube parity is
not yet qualified. Preserve this distinction in later acceptance.
App version remains 0.3.7; writer now schema 7 with readers 4–7. Unrelated root
`__init__.py` is preserved. Source `.blend` files remain untouched.

## Next actions

1. Finish foundation UI settings and current broad gate; corruption coverage now passes.
2. Qualify executable topology/tetrahedral dependencies and build maintained native kernels.
3. Finish native diagnostic bundles, contributor capture and coordinator/publication pipeline.
4. Continue integrated topology, deformation, fitting, OBJ and full qualification per plan.

All three initial questions are answered. No automatic minimal-bone search or
multi-shortcut rig composition is implied: preserve the existing configurable bone
budget and independent fits. General animation editing and rig-capable export remain
separate. No automatic remeshing on deformation and no silent backend fallback.

## Recovery inputs

Addon root is recorded in the inventory. Windows-only fixtures remain under
`E:/development/WIP_models`; local presence is not proof of geometry acceptance.
The containing Git commit identifies this checkpoint; inspect remote reachability
before resuming from another machine.
