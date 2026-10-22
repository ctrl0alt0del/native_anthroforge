# AnthroForge 0.3 — Shortcuts and parametric curves

**Status: confirmed, not implemented.** This is the authoritative 0.3 product contract.
The [implementation plan](implementation_030.md) defines delivery and evidence; the
[engineering guidelines](engineering_guidelines.md) govern implementation. The current
released application remains 0.2.4. This document does not claim runtime qualification.

The [research](shortcuts_030_research.md) and [source inventory](research/shortcuts_030/inventory.md)
record observed Blender behavior. Where earlier proposals differ, this specification
prevails. Existing document, attachment, workspace, scheduling, undo, save and export
contracts continue unless explicitly changed here.

## 1. Release boundary

Deliver numerical-property shortcut wrappers, explicit UI exposure, virtual driving
shortcuts and a general Parametric curve engine through the desktop and shared headless
core. Include the addon's shortcut attachment-edit behavior, not only its arithmetic.
Retain Python 3.12, C++17 and Qt/PySide 6.12.0; numerical evaluation belongs in C++.

Examples may demonstrate circles, arcs and anatomical control relationships. The engine
is not a list of predefined curve shapes. Migration of real Blender skeleton/skull
shortcuts or projects is a separate task. Source inventories and original files remain
reference evidence, not migrated or geometry-qualified output.

Conditionals, scripting, loops, formula-controlled radius/tilt and direct Parametric
Fibers are outside 0.3. Formula-based rest shapes beneath Fiber attachment deformation
remain a possible future improvement. Apply/Bake stays unavailable. No new export,
mirroring, skinning or reconstruction workflow is implied.

## 2. Properties and wrappers

Properties are lower-level data and operations. A shortcut is a separate wrapper around
a numerical property; the property itself is not a shortcut. Eligible numerical
properties have implicit wrappers. Exposing a wrapper makes it an explicit shortcut
without creating a second independent property value.

Cover eligible SCP/VCP properties and their owned construction, curve points, controls,
deformers, tissue parts/sides, engine parameters and parametric variables. Preserve the
true property identity and existing restrictions: generated tissue transforms and other
read-only state do not become writable merely because they are discoverable.
Evaluated measurements and resolved channels may be formula inputs, never write targets.

Ordinary property editing does not automatically activate shortcut attachment policies.
Editing through a wrapper does. Both paths still enforce shared type, reference,
workspace, topology and driven-property restrictions; lower-level access is not a way
to bypass those rules. The UI and headless core have the same contract.

Support component fields and Uniform vector mode. Uniform assigns the same value to
every component, rather than preserving their previous ratios. Proportional behavior
can be expressed with driving formulas. Component write restrictions also apply to
whole-vector edits.

## 3. Driving shortcuts and inferred ownership

A driving shortcut has an editable virtual value, metadata, named inputs and one or more
formula outputs targeting numerical components of implicit or explicit shortcuts.
Inputs may reference several properties. Chains are allowed and remain active when
referenced inputs change, not only while the driving slider is being edited.

Allow one active formula per target component. Separate X/Y/Z writers are possible;
a whole-vector writer conflicts with any overlapping component writer. Driven targets
are read-only to ordinary editing, with navigation to the controlling formula.
Disabling a formula preserves its definition; removing it deletes that relationship.
Either retains the current target value and restores editability when no active writer
remains. Hiding an explicit shortcut never disables formulas or removes the property.

Infer a driving shortcut's owning SCP from the properties it controls. Count controlled
properties reached through chains and the anatomical ownership of shared construction.
If they belong exclusively to one SCP, that SCP owns the shortcut. Targets spanning
multiple SCPs/VCPs have no single owning SCP. Ordinary attachment propagation does not
count as another controlled property: changing a femur dimension does not acquire
ownership of all children that subsequently move.

There is no manual Owning SCP or independent Backsolve SCP selector. Revalidate ownership
and policy eligibility when references change; stale configuration must not apply outside
the inferred scope. Single-VCP controls remain available in the selected VCP's UI, but
this does not grant them SCP-specific attachment policies. Unassigned construction and
controls without a unique anatomical owner remain accessible under All.

## 4. Shortcut attachment-edit policies

Preserve the addon's owner backsolve and descendant attachment overrides. These settings
belong to the initiating shortcut wrapper, not to the raw property, the target wrappers
of its formulas, or a global attachment mode.

| Setting | Supported behavior | Default |
| --- | --- | --- |
| Owner backsolve | Translate the owning SCP so its retained child anchor stays at its pre-edit location relative to its parent; no inverse formula solve or rotation correction. | Off |
| Parent anchor override | Keep, Surface Nearest, Object Origin. | Keep |
| Child anchor override | Keep, Face Center, Nearest Vertex, Object Origin. | Keep |
| Follow Rotation override | Keep, Enabled, Disabled. Disabling rotation does not disable translation following. | Keep |
| Rotation strategy override | Keep, Auto, Stable Surface, Deformation Flow. | Keep |

Descendant overrides apply to explicitly configured descendants of the owning SCP,
including deeper descendants. Do not expand this scope to every SCP reached through
formula targets. Backsolve concerns the owner's own attachment; descendant settings
concern how those children follow. A shortcut without an owning SCP cannot use these
SCP-specific policies. Do not enable direct transforms on generated VCP geometry.

Keep uses authored attachment settings. Changing policy configuration does not itself
move anatomy; it governs subsequent shortcut edits. Auto/Stable Surface/Deformation Flow
retain the applicable addon semantics through the shared standalone attachment service,
using provider capabilities rather than Blender modifier/context inspection.
Stable Surface uses the retained tangent reference; Deformation Flow uses its retained
surface-flow reference with the addon's stable fallback when that reference is unavailable
or degenerate. Rotation strategy can still affect the anchor-offset frame when Follow
Rotation is disabled; do not discard its settings merely because rotation following is off.

Only the initiating shortcut A's policies apply when A drives B and further shortcuts.
B's own policies do not activate through that chain. Ordinary property edits and
reevaluations with no initiating shortcut use normal authored attachment behavior.
Asynchronous work belonging to a shortcut edit retains its originating edit context.

Capture temporary bindings before the edit, retain them across the whole gesture,
including pauses and asynchronous work, and restore authored attachment settings after
use. Commit keeps the resulting geometry and poses; cancel restores the original state.
One gesture is one undo action. Replace the addon's timeout-based session bookkeeping
with the existing explicit begin/update/commit/cancel lifecycle, not a new timeout.

## 5. Expressions, types and units

Use a deliberately restricted expression language shared by drivers and Parametric.
Support arithmetic, powers, approved mathematical functions and comparisons. Exclude
conditionals, loops, arbitrary Python, external I/O and hidden assignments. Each output
has an explicit target; an expression cannot mutate additional properties.

- `12` is an integer literal; `12.0` and `1e3` are real literals.
- Integer addition/multiplication stays integer; mixing integer and real produces real.
- Division produces real, so `5 / 2` is `2.5`.
- Integer targets require integer results. Use explicit `round`, `floor` or `ceil` for
  conversion; do not silently truncate even a whole-valued real result.
- Integer results may feed real-valued properties. Existing ranges and validity rules
  still apply; numerical failures are not silently clamped into valid inputs.

Numerical type and physical quantity are separate. Support length, angle and dimensionless
variables; use canonical metres/radians with the existing UI display conventions.
Reject invalid unit operations. Names such as Radius do not establish units: the source
inventory contains radius-labelled scale factors. Preserve explicit quantity metadata.

Names are user-facing symbols; relationships must survive renaming/reordering through
stable identities. Expose useful errors identifying expression, target and offending input.
The selected native parser's default grammar, casts or extra capabilities cannot override
this application contract. Parser selection/qualification is implementation work, not a
completed finding of the research.

## 6. Evaluation and failure semantics

Separate authored inputs and definitions from accepted formula outputs and geometry.
Publication must not look like a new user edit or recursively activate target wrappers.
Use the existing dependency graph and coordinator for invalidation, capture, reservations,
safe cancellation, coalescing, revision validation and publication. Preserve Live, On
Release and Manual behavior, outside-workspace priority, history and save checkpoints.

| Situation | Required result |
| --- | --- |
| Cyclic formulas | Allow the authored definitions, retain accepted values for the cyclic group and dependent formulas, warn through Issues, continue unrelated calculations. |
| Invalid independent output | Retain that property's accepted value and block its dependent formulas; apply other valid independent outputs. |
| Jointly conflicting outputs | Reject the conflicting property group together, retaining its accepted values; do not choose a winner through iteration order. |
| Obsolete/cancelled work | Do not overwrite newer or restored history state. |
| Missing required accepted input | Report the failed prerequisite; do not invent a fresh value or wait indefinitely. |

For example, a minimum-thickness increase and a maximum-thickness decrease can each be
valid alone but violate minimum <= maximum together. Retain both in that conflicting
group while independent changes proceed. Do not reject every output merely because one
target fails, and do not label retained values as freshly calculated.

## 7. Parametric definition and generated points

Parametric evaluates X/Y/Z expressions from a curve parameter `t` and a dynamic list of
named, typed variables. Variables are editable numerical properties with implicit
shortcut wrappers. The curve's existing local transform and consumer contracts apply.
The parameter is not animation time.

The default parameter interval is 0 to 1. Start/end may be expressions of variables;
range and resolution are also eligible numerical driving targets. Resolution controls
the number of generated points using uniform parameter sampling, not a step size in
world units or equal arc-length spacing. Changing the interval at fixed resolution
does not increase the number of generated points.

Generated point positions come from the equations; do not invent independently editable
Bézier handles or allow sample dragging to rewrite equations silently. Provide parameters
and formulas for shaping while this engine is active. Radius/tilt expressions are deferred;
preserve the ordinary curve contract for supported non-formula attributes.

Open/closed curves remain one connected path. Closed curves need not have coincident
formula endpoints: a straight closing segment is permitted. Preserve the common curve
contract against a duplicate seam endpoint. Do not add a periodicity/matching-endpoint
requirement or inherit another application's self-intersection restrictions automatically.

Hooks and applicable lattice deformation act after formula evaluation, keeping the
definition editable. Stable membership and weights must not be reinterpreted silently
when sampling changes. Consumers retain their own sampling, ranges, direction and
placement; primitives and surfaces accept the common curve output.

## 8. Junctions, engine switching and Fibers

Junctions use the existing explicit shared-source relationship. Parametric source points
move their followers when their evaluated position changes. Unlike ordinary bidirectional
point editing, a follower cannot arbitrarily move a formula-controlled source position.
Two independently formula-controlled members must agree at their junction within the
qualified geometric tolerance or report a conflict; do not deform equations secretly.

Any junction on the curve locks its resolution. Show the reason in the disabled control's
tooltip and enforce it through API/formula writes. Removing the final junction removes
that reason, while other existing topology/attachment locks still apply. Do not retain
extra junction samples as a substitute for this confirmed lock.

Engine selection applies directly as one undo action:

- Switching to Parametric restores its stored formulas, variables and settings. With no
  stored definition, use a valid straight-line formula and display that straight line.
- Switching away uses current generated points as authored controls, not an unrelated
  older authored point set. Bézier can represent the sampled segments with straight
  handles; Polyline connects them; ROUTED uses them as routing control points.
- Keep the parametric definition for a later return. Existing topology restrictions still
  apply. Do not add Preview/Accept gates, bake deformation or apply a deformer twice.

Undefined or nonfinite evaluated coordinates fail the new evaluation as a whole. Retain
the accepted shape and report the expression and parameter involved. With no accepted
result, show a straight-line failure placeholder that consumers cannot use as valid
geometry. A successfully evaluated initial straight-line definition is an accepted result,
distinct from this failure placeholder. Fixed samples cannot certify continuity between
samples; do not claim otherwise or bridge known invalid samples silently.

Creating a Fiber from a Parametric curve makes an independent copy converted to the
default Bézier engine. Preserve the exact finite accepted sampled path, including its
corners, using necessary points and straight handles rather than an approximate smooth
fit. This is not a promise of exact representation of the unsampled analytic curve.
The original definition remains untouched and unrelated to the Fiber copy.
Allocate new curve/point identities and remap copied structural relationships; exact
shape preservation does not authorize linking the copy's control points to its source.

Capture the accepted resolved shape at dispatch after required active work, with existing
revision/restart guards. Accepted Manual results may be used with their provenance;
missing accepted input fails. Preserve closure, applicable path attributes and required
structural relationships under the copy's identity remapping. More points are acceptable
for exactness.
Parametric cannot be selected directly on a Fiber in 0.3.

## 9. Shortcut UI and shared operations

Provide exactly two tabs: Selected SCP/VCP and All. All lists explicitly exposed controls,
not every implicit wrapper. Implicit properties remain reachable through their ordinary
inspectors and searchable property selection. Controls spanning multiple anatomical
owners appear only in All; group single-owner, shared and unassigned controls clearly.

Support search, custom display labels and drag reordering, with bounded/virtualized lists
for large collections. Expose a property from its
context action. Add Driving Shortcut opens focused controls for its value, named inputs
and target/formula rows using searchable selectors rather than raw property paths.
Show read-only driven values and navigation to their source. Use existing numerical
typing/dragging, transactions, keyboard routing, Ui controls and theme.

Direct settings apply without mandatory Preview/Accept or extra confirmation steps.
Preserve focus and gestures; transient feedback must not move editor fields. Use existing
toasts, Activity and Issues for pending work and detailed failures. UI disabled states
present shared policy; they are not the enforcement boundary.

Desktop and headless clients share property discovery, shortcut lifecycle/exposure,
formula configuration/editing, policy inspection and parametric-variable operations.
Reuse the command catalogue, curve-engine selection and evaluation operations; no Blender
runtime, active-viewport dependency or scripting escape hatch is introduced.

## 10. Persistence and compatibility

Use schema 5 for newly saved 0.3 projects. Include a schema-4 reader for existing 0.2.4
projects, initializing new shortcut state empty and leaving existing curve engines
unchanged. Preserve geometry, attachments, accepted results, object/point identities,
resource relationships, workspaces and startup recalculation behavior. Loading must not
trigger blanket recomputation, rerouting or recapture to manufacture compatibility.

Persist editable shortcut definitions, exposure/order/labels, policy configuration,
stable formula references, accepted output provenance and stored parametric definitions,
including inactive ones, for the selected saved revision. Preserve existing atomic saves,
file ownership, historical checkpoints and resource lifetimes. Do not serialize native
handles, compiled-expression caches or undo history.

Saving subsequently writes schema 5. Older applications reject it rather than partially
reading new behavior. This reader does not promise support for schemas 1-3 or Blender
project migration. Compatibility is qualified with actual 0.2.4 round trips, not just a
manifest-version rewrite.

## 11. Superseded proposals and release evidence

| Superseded proposal | Confirmed 0.3 rule |
| --- | --- |
| A property itself is a shortcut; normal fields always apply shortcut policies | Properties remain below separate wrappers; only wrapper edits activate their policies. |
| Manually choose a virtual shortcut's owner or backsolve target | Infer one owning SCP from controlled properties; multi-owner controls have none. |
| Accumulate target-wrapper policies or expand to all formula-target descendants | Only the initiating wrapper's policies, scoped as in the addon. |
| Reject cyclic definitions or the entire multi-output edit | Retain cyclic/failed dependent values; apply unrelated valid outputs; reject jointly conflicting groups together. |
| Resolution counts intervals/parameter-unit steps or retains extra junction samples | Uniform generated-point count; any junction locks resolution. |
| Formula-engine selection requires an editor/preview/accept gate | Immediately restore the stored definition or a straight-line formula. |
| Restore old hand-edited points when leaving Parametric | Use current generated points; retain formulas for a later return. |
| Parametric Fiber rest-shape deformation in 0.3 | Independent exact-path Bézier conversion; direct Parametric Fibers deferred. |
| Require matching closed endpoints; add radius/tilt formulas and conditionals | Straight closure allowed; XYZ only; no conditionals. |
| Reject all existing project formats when introducing schema 5 | Read existing 0.2.4/schema-4 projects; preserve their accepted state. |

The [implementation acceptance matrix](implementation_030.md#acceptance-matrix) is required
before release. Production code, parser qualification, geometry/attachment parity,
performance, GUI and package checks remain unperformed by this documentation task.
Release as 0.3.0 only after qualification, with one canonical
`dist/0.3.0/AnthroForge.dist` and `dist/AnthroForge-0.3.0-source.zip`.
