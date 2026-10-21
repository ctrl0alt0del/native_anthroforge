# Editable SCP migration: Shrinkwrap and Segment Chain

- Task branch: `codex/scp-migration-construction`
- Integration branch: `main`
- Starting revision: `bfe419c79e8ff3e8cba2c12c83daf538020d7151`
- Runtime checkpoint: `4812965f341b3815e17958a7dc5f7dca12a9ea78` (pushed)
- Status: complete; validated for integration
- Last updated: 2026-10-21, Europe/Bucharest
- Active writer: desktop migration chat, direct work

## Authorized outcome

Implement live Shrinkwrap and a generic parameter-driven Segment Chain in the desktop
and headless app, then migrate the 33 approved SCPs and 26 independent counterparts
from the one source file. Atlas v002 is approved. No silent imported-final fallback.
Preserve curves, hooks, lattices, hierarchy, placements and source colors. Keep numerical
work native, use shared operations/policies, and retain the 15-physical-line function limit.
Validation remains background-only. No muscles, fibers or discovery regions are migrated.

## Delivered construction

- Shrinkwrap has explicit target surface roles, offsets, four nearest-surface snap modes,
  weights, undo, dependency tracking, persistence and focused inspector controls.
- Segment Chain exposes lengths, radii, spread, bend, profile and sampling controls.
  Adjacent-pair bending reproduces the saved source graph; cumulative bending is explicit.
  Zero-length segments are disabled. Exact exterior union retains triangle material
  identity across changing output triangulation; covered bindings fail rather than rebind.
- Simple subdivision and local displacement are ordered modifiers. Body pieces support
  pre-bend subdivision. Fixed-length bodies retain caps on cyclic guides.
- Shared validation blocks unstable generated-vertex membership on Segment Chain,
  including thickness fields. Whole-target deformers and weighted cage controls remain.
- Migrated assembly: 10 bodies, one loft, 20 Segment Chains, 27 explicitly approved
  imported/raw source meshes and one grouping SCP; 31 controls and 11 curves.
- Spine is the approved rounded capsule. Pubis/Ischium/Ilium share authored pelvic guides
  through independent consumer frames. Ilium uses a fitted editable BASE cage. Ribs use
  loft plus lattice/hooks. Scapulae retain raw plate, subdivision, live wrap to Ribs,
  local displacement and thickness. Acromion/Clavicle retain their shared Hook.

## Observed defects and owning fixes

Source comparison exposed reversed Segment Chain side winding relative to caps, which
made the Boolean exterior discard segments. Corrected source-compatible topology and
added directed-edge/volume/reference tests. Fixed-length body closure was corrected at
the shared construction policy. Earlier coarse/native-n-gon Ilium cage fits were rejected;
the final cage uses captured Blender pre-bend surfaces and native batched projection.

Full assembly evaluation stalled with 52 queued jobs despite an acyclic output graph.
Contracting all pose work into one batch caused an artificial wait cycle. Pose batches now
split at intervening non-pose dependency stages; direct pose chains remain batched. The
existing coordinator still owns reservations, dispatch, cancellation and publication.

Actual QML inspection caught typed parameter values missing from visible fields. The
shared Qt value adapter now converts identity-free value records recursively, preserving
incremental identity-bearing projections. Tests verify visible fields and resulting edits.

## Evidence and limits

- Blender 5.0.1 Shrinkwrap parity: 24 weighted/transform/offset cases; compact Segment
  Chain and Simple-subdivision fixtures preserve provenance. C++ numerical work only.
- Final development gate passes: 1,647 pytest tests, five native CTests, 319 typed
  modules, lint/format, native/script limits and numerical/runtime checks. Evidence:
  `build/migration-gate-delivery.log`. Existing Qt deprecation warnings remain.
- Actual offscreen QML creation/settings tests pass with no warnings. Visible fields,
  selected segment editing and Shrinkwrap offset editing were inspected. Hidden Windows
  GPU captures show the complete assembly; no physical desktop interaction is claimed.
- All 59 entries evaluate with anatomical attachments enabled; binding capture changes
  placement by at most 3.4e-7 scene units. Shared Hook edits update both consumers;
  digit edits preserve independent counterparts. Undo and exact save/reopen pass.
- Startup attachment recalculation completes without errors; two-way surface deviation
  from saved geometry is below 1e-12. Headless verification imports neither Qt nor Blender.
- Packaged full assembly opens, edits a chain, undoes, explicitly evaluates, saves, reopens
  and renders all 59 entries. Hidden capture has 60 chunks and 313,776 render vertices.
  The full minimal-PATH portable suite passes, including the new construction example.
  Evidence: `build/migration-portable.log` and `build/migration-portable/portable-check.json`.
- All ten digits and their counterparts match source surface samples within about 2e-6.
  Static/raw caged source meshes agree around 1e-6. Approved rounded spine and connected
  rib seams differ intentionally. Rib max/mean: 0.12168/0.01210; live Scapula max/mean:
  0.09459/0.01854. Ilium max/mean/p95: 0.01143/0.000394/0.002249, diagonal 4.77.
  These are vertex-to-opposite-surface samples, not continuous Hausdorff guarantees.
- Original/counterpart comparison images were inspected. Ilium retains its broad rim and
  underside. Native linear subdivision is qualified for these quad stages, not arbitrary
  higher-level nonplanar n-gon Blender parity. No exact Scapula parity is claimed because
  its live target intentionally differs at rib seams.

Separate ownership/coupling review confirms typed core definitions, explicit surface
relationships, shared command validation, native batched geometry/provenance, ordinary
resource leases, existing coordinated execution and desktop-only value adaptation.
No dummy controls, Blender runtime, competing workers or Python numerical fallback.
Computation changes and rejected approaches are in CH-027-030.

## Deliverables and recovery inputs

Source directory:
`E:/development/WIP_models/muscle_reconstruction_workflow/runs/2026-10-13-serratus-anterior-partial-manual-16c4eea4/`.

Source: `serratus_anterior_partial_v001.blend`, unchanged SHA256
`fb199c4f466cb06380e3596d7f83e715dd72abf71b154d703818d4df75832acd`.
Approved atlas: adjacent `scp_migration_atlas_v002/`; detailed source inspection and
captured evaluated assets: `scp_migration_atlas_v001/`.

Final project: `scp_migration_v001/serratus_skeleton_native_v001.anthroforge`.
SHA256: `9fc53f5190a45bd82f588ff1a8060f93a7074d5687b7d3537848c5d5638047c4`.
`comparison.html` provides all source/native front and side views and explicit differences.
`comparison.json`, `qualification.json`, `final-audit.json`, `startup-comparison.json`
and `packaged-assembly-front.png` hold the local-only evidence. One-off extraction,
build, fitting and qualification scripts remain in that external directory; all functions
are within 15 lines. `candidate.anthroforge` is a superseded intermediate, not delivery.

Canonical package: `dist/0.2.3/AnthroForge.dist/AnthroForge.exe` (runtime 4812965).
SHA256: `B57E56BE0BFEC365B6DEC12D0D5CF9291CF88A580C5605F9D753730E10E2384A`.
One companion archive: `dist/AnthroForge-0.2.3-source.zip`, refreshed with final docs.
Preserve unrelated root `__init__.py`. Latest fetched `origin/main` remains the starting
revision; integrate normally without rewriting checkpoint history. No open design
questions or required implementation work remain. Do not claim physical desktop acceptance.
The region-discovery skill records the new topology identity boundary; legacy region
indices were not transferred. This personal skill update and anatomy assets are local-only.
