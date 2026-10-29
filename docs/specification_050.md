# AnthroForge 0.5.0 — Muscle Paint

**Status: Confirmed product requirements — not implemented.**
Consolidated 2026-10-29 from the Muscle Paint interview through Q45. This document
defines behavior, not a qualified reconstruction algorithm or implementation plan.
No package version, project schema or existing computation changes with this delivery.
Research and experimental algorithm choices must remain distinguishable from this contract.

## 1. Outcome and existing contracts

Users paint an intended muscle base over SCPs and gaps, then explicitly generate an
editable Membrane made from attached Fibers. The result uses the existing
[Curve/Fiber/Surface contract](specification_020.md),
[Membrane and tissue contract](specification_022.md), attachment services and branch
semantics. A branch means an actual existing surface branch, not another name for a
stroke bundle. Painting does not create a Tissue automatically.

The generated Fibers initially preserve the fitted painted shape using an authored
curve engine. Generation does not run ROUTED automatically. Subsequent parent changes
use ordinary attachment propagation; switching to ROUTED remains a separate explicit
engine choice. No new attachment, routing, inflation or collision-repair behavior is
implicitly authorized by this feature.

The workflow must be available through shared application operations and desktop tools.
Follow the [engineering guidelines](engineering_guidelines.md): native numerical work,
existing transactions/coordinator/resource ownership, concise UI and functions of at
most 15 physical lines. Algorithms, command names and numerical defaults require later
design and qualification; this specification does not declare them implemented.

## 2. Painting and fiber direction

Two brush modes share one painting:

- **Directional:** stroke travel defines fiber flow; brush width establishes coverage.
- **Perimeter:** painting adds coverage and erasing removes it without replacing the
  established flow. This refines an area; users need not trace a closed outline.

Brush width is a physical model distance, independent of zoom, and adjustable during
painting. The active painting/membrane is clearly identified; only one is edited at a time.

The first directional stroke establishes the main part. Further strokes extend that
part, merge with compatible strokes, or form branches. Touching/overlapping strokes
merge when they belong to the same physical sheet and their local directions align.
Opposite drawing directions A→B and B→A count as aligned. Screen overlap alone is
insufficient. Crossing directions remain distinct; **Keep Separate** overrides merging.
Merging preserves the ability to undo each original stroke individually.

An existing directional stroke can be selected and its direction redrawn while
retaining perimeter refinements. Redrawing interior flow preserves the attachment
strips; relocating attachment regions is deliberate. Perimeter edits at a start/end
can trim or widen its attachment strip and show the resulting attachment proposals.

## 3. Branches and closed paths

A stroke starting inside the main area and leaving it, or the reverse gesture, can
propose a branch connection at the main boundary. Users need not click an exact
boundary point. Use explicit junction identities and the existing root constraints.
Ambiguous proposals, such as crossing the entire main area or meeting multiple roots,
are highlighted for direct viewport choice before generation.

Keep existing restrictions: no nested branches, no closed branching and no overlapping
root intervals. Closed **unbranched** strokes/loops are supported through explicit
closure. Crossing the start of a stroke does not silently close it.

Disconnected strokes block both Generate and Update. Do not silently omit strokes,
create separate membranes, reinterpret unsupported topology or publish a mismatching
shape. Unsupported regions and ambiguous connections must remain visible and actionable.

## 4. SCP placement, gaps and depth

Paint lands on visible eligible SCP surfaces. Users can rotate the camera and continue
the same painting. Do not paint through to the back of a thin bone. The default target
set is visible eligible SCPs; users can restrict painting to selected SCPs while other
bones remain visible. Excluding a paint target does not exclude it from collision checks.

A stroke may cross several SCPs and unsupported gaps. Its contacts and drawn course
define the initial shape, not continuous anatomical attachment to every covered bone.
Across gaps, preserve the drawn course with a smooth depth connection between contacts.

While Paint mode is active, each separate unsupported span per branch has one visible
depth control. Holding LMB on it and scrolling the mouse wheel adjusts the whole span's
width smoothly, with supported ends fixed. Use the provisional span's local normal and
display its direction. If a usable normal cannot be determined, explain the unavailable
control instead of choosing an arbitrary direction. One hold-and-scroll gesture is one
undo action. This geometric construction still requires experimental qualification.

### Background-depth threshold

Provide an adjustable maximum depth behind the current painting layer, measured in
model units along the viewing direction. The first valid contact establishes the layer.
Follow a continuously curving support, but treat a sudden drop to a background bone
visible through a gap as unsupported rather than painting into the gap.

Apply this rule across the entire brush footprint in both modes, not just its center.
Zoom must not change the physical threshold. Changes affect subsequent paint only;
previously captured strokes retain their positions.

A configurable modifier temporarily overrides the depth threshold and highlights the
proposed target. Release restores the threshold. The override still respects the chosen
target restrictions. A default threshold and an event-rate-independent layer-following
rule remain to be designed and tested; no value or heuristic is approved here.

## 5. Attachment regions

For open strokes, start/end regions define attachment **strips**, with generated Fiber
endpoints distributed across them. A strip may span multiple SCPs; each endpoint binds
to its appropriate surface. Do not force the whole strip onto one bone.

Show proposed locations and targets and permit region adjustments. A missing valid end
support leaves the painting unfinished; do not attach it to a distant bone. Branch roots
use the existing shared-junction behavior. For a closed loop, the starting cross-section
provides the default binding region; users may move it or add regions. Do not attach the
whole loop to all covered surfaces.

Use the existing confirmed exterior-placement and retained-material-binding policies.
Preview contacts and confirmed bindings remain distinct. Preserve current source roles,
edit restrictions, attachment offsets and transaction semantics.

## 6. Generate, update and undo

**Generate Membrane** creates the initial result; **Update Membrane** changes an existing
one. Both are explicit actions. Strokes only edit the paint draft until that action;
they do not repeatedly rebuild document construction. Do not add a mandatory separate
Preview/Accept stage.

Each Generate or Update is one undo action:

- Undo Generate removes the Membrane and Fibers created by that generation, without
  removing pre-existing construction.
- Undo Update restores the preceding generated construction.
- Neither operation undoes painting or clears stroke history. After undoing generation,
  users can still undo individual strokes one by one.
- Individual paint strokes and depth gestures remain undoable.

Failure retains the preceding valid output. Keep the attempted result and its diagnostics
available for understanding a failed fit, clearly distinct from published geometry.
Use the existing coherent undo/lifecycle infrastructure; these requirements do not
authorize competing histories or publication outside the coordinator.

## 7. Temporary paintings and their lifetime

Provide a named **Paintings** list inside the tool, separate from scene objects. It
includes unfinished drafts and drafts whose generated result was undone. Users can
switch between paintings during the document session; selecting an associated Membrane
can return to its painting. Only one painting is active.

Paint definitions are temporary and are **not saved in project files**. Generated
Fibers/Membranes save normally. Do not introduce an extra warning about losing temporary
or unapplied paint on document close/switch; retain ordinary unsaved-project behavior.

| Event | Painting behavior |
| --- | --- |
| Shape/topology edit to a painted-on SCP | Discard the affected painting. |
| Relative movement of painted supports | Discard the affected painting. |
| Common rigid movement of the complete painted assembly | Preserve and move the painting coherently. |
| Unrelated SCP edit; names, colors or visibility changes | Preserve painting. |
| Manual construction/geometry/binding edit of generated Fibers or Membrane through ordinary tools | Discard its painting; keep the ordinary edit. |
| Explicit ordinary deletion of the generated Membrane | Discard its painting; preserve normal source-curve deletion semantics. |
| Undo Generate | Preserve painting and stroke history; remove newly generated construction. |
| Successful Create Tissue from the Membrane | Discard its painting in 0.5.0. |
| Explicit paint discard, document close or document switch | End the corresponding temporary painting. |

Discarding paint does not delete otherwise retained generated construction or stop its
ordinary attachment propagation. Undoing the source/manual/deletion edit which discarded
paint restores its associated temporary state within that document session. The precise
resource/undo representation belongs to implementation design, not project persistence.

## 8. Approximation quality and findings

Choose a manageable Fiber count automatically, with accuracy controls and an optional
count override. Respect painted coverage, 3D shape including gap depth, directional flow,
narrow extensions and attachment regions. Small hand jitter may be smoothed only within
the requested tolerance.

Keep spatial tolerance in app length units separate from angular fiber-direction
tolerance. Show their mismatches separately. A chosen Fiber budget is not permission to
silently relax either tolerance.

| Finding | Generate/Update behavior |
| --- | --- |
| Requested approximation accuracy not reached | Block; retain prior output and show the best attempted result/mismatch. User refines paint or explicitly relaxes tolerance. |
| Missing required binding, disconnected strokes, unresolved branch ambiguity or unsupported topology | Block with a specific actionable explanation. |
| Bone penetration | Allow generation/update and report an advisory Issue. |

Do not introduce a blanket tissue self-intersection rejection, automatic repair or an
implicit ROUTED solve. A sampled error estimate must be labeled as sampled; the eventual
implementation must not claim a certified maximum without evidence supporting that bound.

## 9. Superseded proposals

| Earlier proposal or possible interpretation | Confirmed behavior |
| --- | --- |
| Rebuild on each stroke release | Explicit Generate/Update only. |
| Paintings stored in project files | Session-only; generated construction persists. |
| Extra close warning for temporary/unapplied paint | No extra warning. Ordinary save behavior remains. |
| Automatically separate disconnected strokes into membranes | Block generation/update until connected or deliberately corrected. |
| Continued repainting after Tissue creation | Creating Tissue discards paint in 0.5.0. |
| Bone penetration blocks generation | Advisory Issue; creation/update allowed. |
| Undo generation also undoes paint | Painting and individual stroke history remain. |
| Painting over a bone continuously glues the whole sheet to it | Contacts establish shape; explicit endpoint strips/loop regions/junctions establish attachments. |
| Any screen overlap implies stroke merging | Same physical sheet and compatible axial flow are required. |

## 10. Research and future implementation acceptance

Research must first inventory the addon's sparse fiber planner and native smooth-base
fitter; qualify their applicability rather than claiming arbitrary painted surfaces are
already solved. See [Muscle Paint research](muscle_paint_050_research.md).

Future implementation evidence must cover open and explicit closed paintings, multi-SCP
attachments, genuine branches, narrow areas, crossing/opposite strokes, camera changes,
thin-bone back faces, gaps with background bones, depth adjustment and target restrictions.
Compare the actual reconstructed loft against the paint in position and direction,
including independent holdout samples and multiple views. Validate generation failure,
warning-only penetration, each undo/discard transition, cancellation and stale inputs.

Desktop and headless results must agree through shared policies. Profile capture,
projection, fitting, validation, publication and retained resources separately. Numerical
success alone does not establish acceptable shapes or interactive latency. Research
benchmarks on unrelated data do not qualify this workflow.
