# Persistent reconstruction work — confirmed 0.4.2 contract

Status: implemented; release qualification in progress. See the evidence section below.

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

## Desktop walkthrough

Open **View → Reconstruction**. The panel can be docked or detached and has six pages.
It uses the current anatomical selection; mirrored instances remain read-only sources.

1. In **Variants**, create an alternative from selected anatomy. Normal curve, tissue,
   shortcut and transform tools now edit that context. External supports are visible but
   pinned. Return to accepted anatomy without applying changes. Save includes committed
   alternative edits. Checkpoint stores a named immutable state; Fork continues one.
2. Use **Compare** to choose accepted or variant stages. The shared camera, Frame all,
   Split/Overlay layouts and mesh section cuts keep views aligned. Refresh deliberately
   captures newer accepted results. Export evidence writes matching image and JSON data.
3. **Review promotion** prepares affected dependencies in isolation. Resolve conflicts or
   explicit rebinds in the review window; inspect retained failures. Apply promotes the
   prepared state in one undo action and stores a previous-accepted checkpoint. Changed
   supports instead use **Refresh supports**, leaving accepted anatomy unchanged.
4. **Catalogue** creates project-local types and assigns selected instances/side/labels.
   Collections group anatomy or regions without changing hierarchy/workspace membership.
5. **Regions** saves selected triangles from the current Base/Final surface in the comparison
   view. Topology/material-domain and source construction must remain compatible; an
   unavailable region requires explicit redefinition. Ordinary pose/deformation keeps its
   material identity. Historical regions retain the original surface resource.
6. **Stages** embeds Original reference or Transferred anatomy from a supported mesh or saved
   project surface. Mesh imports specify units/orientation/placement; project imports retain
   saved world placement, including SCP geometry-origin offsets. Source files are never edited.
7. **Reviews** records independent decisions, comments, reviewer and optional region/evidence.
   Editing inputs marks decisions outdated; it never turns a numerical result into approval.
   **Queue** claims work by anatomical type and records pauses, blockers, approach and
   checkpoints. Open work returns to its context and selection; takeover is explicit.

Project-assembly import is available in accepted anatomy. Import there before creating an
alternative; a variant can still repair its own declared external references. This keeps
project-wide imported catalogue/provenance from being lost inside a scoped editing snapshot.
Anatomy and construction can otherwise be edited/created through their ordinary scoped tools.

Imported references are surfaces: saved Point/Curve stages are not accepted as mesh imports.
Live point bases and fiber paths remain available in comparison. Surface distances/contours
are reported only for mesh pairs; a path display does not imply a surface correspondence.
Section cuts apply to mesh layers. A reference label records user-supplied stage semantics;
the application does not verify that an imported mesh is an anatomical original.

## Ownership and coupling review

- **Context isolation:** `editing_contexts` owns switching, history projection and callback
  scope. It does not create another Session/executor. Scheduler context namespaces prevent
  identical entity IDs in alternatives from sharing write reservations incorrectly.
- **Editing policies:** `variant_policy` and shared capabilities enforce pinned support and
  workspace restrictions for desktop/API callers. UI disabling is their presentation.
- **Promotion:** typed reconciliation owns accepted-versus-variant conflicts; existing
  replacement/candidate services own dependencies, placements, failure review and adoption.
  Retained accepted formula authority is declared separately and included in read validation.
- **Evidence:** immutable stage/review records and resource reachability own persistence.
  Region availability verifies source lineage as well as material-domain topology. Stage
  comparison uses native connectivity and construction lineage before reporting displacement.
- **Presentation:** reconstruction controllers/models expose shared operations; native batches
  compute bounds and region outlines. Frozen resources feed the existing staged scene/capture
  path. Numerical kernels are not duplicated in Python or in the review queue.

Remaining costs are explicit: each retained scene has authored metadata and references;
unchanged resource payloads are shared. Keeping many changed/checkpoint results increases
memory and package size. Export freezes the project snapshot needed for consistent capture.
There is no multi-user server locking or automatic reconstruction worker behind the queue.

## Qualification evidence

Fixture: the saved 59-SCP/96-authored-muscle assembly, SHA256
`308c216c85d9458d83e163bc3ed2ab85338bccd3adeb496981ffe35ec8275dac`.
Source bytes stayed unchanged. SCM inflation was edited in an alternative, promoted, undone,
saved/reopened, then exercised with **Ribs Top Radius = 3**, explicit support refresh and a
second promotion. Prepared/committed geometry and retained bindings matched exactly;
the shortcut result matched the accepted-only control run.

| Single local trial | Time |
| --- | ---: |
| Initial project load | 5.705 s |
| Create alternative | 0.105 s |
| Inflation edit and evaluation | 0.346 s |
| Prepare first promotion | 1.152 s |
| Apply first promotion | 0.0067 s |
| Save / reopen | 12.828 / 10.746 s |
| Explicit support refresh | 1.660 s |
| Prepare second promotion / Apply | 1.003 / 0.0072 s |

Observed peak working set was about 3.04 GB initially and 4.20 GB with multiple retained
snapshots during follow-up. These are single workflow measurements, not a controlled speedup
claim. `.afprofile.zip` reports and machine-readable comparisons are under ignored
`build/reconstruction-042/production` and `followup`.

Twelve hidden GPU captures cover Original/Base, Transferred/Final, Rest/Final and Fibers/Base
from front, oblique and side. Visual inspection verified framing, isolated source fibers,
aligned matching surfaces and readable controls. Populated panels were also captured at
360 px width and heights 400/700/960 with no QML warnings. An initial fibers view incorrectly
included support-bone guides; required-construction traversal corrected it, with a regression.
Hidden-render evidence does not establish interactive mouse/keyboard usability acceptance.

Full gate and relocated portable results will be recorded before release delivery.
