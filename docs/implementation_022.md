# AnthroForge 0.2.2 implementation plan

Status: in progress; no release completion claimed. Product authority:
[specification](specification_022.md). Recovery: [task record](tasks/unified-tissues-022.md).
Baseline is 0.2.1 at `6f33380`. Apply [engineering guidelines](engineering_guidelines.md).

## Ownership and interfaces

- Core owns immutable TissueVCP, Point, Anchor and Membrane records; typed anatomical
  queries, capabilities, relationship integrity, outputs and material provenance.
- Application operations own shared validation, transactions, copies, deletion,
  rebind, region/field edits and preview acceptance. UI disabling is not enforcement.
- Shared surface providers expose identity, role, frame, geometry, material mapping,
  revisions, readiness and resource ownership to attachments/routing/picking/measurement.
- Native C++ owns preparation, inflation, mesh assembly, constraints, relaxation,
  correspondence, stacking, repeated queries and independent numerical validation.
- Existing coordinator owns all queues, reservations, cancellation and publication.
  Tissue-specific estimation policies must not start independent timers or worker pools.
- Persistence owns schema 4 and atomic revision snapshots; lifetime owners include
  current state, history, checkpoints, jobs and viewport staging/display.
- Desktop owns focused presentation, existing keyboard/tool lifecycle, Ui/Theme,
  native picking, incremental models and staged results. Headless initializes no Qt.

Extend the command catalogue with construction-point/Anchor lifecycle, Membrane
creation, tissue creation/configuration, inflation previews/configuration, fields,
constraints, parts/sides, branches, crops, stacking inspection/configuration and rebind.
Preserve existing primitive-point command meanings. Reuse generic lifecycle operations.
Keep binding, base, intrinsic and final dependencies distinct. A failed stack can
display current intrinsic output while final-surface consumers remain blocked.

## Migration inventory

Paths in this table refer to the Blender addon migration reference, not runtime imports.

| Capability | Production source | Standalone responsibility and evidence |
| --- | --- | --- |
| Inflation/loft preparation | `core/vcp/muscle_numeric*`, `native/fiber_ccd/af_muscle_numeric.hpp` | Native tissue construction; prepared-grid and mode parity, no Python fallback. |
| Section profiles | `core/vcp/muscle_section_profile.py`, native envelope profile | Typed profile strategy; open-loft restriction, coherent direction and zero-depth tests. |
| Parts/sides/branches | `core/vcp/muscle_envelope*`, branched numerical modules | Tissue part policies and native assembly; fixed seams, A/B and branch fixtures. |
| Height smoothing | `native/smoothing`, `core/vcp/muscle_smoothing.py` | Native constrained smoothing; pin/crease/crop/covariance tests. |
| Crop | `core/vcp/muscle_output_domain.py`, domain clipping | Native material-domain clipping; exact base/output mapping, hidden attachment variables. |
| Radial/sweep/shell | `core/visualization/soft_tissue_build.py`, `core/vcp/soft_tissue_*` | Native shape/field preparation as well as solvers; radial/rim/layer fixtures. |
| Static relaxation | `native/fiber_ccd/af_soft_tissue*` | Native geometric/PBD/envelope strategies; pinned backing, volume and iteration-limit tests. |
| Binding/regions | `surface_target`, `attachment_backend`, `soft_tissue_source_goals` | Shared providers and source/target goal adapters; rotation/offset/topology/rebind fixtures. |
| Pair detection/order | `native/fiber_ccd/pair_detection`, `layer_stacking` | Native bounded evidence and relationship policies; automatic/explicit/excluded regions. |
| Vector stacking | `native/fiber_ccd/vector_stacking` | Native adapter over Tissue material domains; providers/chains/constraints/rejection fixtures. |
| Lifecycle/publication | addon surface publication and dependency contracts | Existing standalone coordinator, Issues, ownership, history and staged display. |

Pin source revisions/hashes and compact extracted fixture provenance. Preserve original
.blend files externally; do not commit production anatomy or large binaries. Reuse existing
Eigen/libigl and the addon's pinned PIQP 0.6.4 with notices. Keep production native work
independent of Blender, NumPy iteration, test-only reference code and experiment paths.

### Integrated evidence map

| Boundary | Maintained acceptance entry points |
| --- | --- |
| Model/providers/copies | `test_tissue_contracts`, `test_anchor_operations`, `test_tissue_independence`, material binding and target-region tests |
| Inflation/shape parity | `test_tissue_inflation`, `test_tissue_shapes`, `test_tissue_relaxation_parity`, `test_tissue_presets` |
| Grids/parts/crops | `test_tissue_branches`, `test_tissue_envelopes`, `test_tissue_smoothing`, `test_tissue_crops` plus corresponding workflow tests |
| Stacking | `test_tissue_stacking_native`, `test_tissue_mixed_stacking`, `test_tissue_stack_groups`, `test_tissue_stack_workflow`, `test_tissue_stack_material` |
| Lifecycle/failures | `test_tissue_group_lifecycle`, `test_tissue_relationship_integrity`, `test_publication_frontier`, `test_tissue_relaxation_quality` |
| Desktop editing | `tools/tissue_*_acceptance.py` full QML harnesses; `tools/tissue_*_scene.py` hidden GPU captures |
| Profiling/resources | `test_tissue_material_cache`, `test_tissue_provenance`, `tools/tissue_profile_qualification.py` |
| Executable workflow | `examples/tissues.json`, `tools/tissue_portable.py` through `tools/check_portable.py` |

All test names above refer to `tests/<name>.py`; fixture source hashes and reproduction
tools are recorded in `native/migration/README.md`. Current qualification results and
remaining gates belong to the task record, not to this inventory. The skull scene uses
the existing routing fixture to inspect integration; it is not a reconstruction result.

## Ordered increments

1. Consolidate specification/inventory and update active documentation links.
2. Add typed objects, registry/anatomy queries, schema 4, shared providers and attached
   construction operations. Integrate desktop entry points, workspace and reference rules.
3. Deliver native intrinsic construction: inflation, profiles, parts/sides/branches,
   smoothing/crop, radial/sweep/shell, relaxation, constraints and field editing.
4. Integrate final/base tissue targets, role-aware binding/picking, indirect chains,
   explicit rebind, topology locks, routing and failure retention.
5. Generalize production stacking and relationship editing; qualify relaxed surface
   tissue as both provider and receiver, fixed backing, masks and bounded caches.
6. Complete profiler attribution, examples, documentation, notices and release checks.

Every increment works in the shared API and applicable desktop tools before advancing.
Retain the existing release version until the complete candidate is qualified. Follow
task-branch/checkpoint/push and validated merge practices; never merge partial checkpoints.
Keep every new function within 15 physical lines through meaningful helpers.

## Acceptance matrix

| Area | Required evidence |
| --- | --- |
| Model | Substitution, independent conversions, shared sources, copies, deletion protection; no dummy SCPs. |
| Geometry | Production inflation families, sides, branches, crops, smoothing, radial/rim/layer/pouch and attachment parity; inspect actual shapes. |
| Stacking | Muscle/muscle, tissue/muscle, muscle/tissue, providers/chains, regions, zero inflation, exact backing/attachments and known rejection cases. |
| Relationships | SOURCE/TARGET constraints, base/final roles, indirect anchoring, topology, missing inputs, cycles; no silent rebind/fallback. |
| Lifecycle | Queued/running cancellation, overlaps, stale publication, Manual provenance, workspace changes, undo/redo, historical save, fallback and disposal. |
| Editing | Creation/selection, controls, weights/masks, support drafts, cancellation and coherent undo; inspection causes no changes. |
| Storage | Full schema-4 editable round trips, earlier-format rejection, shared relationships, fields, accepted outputs and startup policy. |
| Performance | Profiler input/preparation/native/publication/picking/model churn, invalidation, cache behavior and retained resources on representative assemblies. |
| Release | Development gate, native/parity, Qt-free headless, offscreen interaction/render, Windows portable checks and separate ownership/coupling review. |

Background/offscreen validation only while the user uses the computer. State rendering
limits and never claim unperformed interactive acceptance. Solver timings alone do not
establish responsiveness or anatomical correctness. Iteration-limit output remains warned.
Deliver one `dist/0.2.2/AnthroForge.dist` and `dist/AnthroForge-0.2.2-source.zip` only after
qualification. Do not replace an in-use distribution or introduce suffixed release folders.
