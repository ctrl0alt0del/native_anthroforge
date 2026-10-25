# AnthroForge 0.3.6 — Audited authoring workflows

Status: source integration verified; portable qualification in progress.
This release integrates the preserved `codex/parity-workflows-034` branch with current
mirroring and Smooth Shape Preservation. There was no separate packaged 0.3.4 release.
Schema 6 remains current and reads schemas 4/5/6 without blanket recomputation.

## Editing workflows

| Task | Desktop entry point and behavior |
| --- | --- |
| Fiber deformation supports | Fiber inspector: automatic supports plus searchable explicit inclusions/exclusions. Anatomical pin targets remain required. These controls do not select routing obstacles. |
| Fiber pin editing | Bound-point Normal Offset uses the retained material normal. Rebind All keeps current shape and targets. Check Pins opens advisory Issues and explicitly reviewed repairs. |
| Routing | ROUTED settings expose Length Weight, solver trials per checkpoint and Use Warm Start. Recalculate from planner explicitly requests a cold route while retaining accepted geometry until completion. |
| Connected body split | Select interior guide points on a one-guide open body and use Split. The first SCP and its children keep their identities; other pieces become siblings joined by shared Hooks. |
| Imported mesh replacement | Replace Mesh selects a new source. Compatible correspondence applies directly; lost bindings/indexed settings require a concrete review. A stale review cannot apply. |
| Tissue source replacement | Tissue source chooser assesses an Anchor, Fiber or Membrane. Compatible settings remain; required mode changes, discarded fields or rebindings are reviewed before one transaction. |
| Existing tissue defaults | Apply Preset resets preset-owned inflation/relaxation/constraints. Custom fields/regions, construction and relationship settings remain. Unsupported combinations reject explicitly. |
| Surface-click Fiber creation | Fiber placement toolbar: click anatomical surfaces; Shift-click continues, plain click after the first finishes. First publication is bound and routed, with one undo and no orphan Curve. |
| Fiber thickness | Display Radius in the Fiber inspector is saved per workspace in world units. Zero uses the centerline. It never changes numerical clearance or authored geometry. |
| Surface source selection | Select Sources selects the ordered source curves/Fibers without an authored edit. |

The shared [authoring API](authoring_api.md) exposes the same policies and lifecycle.
Read-only mirrored geometry remains uneditable. Mirrors share accepted source tubes,
including Mirror only display and hidden sources; picking uses their displayed revisions.
Propagation Preferences still affect future calculations only. Cold routing and explicit
support/pin edits work with both propagation methods.

## Attachment corrections and known differences

Owner backsolve retains the original material anchor across Boolean topology changes,
instead of rereading a potentially recycled face index. Migration utilities capture
effective legacy Backsolve settings. Existing user projects are not rewritten; source
polygon-anchor/policy migration remains a separate explicit operation.

Keep the accepted welded Ribs. Their seam/thickness response differs from Blender's
separate strips, and this release does not claim exact shoulder equivalence. The shared
Hook still joins the curves. Historical source evidence and Thumb measurements remain
in [parity findings](addon_parity_findings.md) and the [preserved task](tasks/parity-workflows-034.md).

## Qualification

The combined development gate passes 2,220 Python tests, five CTests, configured style,
typing and numerical checks. Additional review/mirror regressions are undergoing the
final aggregate rerun. Background QML tools cover all restored desktop entry points.
Actual hidden GPU images verify radius changes and source/mirror geometry, with matching
native picks; this does not establish physical interactive desktop acceptance.

The 96-muscle/326-Fiber fixture passes Ribs Top Radius 3 under both propagation methods,
including undo, redo and reopen. The display profile includes 326 jobs and 326 native
tube spans, retaining exact source buffers, attachment records and undo. A single run
measured 359 ms preparation, 768 ms work and 60 ms CPU staging under uncontrolled load;
these are neither frame latency nor a speedup claim. Raw reports remain local under
`build/workflows-036`; the [task record](tasks/workflows-036.md) tracks final evidence.

Final delivery is one `dist/0.3.6/AnthroForge.dist` and one
`dist/AnthroForge-0.3.6-source.zip` after portable qualification.
