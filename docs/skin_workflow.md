# Building and deforming skin

Available in 0.4.0. Qualification evidence and limits are in [the task record](tasks/skin-040.md).
The [0.4.1 audit corrections](tasks/release-041.md) restore the reference proxy preparation,
diagnostic reporting, budget feedback and persistent FAST weight cache described below.

Open **Skin** in the vertical inspector tabs on the right. **Update final skin** selects
the saved update target. With the checkbox off, committed SCP/VCP edits automatically
update Draft once required anatomy is ready. Draft does not rebuild during dragging.
With it on, the pipeline first waits for current Draft, then prepares or updates Final.
Compatible subsequent edits move final vertices while keeping Draft and topology fixed.
If Final explicitly requires new Draft or topology, the pipeline builds that prerequisite
automatically. **Build Skin** selects Final and explicitly rebuilds in one undo action.

Activity shows progress; previously accepted geometry remains available. Automatic Draft
jobs cannot be cancelled by the user. The application still invalidates obsolete work after
mode/history changes. **Retry skin update** retries a failed request with its captured
configuration. Failed numerical solves retain accepted output and report their reason.

Only SCP and tissue surfaces contribute physical volume. Curves, Fibers and other
construction do not thicken the envelope. Closed Fiber paths and enabled FLOW guides
can still guide the separate topology stage.

## Shape and topology

Choose **Field envelope** or **AVBD (experimental)**. Selecting a builder immediately
requests Draft construction. Each builder owns its parameters: skin distance, collagen
and gap filling belong to FIELD, and are hidden for AVBD. Other parameter edits remain
pending until an explicit successful rebuild applies them. Automatic anatomy updates use
the last successfully applied configuration. If switching builders fails, later anatomy
updates keep using that applied builder; Retry uses the failed selection.

FIELD envelope settings control skin distance, collagen and gap filling. Distances are
percentages of the model's longest axis. Select an SCP to set or paint its collagen
weights and adjust its subtree quad budget. Select a compatible source to override
its gap settings. Display hiding does not remove physical contributors.
Inherited gap fields show their effective document values. Automatic collagen shows the
resolved value and is read-only; select Uniform to enter a custom scalar. Switching modes
preserves inactive overrides. **Reset defaults** restores all six envelope settings in one
undo action without clearing source settings, paint, topology settings or saved geometry.

Choose QuadWild or Instant Meshes, the target quad count, refinement and symmetry.
QuadWild uses the supported loop and FLOW guides. Change these construction settings,
then explicitly rebuild to apply them. Compatible Final updates preserve topology;
changed contributor/material identities can require reconstruction. The default display
follows Draft/Final mode. Explicit stage selection, hidden skin and fit previews remain
independent presentation choices.

Choose the symmetry axis for the project's actual coordinates; it is not inferred from
anatomical names. The migrated 96-muscle assembly uses Y. The quad count is a target:
guide constraints may require more quads. The preserved remesher may return usable output
with openings or discarded-patch warnings. Inspect those findings before export; completing
Build Skin does not certify a watertight or intersection-free surface.

If a later build stage fails, inspect its Issue and retry the relevant stage. A failed
deformation-reference build retains the new topology for retry while preserving any
previously accepted final skin and reference.

## Deformation

With **Update final skin** selected and a reference available, ordinary anatomical updates move skin vertices while
preserving their identities and connectivity. Live, On Release and Manual update modes
remain available. **Update skin** explicitly evaluates the current anatomy against the
retained reference. A typed incompatibility can request required construction through the
same pipeline; compatible evaluation preserves topology.

Preferences chooses the tissue surface used by new references: **Finished** is the
default and follows cropping, relaxation and stacking; **Inflated rest** uses uncropped
inflation before relaxation and stacking. Both inflated sides contribute. Existing
references retain their captured choice until explicitly rebuilt.

The deformation controls select Linear Elasticity or FAST and their settings. Proxy
resolution changes require reference rebuilding. Explicit material or topology incompatibility
requests the required upstream construction. A failed numerical solve is reported as failure;
it is not treated as permission to reconstruct everything.

New references use the draft envelope reduced with the Blender Decimate subset to about
64,000 triangles, then tetrahedralize it. Final skin topology is retained unchanged. Only
projects without a draft use topology as the proxy source. Existing saved references are
not silently rebuilt. FAST retains checksummed weights under
`%LOCALAPPDATA%/AnthroForge/deformation/anthroforge-bbw-v1`; missing, corrupt or unavailable
cache files cause normal recomputation. This disposable cache is not project data.

**Skin diagnostics** shows retained solver and geometry findings. Issues explains inverted
proxy elements, extrapolated embeddings, contact-motion limits and intersections. Reference
comparisons retain at most 256 intersection witnesses, so an incomplete comparison cannot
prove the absence of new intersections. Sampled nearest-normal clearance is not a complete
skin/anatomy volume penetration check. Diagnostics never repair or reject otherwise usable
skin. The budget list shows achieved exclusive-region quads; deviations above 20% produce
the addon's advisory warning. Opening this panel does not recalculate geometry.

## Fit a shortcut to bones

Select a continuous scalar shortcut and click **Fit to bones…** beside its settings.
Enter a value range, sample count and bone budget. Fitting samples the real shortcut in
an isolated document, including its formulas and attachment policies. Your editable
anatomy stays unchanged. The bone count is a budget, not a guarantee of exact reproduction.

Missing skin or an incompatible reference disables fitting with a tooltip. Unapplied
build settings show a warning when the existing skin/reference is still usable. A failure
within the sampled range stops that fit; it does not substitute an old skin sample.

Saved fits appear in Skin. Select one and vary its preview value to inspect independent
playback without recalculating anatomy. **Fit accuracy** lists training and held-out
errors. Values outside the sampled range clamp to the endpoint. Source changes mark a fit
stale but keep its saved preview usable. Refitting is explicit; removal is undoable.
The summary includes the number of active fitted bones and held-out error in the moving
region, alongside the whole-mesh error. This separates fit accuracy from unaffected anatomy.

## Save and export

Projects retain skin definitions, reference data, requested mode, pending/applied builder
configuration and fitted results. Opening restores saved output without starting calculations.
Schema 10 reads versions 4–10. Legacy Draft without applied provenance remains explicitly
unknown until a successful build; migration does not invent a successful configuration.

Ordinary **`.anthroforge`** files omit construction checkpoints. Extended **`.anthroforgex`**
files additionally retain one eligible checkpoint per SCP and the complete combined VCP
checkpoint. Save preserves the chosen format. AVBD reuses only a complete compatible prefix
of the saved parent-first SCP order followed by VCP order. Changed geometry, ordering,
configuration, normalization or runtime identity invalidates the affected suffix. Checkpoint
resources belong to document/history and are checksummed; transient failed VCP prefixes
are retained only in the current session.

Automatic recovery copies use the ordinary format: accepted results remain recoverable,
but construction checkpoints must be rebuilt. Use an extended project save to retain them.

The Windows portable app includes AVBD's interpreter, numerical dependencies and native
solvers. Launch **AnthroForge.exe** from the complete app folder; no Python installation,
environment variable or separate runtime checkout is needed. Keep the `_runtime/avbd`
folder with the app when moving it. An incomplete bundle reports an error without replacing
accepted Draft. AVBD remains experimental and retains its NVIDIA GPU/driver requirements.
Source development can still select a qualified runtime with `ANTHROFORGE_AVBD_RUNTIME`;
packaged applications ignore that override. FIELD remains independent of AVBD.

**Export OBJ…** writes only the skin mesh, retaining polygon/quad connectivity in metres
and application axes. It does not export anatomy, fit bones, weights or drivers. For
pending or stale output choose the last accepted skin, update/rebuild a frozen copy and
export it, or cancel. Subsequent live edits cannot change the captured export revision.

For a compact headless example, run `AnthroForge.exe --cli run examples/skin.json` from
the distribution directory. It uses explicit low-cost demonstration settings, creates
skin and a one-bone fit, and writes `skin.anthroforge` and `skin.obj`. These settings do
not change the application's defaults. See the [authoring API](authoring_api.md) for the
same operations used by the desktop.
