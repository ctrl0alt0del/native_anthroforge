# Building and deforming skin

Available on the 0.4.0 development branch; release qualification is still in progress.

Open **Skin** in the vertical inspector tabs on the right. **Build Skin** creates the
envelope, generates quad topology and prepares the deformation reference. These stages
can take substantial time on a full assembly. Activity shows the running job and allows
cancellation; previously accepted geometry stays visible while it runs.

Only SCP and tissue surfaces contribute physical volume. Curves, Fibers and other
construction do not thicken the envelope. Closed Fiber paths and enabled FLOW guides
can still guide the separate topology stage.

## Shape and topology

Envelope settings control skin distance, collagen and gap filling. Distances are
percentages of the model's longest axis. Select an SCP to set or paint its collagen
weights and adjust its subtree quad budget. Select a compatible source to override
its gap settings. Display hiding does not remove physical contributors.

Choose QuadWild or Instant Meshes, the target quad count, refinement and symmetry.
QuadWild uses the supported loop and FLOW guides. Change these construction settings,
then explicitly rebuild to apply them; moving anatomy does not remesh existing skin.
Use the display selector to inspect the envelope, topology or final result.

If a later build stage fails, inspect its Issue and retry the relevant stage. A failed
deformation-reference build retains the new topology for retry while preserving any
previously accepted final skin and reference.

## Deformation

After the reference exists, ordinary anatomical updates move skin vertices while
preserving their identities and connectivity. Live, On Release and Manual update modes
remain available. **Update skin** explicitly evaluates the current anatomy against the
retained reference. It does not generate new topology.

Preferences chooses the tissue surface used by new references: **Finished** is the
default and follows cropping, relaxation and stacking; **Inflated rest** uses uncropped
inflation before relaxation and stacking. Both inflated sides contribute. Existing
references retain their captured choice until explicitly rebuilt.

The deformation controls select Linear Elasticity or FAST and their settings. Proxy
resolution changes require reference rebuilding. Invalid or missing material references
block updates with an explanation; the application never silently reattaches them.

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

## Save and export

Projects retain skin definitions, reference data and fitted results. Opening a saved
project restores accepted output without rebuilding everything. Schema 7 reads existing
schema-4–6 anatomy projects and saves new edits in schema 7.

**Export OBJ…** writes only the skin mesh, retaining polygon/quad connectivity in metres
and application axes. It does not export anatomy, fit bones, weights or drivers. For
pending or stale output choose the last accepted skin, update/rebuild a frozen copy and
export it, or cancel. Subsequent live edits cannot change the captured export revision.

For a compact headless example, run `AnthroForge.exe --cli run examples/skin.json` from
the distribution directory. It uses explicit low-cost demonstration settings, creates
skin and a one-bone fit, and writes `skin.anthroforge` and `skin.obj`. These settings do
not change the application's defaults. See the [authoring API](authoring_api.md) for the
same operations used by the desktop.
