# AnthroForge workbench redesign

Status: **approved design, implemented in 0.3.7**. See the
[runtime workbench walkthrough](ui_workbench.md) and [qualification](tasks/ui-workbench.md).
The Preferences actions and shared multiline tooltip style are also delivered in
[0.3.7](usability_037.md). This design reorganizes existing capabilities; it does not
change geometry, attachment rules, shortcut ownership or calculation semantics.

## What the audit found

Reviewed the production QML shell, tissue/curve/shortcut editors, shared controls, and
offscreen captures at 1440×900 and 1050×680. Relevant owners are `Main.qml`,
`TissueInspector.qml`, `TissueInspection.qml`, `Shortcuts.qml`, `CurveEngine.qml`,
`PreferencesDialog.qml`, `UiButton.qml`, `UiHelp.qml` and `Theme.qml`.

| Observed interface | Consequence | Proposed correction |
| --- | --- | --- |
| Two top bars mix file actions, creation, workspace management, profiling and calculation controls. | The same visual weight is given to unrelated work. | App commands in the menu, workspace/view controls over the viewport, calculation state in a stable bottom strip. Keep frequent creation tools directly available. |
| Tissue begins with source replacement, presets, independence and inspection before inflation. | Finding the shaping controls takes scanning or scrolling past setup operations. | Name/type, primary shape parameters, then optional settings and source relationships. |
| Inspect, source actions, preset and numerical controls share one long column. | The user must remember where an action sits in an increasingly large inspector. | Context editor with **Shape, Shortcuts, Inspect** pages, remembering the chosen page for each object category. |
| Several selectors expose identifiers such as `CTRL_POINT`, `SECTION_PROFILE`, `ON_RELEASE`. | Implementation vocabulary obscures understandable choices. | Display names such as Control point, Section profile, On release; retain stable IDs underneath. |
| Some help leads with caveats, implementation stages or preserved data rather than purpose. | The user learns a restriction before learning what the tool does. | Purpose first; useful consequence second; detailed limitations in help or Inspect. |
| Existing charcoal/amber palette, compact radii and flat controls. | The cited purple gradients, glows and rounded-card grids are not an observed defect here. | Retain the established visual identity; improve grouping, contrast, wording and density. |
| Attached tooltip width was unconstrained. | Long help appeared as a single line. | Implemented: one bounded, wrapping shared ToolTip style with Basic fallback. |

Blank anatomy in software/offscreen UI captures is not evidence about viewport rendering.
The prototype uses a clearly labelled anatomy schematic, not a calculated muscle or a
claim that changing its fields evaluates geometry. Its sample names/values demonstrate
layout; production values and units must come from existing descriptors.

## Recommended workbench

The [interactive concept](design/workbench.html) demonstrates object selection,
Anatomy/Construction navigation, inspector pages, shortcut scope, optional sections,
Preferences, and the diagnostic drawer. Edit → Focus editor shows an optional layout
with the navigation pane hidden. This is a presentation choice, not a new anatomical
workspace or dependency policy. The inline version also offers control-height and
inspector-width adjustments for review.

### Stable regions

1. **Menu strip.** File, Edit, Create, View and Help, with the project name. Save/Undo
   remain on the menu and existing keyboard commands. A future compact toolbar option
   may retain their buttons; do not remove discoverability from the menu.
2. **Document navigation.** Keep Anatomy and Construction separate. Search at the top;
   visible object rows below. Keep visibility/delete/context actions on hover or
   selection, with keyboard alternatives. Retain the original structural hierarchy and
   absence of mirrored hierarchy nodes. Full names remain accessible when rows elide.
3. **Viewport.** Largest work area. Its toolbar owns workspace and display controls.
   Its tool rail owns transforms, curves/point placement/drawing, cursor, surfaces,
   tissue creation and measurement. Retain existing anatomical tool icons in runtime;
   the concept's letter/text buttons make the layout inspectable without introducing
   a new icon library. Axis views and camera restoration remain viewport controls.
4. **Context editor.** Object name and type anchor the pane. Three pages: Shape,
   Shortcuts, Inspect. Shape opens by default for a newly selected object category.
   Retain a user's chosen page and disclosure state while navigating similar objects.
   Deliberate page changes may rearrange controls; background updates must not.
5. **Bottom strip and drawer.** Activity, Issues, update mode, Recalculate, save state.
   Short status uses a reserved area; transient messages use the existing bottom-right
   toast. Open the detailed drawer only on request. A problem remains discoverable
   through an Issues indicator; do not hide actionable failures in disappearing text.

No panel is a collection of bordered cards. Use pane boundaries, section headings and
whitespace. Numeric fields align on a consistent value column. Controls use the existing
compact visual language, with adequate pointer targets and larger targets when required.
The viewport's scene colors remain authored/presentation data, not a new global recolor.

### Context editor mapping

| Selection | Shape: first controls | Secondary controls | Inspect |
| --- | --- | --- | --- |
| SCP | Main primitive parameters; Edit primitive; transform where allowed | Attachments, ordered deformers, source replacement, splitting, mirroring | Dependencies, attachment evidence and geometry checks already supported |
| Curve | Direct path-engine selector, Edit points, applicable engine parameters | Closure/sampling, source usage, junctions, independence | Path evaluation, supports and provenance where available |
| Fiber | Same curve editor plus bindings; no object transform controls | Supports/pins, routing, rebind/repair and display radius | Binding and routing evidence; retained-result state |
| Tissue | Inflation mode and principal values; part/side only when relevant | Boundary/taper, smoothing, crop, supported relaxation, constraints/fields, stacking, source graph | Stage comparison, point explanation, findings and section cutaways |
| Surface/Membrane | Source order/correspondence and sampling | Branches, Realign, source navigation; Create Tissue on a Membrane | Existing accepted-result/dependency details |
| Reference image | Image assignment, physical dimensions, opacity | Parenting, calibration, depth/side/axis visibility and pickability | Existing resource/relationship information |
| Point/Anchor | Coordinates or binding controls, as permitted | Existing conversion/rebinding and parent relationships | Existing provider/binding information |
| Hook/Lattice | Target membership and relevant deformation controls | Follow/parent relationships, weights, ordering, resolution locks | Affected consumers and supported diagnostics |

Unsupported controls are not invented to fill a page. Show only actual capabilities;
retain an explanatory reason for important unavailable actions. Mirror selection shows
read-only source properties and Select Source. No duplicated driver editing.

**Shortcuts** keeps precisely its Selected SCP/VCP and All scopes. Values remain direct
edits; options contain renaming, ordering, exposure, policies and formulas. Multi-owner
controls remain under All. Comparison and influence inspection move into a deliberate
detail area rather than being expanded beside every numeric value. Existing override
scope and backsolve semantics remain unchanged.

**Shape** distinguishes frequently adjusted dimensions from setup operations. Change
source, Make Independent, apply preset and delete remain reachable from the object's
relationship/settings area and context menu. They must not become required prerequisites
for ordinary editing. The concept is illustrative, not an exhaustive replacement for
these inspectors: the table is the capability-retention checklist for implementation.

## Copy rules and examples

The label names the thing being changed. A tooltip begins with what the control does,
then adds one consequential constraint if necessary. Long numerical/algorithm evidence
belongs in Inspect or documentation. Do not remove genuine safety restrictions, reset
effects, binding failures or unit information in the name of brevity.

| Current copy | Proposed visible copy | Help / retained detail |
| --- | --- | --- |
| `CTRL_POINT`, `DISTRIBUTED`, `SECTION_PROFILE` | Control point, Distributed, Section profile | Explain each mode's shape effect; retain capability restrictions beside unavailable modes. |
| `INHERIT`, `LIVE`, `ON_RELEASE`, `MANUAL` | Inherit, Live, On release, Manual | Inherit uses the ancestor's mode. Manual needs Recalculate. |
| Change construction source | Source → Change… | Replace the construction used to build this tissue. Keep the existing reviewed replacement workflow. |
| Make construction independent | Make source independent | Copy this tissue's construction so edits no longer change other consumers. External attachment targets remain shared. |
| Curve-engine hint: “Change the path engine directly…” | Path engine | Choose how the curve connects its points. Put Parametric restoration/conversion and Undo details in its help. |
| “QP solver used by routed curves and fibers” | Routed solver | Choose the numerical solver used to route curves around obstacles. Custom is the default; PIQP may help dense routes. Neither is universally faster. |
| Fiber propagation hint: “Applies to future calculations…” | Fiber propagation | Choose how fibers change shape when their supports move. Then explain the two methods and the absence of a collision guarantee. |
| Apply preset hint: “Reset inflation, relaxation and preset-owned constraints…” | Preset | Start from a muscle, layer, rim or bulk configuration. Clearly say selecting one resets inflation/relaxation/preset constraints; retain the complete list of preserved settings in help. |
| Boundary power | Boundary power | Change how quickly inflation grows away from the boundary. Do not rename it to smoothing; it is a different operation. |
| Material resolution | Surface resolution | Controls evaluated surface sampling. Confirm exact units/range and topology-lock reasons from its descriptor. |
| Evaluate tissue | Recalculate | Update the selected tissue using its current settings. |
| “View an accepted computation stage without changing tissue settings” | Show stage | Compare the base, inflated and stacked shapes. This changes only the view. |
| Expose property | Add property… | Show a numerical property as an explicit shortcut. Hiding it does not disable formulas. |
| “Active calculations use the latest committed revision” | Autosave recovery copies | Save a separate recovery copy periodically. While calculations run, save the latest complete checkpoint; it may predate visible edits. |

These are display-text conventions, not new terminology in persisted data or public API IDs.
Before changing a numerical label, trace the actual parameter and unit. For example,
inflation Amount becomes Depth only in modes where that describes its effect correctly.
Ellipses mean a further dialog/choice is necessary; direct actions have no trailing ellipsis.

## Reviewed delivery boundaries

| Increment | Owning boundary | Deliverable and evidence |
| --- | --- | --- |
| 1. Shell/navigation | Main window and existing pane state | Stable menu/view/status regions; resizable panes and remembered layout. Audit every relocated action, keyboard route and minimum size. No geometry/service changes. |
| 2. Context editors | Existing inspector components and typed presentation descriptors | Primary controls first; Shape/Shortcuts/Inspect organization; source navigation. Exercise SCP, Fiber, tissue, image, control, mirror and mixed-selection workflows. |
| 3. Copy and shared controls | Ui controls, option-label mappings, component-owned help | Apply the reviewed copy rules across menus, selectors, errors and tooltips. Preserve IDs, dimensions and structured diagnostic details. Check all new labels against actual behavior. |
| 4. Detailed inspection | Existing Activity, Issues, comparison and inspection adapters | On-demand drawer/details with navigation; search and virtualization for long relationships. Do not duplicate collection or trigger hidden geometry checks. |
| 5. Qualification | Existing UI tools, profiler and packaging | Before/after interaction captures, click-count review, drift-free numeric drags, hover/focus contrast, real production project and portable app. |

Use existing command and capability owners, not a new UI-specific operation system.
Extract cohesive presentation components when moving controls; avoid copying inspector
logic. Shared label mappings belong beside typed presentation metadata, not scattered
conditional replacements of enum strings. Numerical/model behavior is outside this task.
Preserve one undo action per gesture, direct engine changes, keyboard abstraction,
modifier behavior, read-only restrictions, scene revisions and native picking.

Acceptance criteria: no inaccessible old actions; no prerequisite clicks added
to shaping/creation; no transient field movement; tooltip and focus readability; long
names and lists; 1050×680/1440×900 and 150% scale; primary inputs visible without scrolling;
profiler comparison of UI refresh/model churn; offscreen and packaged checks plus honest
limits on physical interactive evidence. Phone-sized rendering of this design is only
for reviewing the proposal, not a commitment to a mobile AnthroForge editor.

The user approved the three inspector pages and placement of advanced relationships.
The prototype is retained as design history; the linked runtime walkthrough is current.

## References and delivered boundary

[Qt custom controls/styles](https://doc.qt.io/qt-6/qtquickcontrols-customize.html)
supports a shared style for attached tooltips. The implementation preserves Qt Basic
for other controls rather than creating per-field popup objects.
[Microsoft Default Programs](https://learn.microsoft.com/en-us/windows/win32/shell/default-programs)
and [Default Apps settings](https://learn.microsoft.com/en-us/windows/uwp/launch-resume/launch-default-apps-settings)
define the implemented per-user registration and user-controlled default choice.
The visual/layout proposal above is based on this repository's observed UI and the
user's preferences, not a claim that a third-party design article proves a local defect.
