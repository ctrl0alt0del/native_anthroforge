# Whole-skeleton updates — 0.4.2

Status: **Confirmed contract; implementation in progress.** This document does not claim
qualification. [Task and evidence](tasks/skeleton-update-042.md).

## Product contract

**File → Update Skeleton from Project…** prepares an independent candidate from a pinned
saved AnthroForge project. Apply adopts the reviewed candidate as one undo action.

- Match SCPs one-to-one through verified identity/provenance or explicit selection.
  Names support search only. Ambiguous candidates remain unselected.
- Adopt replacement construction and world placement; preserve destination identity,
  names, hierarchy, presentation, update modes and mirror rules.
- Retain unmatched destination definitions; normal attachment propagation still applies.
  Add unmatched source bones only explicitly, with a destination parent.
- Copy required curves, controls, deformers, junctions and resources once. Preserve
  unrelated consumers and retain superseded standalone construction.
- Do not import source tissues, skin, workspaces, history or active calculations.
  No fitting, split/merge, source modification or ongoing synchronization.

## Attachments, controls and results

Separate placement, construction, verified deformation, incompatible topology and additions.
Counts/names do not establish material correspondence. Preserve compatible material bindings.
To preserve replacement bone poses, review necessary bone-to-bone recapture while keeping
parents/settings. Review incompatible face/vertex locks explicitly.

Incompatible Fiber/Anchor/constraint bindings require explicit Rebind. Propose capture using
replacement geometry in the old bone frame, then use ordinary propagation into the replacement
pose. Show before/proposed locations and allow surface-placement correction. Never change
surface roles or support objects implicitly. Numerical algorithms remain unchanged.

Keep destination shortcuts/drivers with verified property remapping. Missing properties,
incompatible types, conflicting writers or outputs that overwrite replacement values require
explicit decisions. No formula inversion or silent disabling. Required source construction
drivers do not imply copying unrelated shortcut UI.

Evaluate all affected construction/fibers/tissues once, including Manual, while preserving
their future update modes. New dependent failures require acknowledgment, retain accepted
geometry and produce Issues. Invalid skeletons, unresolved required relationships and
unreviewed destructive changes block Apply. Show retained output distinctly from fresh output.
Always explain skin impact. Optional final-skin preview preserves topology; never automatically
regenerate draft skin, topology or fitted solutions.

## Interaction and architecture

One searchable review window provides mappings, affected objects, synchronized Before/After
and Overlay views, visibility filters, proposed anchors and comparison evidence. Changing
choices prepares automatically; stable progress/footer, no mandatory Preview/Accept sequence.
Cancel releases work. Existing geometry checks remain on demand.

Core owns typed matches/changes/decisions. Application owns policies, graph copying, isolated
evaluation and atomic adoption. C++ owns numerical transforms/capture/comparison and existing
evaluators. Desktop presents shared operations through existing UI, keyboard and picking.

Reuse assembly source snapshots/selective resources and replacement candidates. Candidate
evaluation has its own immutable document/resource state, but uses the existing coordinator
and worker pool. Complete read validation includes automatic dependency membership. Relevant
edits obsolete candidates; unrelated edits can survive. No live-document preview mutation.
At Apply coordinate writers and publish prepared results without unnecessary reevaluation.

Planned API: `skeleton_update.inspect`, `.prepare`, `.status`, `.cancel`, `.apply`.
Desktop and Qt-free headless clients share policy/transactions; status supports waiting.
Keep schema 8 using ordinary records and existing provenance; sessions/previews are transient.

## Delivery and acceptance

1. Contracts, source inventory/matches and graph replacement with contract tests.
2. Shared API and desktop matching, resource/identity/reference fidelity.
3. Reviewed bindings/properties and isolated dependent evaluation.
4. Comparison, anchor correction, skin option and atomic commit/cancel/undo.
5. Full gate, profiler, actual offscreen geometry and portable qualification.

Cover unchanged/pose/deformation/remesh inputs (including reordered equal-size meshes),
ambiguous matches, shared construction, mirrors, attachments, shortcuts, crops, stacking,
Manual results, failures, cancellation, concurrent edits, historical saves and resource release.
Use the 96-muscle assembly for compatible and topology-changing replacements, preview/commit
parity and subsequent shortcut edits. Verify source hashes and source-independent reopening.
Measure preparation/native work/publication/model changes/memory and cancellation; inspect
actual shapes and state limits of offscreen evidence. Preserve the single canonical 0.4.2
distribution/source archive. Functions remain at most 15 physical lines; separate coupling review.
