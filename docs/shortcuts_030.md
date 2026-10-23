# Shortcuts and Parametric curves — development walkthrough

These operations are implemented on the unreleased 0.3 feature branch. The runtime
version remains 0.2.4 while qualification continues. Follow the
[cloud task record](tasks/shortcuts-parametric-030-cloud.md) for current evidence and
remaining work; the [specification](specification_030.md) remains authoritative.
This branch writes schema 5 and reads schema 4. Keep source projects backed up when
trying development builds; released 0.2.4 cannot read the new format.

## Run the example

After the normal source/native setup, run from the repository root:

```sh
uv run --no-sync python -m anthroforge run examples/shortcuts_parametric.json
```

The example creates a closed, 64-point Parametric circle and exposes its radius.
A Length driver writes the radius through the native expression `value`. Editing
that driver changes the accepted radius from 0.03 to 0.05 metres and recomputes the
curve. The `radius_result` response reports `value: 0.05`; `driver_result` includes
the formula's accepted result and status. The project is saved under
`build/shortcuts-parametric.anthroforge`. JSON output uses canonical metres/radians
even though the example chooses millimetres for desktop display. Numerical `run`
and `serve` do not initialize Qt.

In the desktop, open **Shortcuts → All** to edit Radius control. Circle radius is
read-only while its formula is enabled. Right-click an ordinary driven numeric
field and choose **Go to driving shortcut** to open its controller. Exposing or
hiding a shortcut changes its presentation; it does not disable a formula.
The Parametric inspector edits XYZ equations, the interval, point count and typed
variables. Generated coordinates are read-only. Junctions, point-specific deformer
membership/weights and formula references to generated points lock point count.
Hover the label or field for the reason. Removing those references unlocks it;
disabling a binding or formula retains its references and therefore retains its lock.

## References, values and policies

`property.discover` returns references; retain those references rather than building
paths from labels. A reference contains `target`, a `path` array and an optional
zero-based `component`. Stable members use `@<identity>`. The example supplies the
variable identity `radius` explicitly; ordinary creation generates identities.
Renaming a variable retains its property reference and updates its symbol in unchanged
XYZ/interval expressions. Explicitly edited expressions retain the text you supplied.
Removing a variable that is still used reports which references must be resolved.

Each exposed property wrapper has its own label and attachment policy. Direct
`property.set` uses ordinary edit semantics; `shortcut.set` activates only the
initiating wrapper's policy. A driver's value edit similarly activates its policy.
Ownership is inferred from construction consumers. Backsolve and descendant
overrides require one inferred owning SCP; policy configuration does not move anatomy.

Expressions distinguish integers and reals: `12` is integer, `12.0` is real and
division returns real. Use `round`, `floor` or `ceil` explicitly for integer outputs.
Integers use the native signed 64-bit range. Typed desktop controls preserve exact
integer text, including values above 2^53, through editing and scrubbing. Integer
quantities step by one canonical unit: one metre for Length or one radian for Angle.
The UI displays those quantities in the selected length units or degrees; fractional
canonical values are rejected. Integer angles recognize their rounded degree display.
Dimensions are independent of numerical type. Metres (`m`) and radians (`rad`) are
unit constants; a radius variable declared LENGTH can multiply `cos(t)` directly.
There are no assignments, loops or arbitrary function calls. See the
[expression qualification](research/shortcuts_030/expression_qualification.md).

## Implemented operation signatures

Optional arguments are marked `?`. Operations use the same application commands
as the UI. Mutations return IDs where listed; asynchronous work is observed with
`wait` and inspection operations. Formula diagnostics appear in `driver.inspect`;
a successful command submission alone does not prove successful evaluation.

| Operation | Arguments and result |
| --- | --- |
| `property.discover` | `target?`, `search?`, `values?` → descriptors, references, units, owners and writer IDs |
| `property.get` | `reference` → descriptor plus current value and `driven_by` |
| `property.set` | `reference`, `value`, `uniform?` → ordinary property edit |
| `shortcut.expose` | `reference`, `label?`, `exposed?` → wrapper ID; `exposed: false` hides it |
| `shortcut.inspect` | `reference` → wrapper, policy and inferred owners |
| `shortcut.list` | `selected?`, `search?` → exposed controls in shared order |
| `shortcut.configure` | `reference`, `policy` → replace wrapper policy |
| `shortcut.set` | `reference`, `value`, `uniform?`, `component?` → edit through wrapper policy |
| `shortcut.reorder` | `identities` → complete ordered list of stored wrapper/driver IDs |
| `driver.create` | `label?`, `value?`, `numeric_type?`, `dimension?` → driver ID |
| `driver.configure` | `driver`, `changes` → label/type/dimension/value/exposure/policy |
| `driver.value` | `driver`, `value` → edit virtual input through driver policy |
| `driver.inspect` | `driver` → definition, inferred owners and accepted/pending/failed formula results |
| `driver.remove` | `driver` → remove driver/formulas, retaining current target values; referenced drivers must be disconnected first |
| `driver.formula.add` | `driver`, `target`, `expression`, `inputs?`, `enabled?` → formula ID |
| `driver.formula.update` | `driver`, `formula`, `changes` → edit target/expression/inputs/enabled |
| `driver.formula.remove` | `driver`, `formula` → remove writer, retaining current target value |
| `curve.parametric.configure` | `curve`, `changes` → XYZ, interval, resolution or variable definition changes |
| `curve.parametric.variable.add` | `curve`, `name`, optional `value`, `numeric_type`, `dimension`, `label` → variable ID |
| `curve.parametric.variable.update` | `curve`, `variable`, `changes` → edit variable while preserving identity |
| `curve.parametric.variable.remove` | `curve`, `variable` → remove variable, subject to reference guards |

Formula inputs have either `{name, property: reference}` or `{name, driver: id}`.
Property inputs select a scalar or a vector component. `value` names the current
driver's input. There is one active writer per target component. Invalid or cyclic
formulas retain accepted target values; independent valid formulas can still run.

A policy contains `backsolve` and a `descendants` array. Each descendant entry has
`target` and optional `parent_anchor`, `child_anchor`, `follow_rotation`, `strategy`.
Omitted options use `KEEP`; rotation overrides are `ENABLED`/`DISABLED`. The policy
editor lists the eligible owner and descendants without editing their authored settings.

Use existing `curve.create`/`curve.engine` with `engine: "PARAMETRIC"`. Leaving the
engine retains its inactive definition; returning restores it. Parametric-to-Fiber
conversion copies the accepted finite path into an independent Bézier construction.
Construction duplication/independence copies internal controls and remaps their
references once, while preserving explicit external inputs.
