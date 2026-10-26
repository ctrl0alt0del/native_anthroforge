# AnthroForge 0.4.0 — Implementation and acceptance

Status: **Confirmed; implementation in progress, not release-qualified**.

Implement [the specification](specification_040.md) under the
[engineering guidelines](engineering_guidelines.md). The [source inventory](skin_040_inventory.md)
records algorithms/defaults, source provenance and evidence limits. Continue
`codex/skin-040`; preserve unrelated files and source `.blend` assets. All testing is background-only.

## Ownership

| Owner | Responsibility |
| --- | --- |
| Core | Immutable skin settings/results, contributor settings, guides, reference identity and independent fitted results. No dummy anatomy nodes. |
| Application | Shared operations, contributor capture, invalidation, transactions, reference compatibility, persistence, export policy and publication. |
| Native C++ | Raster/field/distance work, meshing preparation, guides/refinement, tetrahedral preparation, LE/FAST, fitting and preview skinning. |
| Desktop | Vertical inspector, contextual controls/painting, fit preview and diagnostics through shared APIs. |
| Export adapters | OBJ writer over a frozen skin snapshot; shared eligibility/units/atomic-write policy above writers. |

Extend the existing coordinator with task policies for envelope, topology, reference, deformation,
sampling and fitting. Keep dispatch capture, complete revision validation, reservations,
cancellation, stale rejection, Manual provenance, workspace priorities and save checkpoints.
External processes are coordinator-owned with process-tree cancellation and resource-aware
admission. Normal production runs have no arbitrary time or fixed per-job memory cutoff;
bounded retained logs never terminate computation. Preserve source numerical thread settings
and account for them in scheduling. Explicit test limits remain separate from production policy.

The approved correction uses pinned Blender 5.0.1 Decimate and the needed BMesh subset,
replacing the approximate libigl collapse traversal and custom half clipping. Preserve source
topology behavior, including degenerate outputs, until a separate change is approved. Accepted
departures and their qualification requirements are recorded in the specification/task record.
If the agreed approach needs replacement or a new algorithm change, stop implementation and
discuss the concrete blocker and alternative with the user before proceeding.

Keep authored inputs, accepted stage results and presentation distinct. Resource leases include
current state/history/checkpoints/jobs/viewport. Settings changes invalidate construction;
compatible source motion invalidates deformation. Persist the reference, not prepared caches.

## Integrated increments

1. **Qualification:** freeze native/source fingerprints, paired fixtures and expected warnings;
   qualify matching-runtime topology/tetrahedral/fitting dependencies before pipeline integration.
2. **Foundations:** typed skin state, reference/resource contracts, schema-7 reader/writer retaining
   4–6, shared commands/capabilities and vertical inspector. Test old project preservation.
3. **Envelope:** native numerical preparation and maintained kernels; contributor capture,
   collagen/gap controls and painting, scheduling, staged display and quality diagnostics.
4. **Topology:** explicit QuadWild/Instant Meshes, loop/FLOW guides, density, symmetry, native
   assembly/refinement and usable-result warnings. Inspect actual output shapes.
5. **Deformation:** durable reference, LE/FAST, contact diagnostics, compatibility/invalidation,
   atomic replacement and failure retention through desktop/headless operations.
6. **Fitting:** isolated shortcut sampling, maintained scale-aware/authoring-only Single Active
   fitting, stable sample identities, independent preview, stale provenance and persistence.
7. **Export/release:** OBJ, examples, regression/parity/performance evidence, portable delivery.

Each increment includes shared API and desktop entry points before advancing. No public command
may depend on viewport selection. Extend command families for skin inspection/configuration,
contributors/paint/guides/budgets, build/update/reinitialize, fit/preview/remove and export.

## Qualification

- Source manifests distinguish clean tracked addon code from local untracked fitting work.
  Keep upstream licenses/configurations. Do not reuse CPython-3.11 extensions in Python 3.12.
- Match units and identities in paired skin/skull/digit and 96-muscle fixtures. Verify envelope,
  gaps, collagen, loop patches, branched charts, density and symmetry numerically and visually.
- Preserve connectivity/IDs through large shortcut updates and open-contact-open sequences.
  Test incompatible contributors and reference preparation/rebuild failures.
- Check actual fitted playback at held-out/intermediate values, clamping, policy-aware sampling,
  determinism, source preservation and no anatomy evaluation during preview.
- Exercise queued/running edits, cancellation, obsolete publication, Manual inputs, undo/redo,
  failed replacements, historical saving and resource disposal.
- Round-trip schema 7; load 4–6 without changing existing results. Restore without blanket work.
  Round-trip OBJ quads and test all stale-export policies with edits during export.
- Profile capture, native stages, publication, UI and retained resources on production anatomy;
  distinguish kernel timings from whole-app responsiveness.
- Run development/native/parity, Qt-free headless, offscreen interaction and relocated portable
  checks. Review ownership/coupling separately. Offscreen evidence is not interactive acceptance.

## Delivery

Keep Python 3.12, C++17, Qt/PySide 6.12.0 and 15-line authored functions. Record computation
changes with baseline/candidate evidence in computation history. Push coherent checkpoints with
recovery notes; incomplete checkpoints stay off main. Advance versions only after the full
workflow qualifies. Produce one `dist/0.4.0/AnthroForge.dist` and companion source archive.
