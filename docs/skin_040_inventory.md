# Skin migration inventory for 0.4.0

Status: **0.4.0 implemented, qualified and merged**; accepted limits remain in its
[task record](tasks/skin-040.md). The [0.4.1 audit corrections](tasks/release-041.md)
complete reference preparation, diagnostics, budgets, caching and inspector feedback.

**October 27 review:** the tables below describe the addon, including its bare-Fiber
contributors. The confirmed standalone contract now excludes construction from physical
draft/deformation sources, while retaining topology guidance. This intentional difference
supersedes the earlier thin-tube experiment and is implemented on the task branch. See the
[current specification](specification_040.md) and [task record](tasks/skin-040.md).

The user confirmed the full existing workflow for 0.4.0, including fitting bones to
reproduce a shortcut. Export starts with OBJ through an extensible format boundary.
Skin joins Shape, Shortcuts and Inspect in a vertical strip along the left edge of
the right inspector, following the supplied sketch. This supersedes the proposed
separate Skin mode or root-only inspector placement.

## Confirmed migration baseline

For 0.4.0, first reproduce the existing addon workflow, algorithms, settings and
supported behavior. Improvements to that behavior belong to subsequent work, after
the migrated workflow is usable and compared against the addon. In particular, bone
fitting retains its configurable budget and independent shortcut fits; automatic bone
count selection and multi-shortcut composition are not part of this migration.

Adapt implementation ownership to the standalone application: native numerical work,
the existing coordinator and shared operations replace Blender-specific integration.
Those architectural adaptations must preserve computational behavior and be verified;
they do not authorize silent algorithm substitutions or changed quality policies.
The confirmed vertical inspector and extensible OBJ export remain in scope.

Record observed source defects, parity differences and improvement proposals separately.
Do not describe source inspection as validation, or silently turn a migration problem
into an accepted limitation. Establish the cause and evidence for any necessary fix.

## Evidence boundary

- Standalone baseline: `6260864`, version 0.3.7, schema 6.
- Addon inspected: `fae36aba1b208676cf21d7c4a78a20d5b1f68c66` at
  `C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
  Inspected skin/topology/deformation paths have no local tracked changes.
- Bone fitting is additional **local, untracked addon work**, not attributable to that
  commit alone. Inspected its native fitter, capture/publication, UI, docs and tests.
  [Source fingerprints](skin_040_bone_source.json) record the exact inspected files;
  this does not claim addon release qualification or standalone parity.
- Read production operators, panels, properties, capture, computation, validation and
  publication, alongside their documentation and tests. Source inspection is not a
  claim that every fixture currently passes. No Blender project was modified or built.
- Existing standalone skin-only export rules specify scope; they do not constitute an
  implemented skin generator/exporter. `native/topology.py` manages mesh connectivity
  reuse; it is not the missing retopology engine.

## Current addon capabilities

Paths in the source column are relative to the addon root above.

| Area | Current behavior | Source owners |
| --- | --- | --- |
| Contributors | Root-scoped evaluated SCPs, muscles, soft tissues/blobs and applicable standalone Fibers; includes source/mirror roles regardless of display visibility. Muscle BASE, controls and existing skin are excluded. Consumed Fibers avoid duplicate contribution when the owning muscle has valid output. | `adapters/draft_skin/capture.py`, `adapters/deformation/capture.py` |
| Envelope | Minimum distance, additional collagen depth, core radius and falloff, expressed as percentages of model longest axis. A closed generated envelope is distinct from quad topology. | `properties/draft_skin_properties.py`, `core/draft_skin/settings.py`, `core/draft_skin/solver.py` |
| Collagen | Per-SCP Auto, Uniform and Painted modes. Auto uses name terms ear/cartilage/nasal for zero, otherwise one. Painted weights are absolute; unpainted vertices inherit the scalar. Fill, clear, brush weights and painting are exposed. | `ui/panels/scp_skin_section.py`, `adapters/draft_skin/painting.py`, `core/draft_skin/settings.py` |
| Gap control | Maximum gap eligible for closing and filling strength, globally and per contributor. Strength does not override maximum gap. Native corridor/exterior tests distinguish protected openings from enclosed voids. Contact at zero separation is allowed by the gap predicate. | `properties/skin_gap.py`, `ui/panels/skin_gap.py`, `core/draft_skin/gap_*`, `native/fiber_ccd/af_skin_*` |
| Envelope computation | Rasterized required/rest/collagen fields, exterior accessibility, distance transforms, 16 collagen levels, protected fine lattice, marching cubes, supported-component filtering and eight constrained smoothing passes. | `core/draft_skin/raster.py`, `fields.py`, `gap_solver.py`, `gap_tiles.py` |
| Resolution/resources | Target 220 cells along the longest axis, minimum 160 under the coarse-grid memory rule; protected gaps can require finer sampling. Compact constant/varying tiles reduce memory. Cancellation and resource limits are explicit. | `core/draft_skin/grid.py`, `resources.py`, `native/fiber_ccd/af_skin_tile_*` |
| Quad construction | QuadWild Muscle FLOW + Paths is the default; Instant Meshes is explicitly selectable. No silent backend fallback. Target count defaults to 8,100 (1,000–500,000), with actual count/limitations reported. | `properties/topology_properties.py`, `core/topology/constants.py`, `quadwild.py`, `adapters/topology/solver.py` |
| Topology guides | Paired closed Fiber loops produce authored annular patches. Open Fibers can be FLOW guides. Regular muscle material charts contribute direction samples/central paths, including constituent branched patches. | `adapters/topology/capture.py`, `engine/annuli.py`, `engine/guides.py`, `native/topology/field.cpp` |
| Density | Hierarchical SCP subtree budgets, target validation, adaptive all-quad refinement, optional muscle proximity. Requested counts are targets, not guarantees. | `ui/panels/scp_topology_section.py`, `core/topology/budgets.py`, `density.py`, `adapters/topology/adaptive_refine.py` |
| Symmetry | None, root-local X/Y/Z or custom origin/normal; solve one half, assemble reflected geometry and retain symmetry correspondence. | `properties/topology_properties.py`, `core/topology/symmetry.py`, `adapters/topology/engine/annuli.py` |
| Durable reference | Build tetrahedral proxy, anatomical/material samples, embedding, vertex identities and symmetry data. Keep an immutable, serializable reference; disposable solver caches may be reconstructed. Successful reference publication removes the temporary draft. | `core/deformation/reference.py`, `proxy.py`, `adapters/deformation/initialization.py`, `construction.py` |
| Final skin updates | LE (Linear Elasticity) is default; FAST uses reduced ARAP. Solve from the immutable reference and publish positions only. Connectivity, vertex order and identity remain fixed. Explicit rebuild replaces topology/reference; changing construction settings marks them stale. | `core/deformation/strategy.py`, `pipeline.py`, `native/deformation/elastic.hpp`, `reduced.hpp`, `adapters/deformation/runtime.py` |
| Shortcut bone fitting | Sample one continuous scalar float shortcut through final-skin updates in isolation; fit an independent weighted bone representation. User chooses range, bone budget and odd sample count. Public Scale Aware and authoring-only Single Active strategies remain distinct. | `docs/shortcut_bone_fitting.md`, `core/bone_fitting/`, `adapters/bone_fitting/`, `native/bone_fitting/native.cpp` |
| Fitted result/preview | Persist weights, transforms, sampled shortcut mapping and error metrics; preview without rerunning anatomy. Preserve original anatomy/skin. Addon publication uses a separate mesh/armature with ordinary channels and FCurves. | `adapters/bone_fitting/rig.py`, `publication.py`, `ui/bone_fitting.py`, `tests/blender/test_bone_fitting.py` |
| Contact/quality | Native unilateral contact with symmetry, separate validation of motion from displayed pose, bounded work. Residual intersections, inverted proxy elements and iteration limits are reported. No complete collision/containment guarantee. | `core/deformation/contact.py`, `anatomy_quality.py`, `native/deformation/contact*.hpp` |
| Lifecycle | Background work, progress/cancellation, input/revision validation and atomic publication retaining previous output on failure. Persistent reference identity and contributor compatibility checked before updates. | `adapters/deformation/request.py`, `publication.py`, `construction.py`, `adapters/job_revision.py` |
| Legacy workflows | Draft/topology warm updates and preparation of old bindings remain for addon files without a durable reference. They are not the current reference-based final-skin algorithm. | `core/warm_start/`, `adapters/warm_update/`, `ui/panels/warm_update_panel.py` |

## Source/documentation discrepancies to preserve explicitly

Current `core/mesh_issues.py::annotate` rejects empty/nonfinite/malformed meshes and
unusable indices/faces; it converts measured quality failures into Issues. It is called
by skin and topology result paths. The unused `gap_solver.require_coverage` helper and
older statements that every coverage/gap finding rejects publication do not describe
the current output policy. Gap validators can report a bridge as a failed quality
predicate without the publication policy rejecting every usable result.

`docs/draft_skin.md` also names an older job protocol, whereas current constants use
protocol 5. Standalone persistence must have its own contract, not copy historical
protocol labels. Older memory experiments explicitly failed geometry checks and are
not accepted-shape reference fixtures.

The current topology workflow may retain usable annuli/fill with explicit open-seam
warnings when a join fails. It does not silently repair them or claim watertightness.
Native construction failure, malformed data, cancellation and dependency/resource
failures preserve earlier output. Any deliberate change to this policy needs an
explicit product decision and computation-history entry.

## Confirmed scope additions and fitting limits

The user explicitly includes shortcut-to-bone fitting in 0.4.0; earlier deferral of
that system in this inventory is superseded. This includes its usable result and
preview workflow, not only a numerical report. It does not imply a general animation
editor, automatic anatomical joints, or exporting a rig through OBJ.

Current addon fitting behavior to preserve:

- One continuous scalar float shortcut, with other controls held at captured values.
  Use the same shortcut operations/policies that produced the anatomical deformation.
- Increasing range and odd sample count: default nine, UI range 5–33. Fit both endpoints;
  alternate interior samples are held out for validation. Minimum defines reference pose.
- Bone budget defaults to four, range 1–64. The algorithm fits weights/transforms for
  that budget; it does **not** discover a guaranteed minimal number of bones.
- Scale Aware uses the maintained independent-axis scale fitter with Dem Bones
  initialization/weight updates, scale bounds 0.25–4 and at most four influences per
  vertex. Unsupported shear/reflections and invalid weights are structural errors.
- Single Active remains available to authoring: one moving TRS bone plus a fixed
  identity background influence. The affine/shear experiment is not a product strategy.
- Samples must share vertex identities/connectivity. Replay the first sample to detect
  nondeterminism; record held-out/global/moving-region fit errors rather than claiming
  arbitrary-parameter accuracy from training error.
- Clamp outside the sampled interval. Native SLERP predictions supply saved sample keys;
  addon playback interpolates translation, scale and quaternion channel values linearly.
  Qualification must compare actual displayed playback, not assume equivalence between
  interpolation schemes at unmeasured intermediate values.
- Separately fitted shortcuts are independent; automatic composition is not supported.
  Fitting cannot repair defects in its sampled target meshes.
- Isolate capture from the live document; cancellation, stale publication rejection,
  coherent Undo and save/reopen must include the fitted result and its source provenance.

The app needs typed fitted-bone/weight/control records and native preview evaluation,
not Blender armatures or driver namespaces. These are derived companion results; they
must not replace the editable source or introduce Apply/Bake for anatomy primitives.
Keep them in the project with their reference and diagnostics. OBJ exports skin geometry
and preserves quad faces; it cannot carry bones, weights or shortcut drivers.

Export must have a narrow format interface over an immutable, validated export snapshot.
Common currentness, units, source selection and atomic-write rules belong above individual
writers. OBJ is the first writer; adding another format must not modify skin algorithms
or require a parallel export workflow. No rig-capable format is silently added in 0.4.0.

The vertical inspector tabs are **Shape / Shortcuts / Inspect / Skin**. Skin is a
document-level page, accessible without selecting the root. It shares the existing
inspector; selecting it does not create a new anatomical workspace or mutate geometry.
Preserve the other pages, drafts, keyboard/focus conventions and local layout state.
Detailed layout/interaction validation remains part of implementation planning.

## Standalone ownership and porting work

The following is an implementation direction, not a confirmed public API.

| Owner | Work to add/reuse |
| --- | --- |
| Core | One document-owned skin definition/output lifecycle, separate authored settings, accepted envelope/topology/reference, source identities and construction freshness. Typed shortcut-fit results and independent preview controls. No dummy SCP or TissueVCP. |
| Application | Contributor selection, reference compatibility, shared operations, construction/update dependencies, revision capture, saving/export policy, undo and lifetime through the existing coordinator. |
| Native C++ | Port field/raster/distance work, meshing preparation, guide projection/pairing/transitions, density/refinement, deformation, bone fitting and repeated preview skinning through owned batched inputs. Reuse maintained native kernels and spatial/material services. |
| Desktop | Vertical inspector tabs including Skin, build/update/fitting controls, collagen painting, guide/density editing, independent fitted preview, stage inspection and Issues using the existing workbench. No extra editor or calculation manager. |
| Export adapters | Extensible format interface with OBJ first. Shared export snapshot, eligibility, unit and publication rules remain application-owned. |
| Packaging | Qualify/pin topology and tetrahedralization dependencies for the app runtime, include source provenance/notices, and exercise a relocated portable build. |

Important migration differences:

- Addon topology construction creates temporary Blender meshes and uses `bmesh`,
  Blender modifiers, SciPy trees and NumPy geometry loops. Port numerical preparation
  and assembly as well as the solvers; copying only the final native call is insufficient.
- Coarse skin fields use SciPy distance transforms/connected-component operations;
  fine gap fields already have native kernels. Move repeated numerical work to C++
  without silently changing connectivity conventions, sampling or tolerances.
- The addon's packaged CPython 3.11 extensions are not interchangeable with the app's
  Python 3.12. Qualify native library/executable boundaries or matching builds.
- QuadWild has a maintained command-line path; external processes can be jobs owned
  by the existing coordinator. Do not recreate per-root Blender services, temp `.blend`
  capture, polling managers or competing worker pools.
- Reuse geometry leases, surface roles, material correspondence, immutable results,
  staged viewport publication, Issues and profiling. Presentation hiding must never
  remove a contributor or change authored output.
- Reuse brush interaction and native painting primitives, while giving collagen its
  own domain/validation. Tissue field semantics must not be reused by pretending an
  SCP is a TissueVCP.
- Generalize consumed-Fiber and muscle-chart rules to shared Curve/Fiber/Membrane and
  TissueVCP relationships. Resolve by supported construction/material capabilities;
  muscle/fat labels alone must not select a different numerical owner.
- Existing material domains and instance IDs should identify sources; do not adopt
  temporary Blender names or new nearest-surface reassignment during updates.
- Keep the latest accepted output while work runs or fails. Full rebuild and cheap
  position updates are distinct operations; do not automatically remesh after a shortcut.
- Legacy warm-start migration and Blender-project conversion remain separate from new
  standalone skin. Shortcut-to-bone fitting is now explicitly included. General rig
  editing/animation and multi-shortcut composition are not inferred from that inclusion.

## Proposed delivery sequence

1. Consolidate the confirmed full scope, vertical tabs and extensible OBJ export into
   the 0.4.0 specification and implementation plan.
2. Define document settings/results, contributor/reference contracts and lifecycle;
   establish paired fixtures before changing algorithms.
3. Deliver native envelope construction, collagen/gap controls and painting through
   desktop and headless operations; inspect actual output shapes.
4. Deliver quad construction, loop/FLOW guidance, density and symmetry, retaining
   warnings and explicit backend selection.
5. Integrate durable reference and LE/FAST updates, contact diagnostics, stale
   construction state, cancellation and persistence.
6. Integrate isolated shortcut sampling, native bone fitting, independent result preview,
   quality inspection and persistent fitted data through shared desktop/headless operations.
7. Complete OBJ export, production-assembly profiling, parity/visual checks,
   documentation and one canonical 0.4.0 package/source archive. Do not advance the
   release version merely because part of the pipeline is implemented.

No compatibility decision is made here. Existing standalone anatomy files should remain
usable; the final specification must state its reader/writer rules explicitly.

## Required acceptance inventory

This is the required acceptance checklist, not a claim that every check has passed.
The [task record](tasks/skin-040.md) records completed native parity, lifecycle, GUI and
profiling evidence and the remaining production-assembly and portable-release checks.

- Contributor capture: source/mirror identity, visibility independence, shared consumed
  Fibers, missing/failed tissue output, tissue base/final roles and partial anatomy.
- Collagen defaults/paint/fill/clear and gap inheritance; undo, source deformation,
  topology locks/remapping decisions and mirror reuse without duplicate authored fields.
- Envelope parity at multiple scales/translations, protected finger/toe gaps, contact
  versus penetration, cavities, memory limits and cancellation.
- QuadWild and Instant Meshes independently, paired loops, open FLOW, branched charts,
  density budgets, custom symmetry, unpaired guides/open-seam diagnostics, missing
  dependencies and the explicitly qualified QuadWild process exit exception.
- Reference preparation failure versus usable construction results; successful rebuild
  publication must be atomic and must not destroy the previous reference on failure.
- LE/FAST coordinate updates with exact connectivity/vertex-identity preservation;
  open-to-contact-to-open sequence, large shortcut changes, solver limits, contributor
  incompatibility and explicit reinitialization/rebuild.
- Bone fitting: Scale Aware and authoring-only Single Active, scalar eligibility,
  stable sample identity, source preservation, held-out validation, actual preview
  interpolation, clamping, fitting/capture cancellation, stale results and persisted
  playback without invoking anatomical calculations. Cover shortcut attachment policies
  and driving formulas, not only synthetic TRS targets.
- Editing while queued/running, obsolete work, complete publication read validation,
  Manual inputs, workspace priorities, Undo/Redo, save checkpoints, reopening without
  blanket recalculation and native resource release.
- Export only the eligible skin revision; no anatomy/debug content. Quad preservation
  depends on the chosen format and must be measured in a round trip.
- Profile capture/preparation, native stages, reference/cache memory, publication and
  actual UI work separately. Offscreen tests do not establish physical input latency.

Existing addon tests cover these categories in `tests/unit/test_skin_gap_contact.py`,
`test_skin_tiles.py`, `test_topology.py`, `test_deformation*.py` and Blender tests for
draft skin, topology, QuadWild and final deformation. Their assertions require review
against current result/warning policy before being ported unchanged.

Local fixtures discovered, not yet qualified for this release:

- `E:/development/WIP_models/skull_muscles_skin_test.blend` and related sparse-topology cases.
- `E:/development/WIP_models/draft_skin_gap_controls/preferred_gap_wrap_fine/capture.npz`.
- `E:/development/WIP_models/draft_skin_gap_controls/local_digits_20261010/` captures.
- The existing 96-muscle standalone assembly and paired Blender source recorded by
  the shortcut-parity work. Match identities and units before comparisons.

## External references checked

- [QuadWild-BiMDF source and command-line interface](https://github.com/cgg-bern/quadwild-bimdf)
  and [release usage](https://github.com/cgg-bern/quadwild-bimdf/blob/main/README_release.md).
  The addon's pinned version/configuration and native guidance remain the reference;
  upstream availability alone does not qualify a replacement.
- [Instant Meshes native entry point](https://github.com/wjakob/instant-meshes/blob/master/src/main.cpp)
  and [license](https://github.com/wjakob/instant-meshes/blob/master/LICENSE.txt).
- [libigl deformation/BBW/FAST tutorial](https://libigl.github.io/tutorial/).
- [Dem Bones source and native interface](https://github.com/electronicarts/dem-bones).
  Reuse the maintained addon adapter/fitter, not upstream rigid decomposition alone;
  the addon's scale-aware extension and strategy restrictions matter.
- [Qt navigation controls](https://doc.qt.io/qt-6/qtquickcontrols-navigation.html).
  The confirmed vertical strip requires presentation composition; Qt TabBar's position
  setting is header/footer and is not a vertical-orientation setting.
- [Blender remeshing](https://docs.blender.org/manual/en/5.0/modeling/modifiers/generate/remesh.html).
  Generic remeshing is not the addon's collagen, protected-gap and guided-topology pipeline.
