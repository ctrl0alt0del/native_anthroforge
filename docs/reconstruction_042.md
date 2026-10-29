# Persistent reconstruction work — confirmed 0.4.2 contract

Status: confirmed; implementation in progress. Qualification is not yet claimed.

## Product contract

Selected-anatomy variants retain their construction and pinned external support baseline.
Normal tools edit an isolated variant; accepted anatomy changes only through explicit
promotion. Copy shared construction independently from outside consumers, preserving sharing
within the variant. Persist committed edits automatically with project saves/autosaves.
Named checkpoints are immutable; continuing one forks an editable variant. Inactive variants
do not recalculate. Changed accepted supports mark variants outdated; Refresh supports is
explicit and uses existing correspondence, placement and rebind policies.

Promotion reviews conflicting accepted edits, bindings and all affected dependents including
Manual objects, without changing their update modes. Required invalid relationships block it;
new dependent failures require acknowledgment. Reviews remain advisory. One promotion/undo
preserves destination identities and unrelated state, and retains the previous accepted
anatomy as a checkpoint. Skin compatibility is reported; compatible final-skin preview is
optional. No automatic draft/topology generation, fitting, transfer or anatomical algorithm
changes are authorized.

Project-local user-defined anatomical types have explicit instance assignments, side and
optional instance labels. Names suggest but never establish identity. Existing read-only
mirrors retain source relationships. Named object collections and surface/material regions
support review. Unverified topology changes make regions unavailable until explicitly
redefined; no nearest-face reassignment.

Separate anatomy, route/collision, attachment, stacking, persistence and display reviews.
Each decision (Pending/Approved/Rejected/Not applicable) refers to an exact stage/input
signature, reviewer, comments and evidence. Freshness is independent; computation never
grants anatomical approval. Keep historical decisions after relevant changes.

The resumable queue records owner, status, next action, blocker, approach and checkpoint.
Claim next skips already-owned anatomical types; takeover is explicit. Pause/Resume/Block/
Complete organize human/API work, not automatic reconstruction. Ownership is protected by
the project writer lock, not a cross-computer coordination service.

Original-reference and transferred stages import supported meshes or saved project results
with explicit units/orientation/placement and immutable embedded geometry/provenance. They
are comparison records, not dummy SCPs or numerical supports. Compare these and existing
base/fibers/rest/intrinsic/final stages with shared camera, overlay/split views, sections and
inspection exports. Material displacement requires verified correspondence; geometric
distance remains distinctly labeled. No automatic fitting or anatomical transfer.

## Ownership and delivery

Core owns immutable context/checkpoint/catalogue/region/review/queue/stage records. Application
owns scoped commands, isolated evaluation, refresh/reconciliation, promotion and persistence.
C++ owns numerical queries/evaluation. Desktop adds a dockable Reconstruction panel, using
normal tools and shared comparison presentation. One coordinator/worker pool serves explicit
context-scoped reads, reservations and publication; no second Session per variant.

Share immutable resources and persist non-recursive snapshots. Schema 9 reads schemas 4–8;
new records initialize empty without recalculation. Serialize committed states, never native
handles, active jobs or undo histories. Anatomy import carries applicable catalogue/stage/
region/evidence metadata; variant inclusion is explicit and identity mapping is provenance-
based. Changed inputs invalidate review freshness.

Shared operation families: variant.*, catalogue.*, review.*, reconstruction.queue.* and
reconstruction.stage.*. Desktop/headless clients use identical policies and cancellable jobs.

Delivery order: contracts/persistence; editable variants and desktop navigation; refresh and
promotion; catalogue/regions/review/queue; stage comparisons and release qualification.
Each increment integrates desktop and headless operations. Keep every function within 15
physical lines; preserve unrelated files and task checkpoint/push workflow.

Qualification requires the 96-muscle assembly, multiple alternatives, support refresh,
promotion/undo and subsequent shortcut edits, exact preview/commit geometry and bindings,
context cancellation/concurrent jobs/stale reads, save/reopen/resource ownership, review
freshness, regions, imported stages/units/correspondence, native comparison metrics and actual
multi-angle hidden renders. Profile creation/loading/evaluation/publication/switching/memory.
Run the full development/native/headless/portable gates and separate coupling review.
Deliver one dist/0.4.2/AnthroForge.dist and companion source archive; state interactive limits.

Research: [OpenUSD variant authoring](https://openusd.org/dev/tut_authoring_variants.html)
provides a reference for separate edit targets and shared data, not a new dependency or
authority over AnthroForge's explicit promotion/support policies.
