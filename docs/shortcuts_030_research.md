# 0.3 preparation: anatomical shortcuts and formula curves

Research completed 2026-10-22 against standalone `e448291` and addon
`fae36aba1b208676cf21d7c4a78a20d5b1f68c66`. Source observations remain evidence; the later
[confirmed 0.3 specification](specification_030.md) and
[implementation plan](implementation_030.md) now supersede the design proposals and open
questions below. **Confirmed, not implemented:** neither research nor consolidation
changes production code, application version, project schema or source `.blend` files.

## Confirmed direction after the interview

- Eligible SCP/VCP numerical properties have separate implicit shortcut wrappers;
  properties themselves are lower-level data/operations. Explicit shortcuts expose the
  user's chosen wrappers without a second independent value. Ordinary property editing
  does not activate wrapper attachment policies.
- Driving shortcuts introduce a virtual editable value and formulas targeting other
  shortcuts, whether exposed or implicit.
- Add a general curve engine evaluating `x(t, variables)`, `y(t, variables)` and
  `z(t, variables)`. Its editable variable list is dynamic; variables have implicit wrappers.
- Formula-driven curves are not a menu of fixed circle/ellipse/helix types. Such shapes
  can be examples/templates of the same engine.

## Source inspection

The original files previously identified by the user were inspected in Blender 5.0.1
background mode with factory startup and automatic scripts disabled. Only the required
addon property classes were registered, not addon runtime/load handlers. Source SHA256s
were checked before and after. No file was saved or migrated.

| Source | SCPs | Saved shortcuts | Driver FCurves | Shortcut targets |
| --- | ---: | ---: | ---: | --- |
| `E:/development/WIP_models/skeleton_comb_base.blend` | 33 | 105 | 34 | 82 Geometry Nodes inputs, 14 transforms, 9 custom properties |
| `E:/development/WIP_models/skull_muscles.blend` | 19 | 11 | 6 | 9 transforms, 2 custom properties |

All **116 paths resolve**, including their values. All saved shortcut owners are SCPs;
there are **no saved VCP shortcuts in these two files**, despite the skull containing
muscles. This does not restrict 0.3's requested VCP coverage.

The [complete readable inventory](research/shortcuts_030/inventory.md) lists **every
shortcut's saved path, resolved object/property, and incoming/transitive downstream
drivers**, followed by all **40 exact driver expressions and variable targets**.
The [JSON inventory](research/shortcuts_030/inventory.json) additionally preserves socket
names, values, property metadata, vector modes, attachment overrides and FCurve mapping.
Hashes are recorded there. These inventories are committed; raw background captures
remain local in `build/shortcuts-030/` and contain no necessary extra shortcut definitions.

### A shortcut is usually an input to a driver

None of the 116 exposed shortcut targets is itself driven by a saved FCurve.
**12 skeleton and 2 skull shortcuts feed drivers**; the other 102 have no declared
downstream driver relation. They can still change geometry through modifiers and
attachments. The driver tables do not pretend to enumerate those other dependencies.

There are 39 SCRIPTED drivers, all reported as simple expressions by Blender, and one
AVERAGE driver. The latter copies one input; its stored expression text is not its
evaluation rule. Driver FCurves have no modifiers, two identity key points and linear
extrapolation. A seven-value mapping probe from -2 through 10 matches identity to
about 6e-8. This is a definition/mapping audit, not shape parity under edited parameters.

### Skeleton controls and exact relationships

| Control family | Observed behavior |
| --- | --- |
| Ribs Arc Radius | Custom property on `ribs_curve`; drives all three guide scale components. Also feeds Sternum width. |
| Ribs Arc Angle | `ribs_geom.modifiers["GeometryNodes"]["Socket_5"]`, socket **Angle** in `Loft_Two_Curves`; also feeds Sternum width. |
| Ribs Lower Angle | Same modifier, `Socket_10`, socket **Lower Angle**; no FCurve consumer. |
| Ribs Top/Bottom Radius | Custom properties on their respective profile curves; each drives X/Y/Z scale. |
| Sternum Height | Custom property drives Sternum Z scale. Width is unexposed: `r * sin(a/2)` → `Sternum["Sternum Width"]` → Sternum Y scale. |
| Pubis Arc Radius / Shrink | `pubis_arc` owns the input values. They are copied into `ilium_arc` and `ischium_curve`. Each guide scales as `(r, r*shrink, r)`. |
| Pubis Arc Angle | `pubis_geom["Pubis Arc Angle"]`; body X scale is `angle*r/2`. It also feeds Sacrum width. |
| Ilium Seg Angle | `ilium_geom["Ilium Seg Angle"]`; body X scale is `angle*r/2`, using the linked pelvic radius. |
| Sacrum Width, unexposed | `r*sin(a/2)*0.67*s`, where `s` is **Pubis WORLD_SPACE SCALE_AVG**, then drives Sacrum X scale. This is not simply the local X scale. |
| Radius Length | Direct Radius local X scale; Ulna X scale reads **Radius WORLD_SPACE SCALE_X**. |
| Tibia Length | Direct Tibia local Z scale; Fibula Z scale uses AVERAGE with one SINGLE_PROP input `Tibia.scale[2]`. |
| Hip Joint Distance | `hip_join_hook["AF Local X"]`; three affine formulas combine AF Local X/Y/Z with stored basis coefficients and offsets to drive its location. |

The saved pelvic and rib guides are **closed, four-point Bézier splines**. Their radius
drivers scale these existing curves; no driver evaluates their point coordinates from
`sin(t)`/`cos(t)`. Replacing those curves with mathematical circles is therefore an
intentional possible shape change, not an automatically exact migration.

The remaining controls include frontal/back rib Hook X positions, Ischium/Ilium X
rotation, Humerus/Femur length, Carpals width, lattice/hook sizes and Knee Cap protrusion.
Full ownership and paths are in the inventory.

**Digits:** eight shortcuts per finger/toe, ten digits = 80 controls. They target the
existing `FingerNodes*` inputs, not Blender FCurves:

| Input | Socket |
| --- | --- |
| Metacarpal / Proximal / Middle / Distal length | `Socket_12` / `Socket_2` / `Socket_3` / `Socket_4` |
| Metacarpal / Base / Middle / Tip thickness | `Socket_13` / `Socket_8` / `Socket_9` / `Socket_10` |

Spread, three bend angles and Knuckle Size also exist on the node groups but are not
saved explicit shortcuts. This directly supports the implicit/exposed distinction.
Standalone already has Segment Chain parameters; another digit construction engine
is not needed for these controls.

### Skull controls

| Saved shortcut | Target / behavior |
| --- | --- |
| Cranium Lobe Width | `frontal_lobe_hook.scale[0]` |
| Nasal Inner / Outer Width | `Nasal Frontal Hook.scale[0]` / `Nasal Back Hook.scale[0]` |
| Maxilla Lower / Top Radius | Uniform vector shortcut to the corresponding curve's `scale` |
| Maxilla Bottom / Top Location Y | Corresponding curve's `location[1]` |
| Cheekbone_Front Protrusion | `Cheekbone_SuperHook["AF Local X"]` → three affine location drivers |
| Mandible_Side Base Size | Uniform vector shortcut to `mandible_side_base_hook.scale` |
| Ajar_Cartilage Protrusion | `ajar_side_hook["AF Local Y"]` → three affine location drivers |
| Brow_Ridge Location Y | `front_brow_ridge_hook.location[1]` |

The nine local-hook drivers across both files implement `location = origin + basis *
local_controls`. Their exact coefficients are retained in the driver inventory. A
native local-frame control may represent this more directly than manually authored
three-output formulas; equivalence must be qualified, not assumed.

### Behavior that property paths alone would lose

- **Seven uniform vector shortcuts:** four skeleton sizes and three skull sizes.
  Do not turn these into unrelated axis sliders when preserving the old control.
- **Pubis Arc Angle override:** editing it temporarily uses SURFACE_NEAREST parent,
  FACE_CENTER child, enabled follow rotation and DEFORMATION_FLOW for **Ilium SCP_12**.
- **Cheekbone_Front Protrusion:** owner back-solve is explicitly enabled. No other
  captured shortcut has the flag enabled. This participates in attachment edit handling,
  not just arithmetic evaluation.
- **World/local distinction:** the two TRANSFORMS variables above are evaluated world
  channels; ordinary `scale[n]` property reads are local channels.
- **Units are not implied by names:** Ribs/Pubis Arc Radius and Sternum Height have
  Blender subtype NONE and feed scale channels. Pubis/Ilium angles have subtype ANGLE.
  Migrating a value called Radius into a physical-length variable requires checking
  the original guide dimensions and frames; copying its number as meters is not justified.

The addon resolver, value writer, shortcut edit use case, override sessions and owner
back-solve are separate components (`core/shortcuts/*`, `app/use_cases/shortcut_edit.py`).
The standalone should preserve necessary behavior in its shared edit/attachment policies,
not recreate Blender's global RNA-path lookup or transient context machinery.

## How other applications handle this

| System | Observed design | Useful lesson for AnthroForge |
| --- | --- | --- |
| [COMSOL Parametric Curve](https://doc.comsol.com/6.4/doc/com.comsol.help.comsol/comsol_ref_geometry.23.053.html) | Coordinate expressions, named parameter/range and local placement. Approximates the mathematical curve with a B-spline, using relative tolerance and a maximum knot count; offers arc-length reparameterization. | Store equations separately from bounded evaluated geometry; make approximation quality explicit. Its self-intersection restrictions are not automatically our requirements. |
| [Creo curve from equations](https://support.ptc.com/help/creo/creo_pma/r13/usascii/part_modeling/part_modeling/To_Create_a_Datum_Curve_from_Equations.html) | Equations in a selected coordinate system, one independent parameter and editable interval; Cartesian, cylindrical and spherical coordinates. | A single parameter plus local frame is sufficient; additional coordinate systems can be expressions, not new primitive classes. |
| [SOLIDWORKS equation-driven curves](https://help.solidworks.com/2023/english/SolidWorks/sldworks/c_equation_driven_curves.htm?id=28.14.16) | Explicit/parametric equations, 3D coordinate equations, interval and radians. The cited version routes global variables through dimensions. | Support direct named variables instead of importing that extra UI step. |
| [FreeCAD expressions](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Expressions.md) | Property references, user-facing names, functions, conditionals and dimensional unit validation. | Property identity, units and expression diagnostics belong in a common layer. Its angle convention differs from Blender's; choose and document ours. |
| [Houdini channel references](https://www.sidefx.com/docs/houdini/expressions/ch.html) | Parameters can reference other parameters; spare/interface parameters drive internal nodes. | A virtual control and its downstream relationships need not correspond to a mesh property. |

These are documentation comparisons, not tested integrations or performance rankings.
The cited FreeCAD documentation mirror is archived; it is evidence of the expression
design, not a claim about the newest release interface.

## Historical ownership proposals — superseded by the specification

The following captures the research-stage proposal, not current product authority.
In particular, an explicit shortcut is now a separate wrapper rather than merely a
catalogue presentation reference; attachment policies do not live on raw properties.
The specification defines partial/grouped failures, inferred ownership, integer/real
types, no conditionals, generated-point resolution locks, direct engine restoration and
independent Bézier Fiber conversion. Use the implementation plan for current boundaries.

**One numerical-property catalogue.** Give properties stable identities, type/unit/range,
component information, getter and semantic editing operation. Use stable entity/part/
point/variable IDs, not display labels or collection positions. Reuse existing validation,
workspace and topology policies. An explicit shortcut is a presentation reference to this
catalogue; removing it does not remove the property or break a formula.

Include owned construction and controls: many observed SCP shortcuts edit a **curve,
Hook or lattice**, not an SCP transform. Shared construction can be presented under an
SCP while keeping its true owner and consumer relationships. Curve variables need the
same catalogue. Read-only evaluated channels, such as resolved world scale, require
explicit provenance and cannot be mistaken for editable authored properties.

**Driving shortcut.** Store its virtual input, metadata, referenced inputs and a list of
`target property ← expression` outputs. A formula may read several other properties,
as the existing Sternum/Sacrum drivers demonstrate. Resolve and validate all outputs
together, then produce one coherent edit/undo and downstream invalidation through the
existing operations and coordinator. Do not issue one independent user command per
target or repeatedly mutate properties from Python callbacks. Formula dependencies
must remain active when any referenced input changes, not only when the exposed slider
is dragged. Evaluated values need distinct ownership from authored defaults.

**Common native expression service.** Compile expressions once per formula/symbol
layout, evaluate owned variable snapshots in C++, and share it between drivers and the
curve engine. It returns values/diagnostics; it does not know about UI, documents or
`bpy` paths. Dependency references and edits belong in the application/core contracts.

**Parametric path engine.** Own coordinate expressions, local variables with stable
identities, interval, closure and quality settings. Feed the existing path contract,
consumers, transforms and scheduling. Generated samples are evaluated output, not
authored control points. A dynamic variable list does not require unstable references
such as “the third UI row”: names in formulas resolve to durable variable IDs.

Existing integration points were inspected:

- `core/construction.py::Curve` currently requires at least two authored points and
  accepts exactly three typed engines; closed curves require three authored points.
  Those assumptions need engine-specific ownership, not fake points for formula curves.
- `core/curve_engines.py` owns typed settings; `application/curve_evaluation.py` separates
  binding resolution from engine evaluation; `native/paths.py` owns native sampled paths.
- `core/curve_uses.py` already separates consumer sampling/placement from the curve.
- `core/dependency_graph.py` already distinguishes pose/path/geometry outputs and finds
  cycles. Extend it and the existing coordinator; do not add a second scheduler.
- Shared commands already enforce edit/undo and validation. A property catalogue must
  route to these semantic operations, not bypass them with generic attribute writes.

### Example: a variable-driven arc

Illustrative design, **not a reconstruction of the saved pelvic guide**:

```text
variables:
  r      Radius       length
  k      Flattening   dimensionless
  start  Start angle  angle
  arc    Arc angle    angle
t: 0 .. 1

x = r * cos(start + arc*t)
y = r * k * sin(start + arc*t)
z = 0
```

`r`, `k`, `start` and `arc` are editable implicit shortcuts; the user may expose any
subset. A driving shortcut can set `r` and simultaneously drive another object's width.
A circle is simply `x=r*cos(t), y=r*sin(t), z=0`, interval `0..2*pi`. No predefined
circle engine is necessary. Prefer named variables in the editor; positional arrays
can remain an internal evaluation layout.

### Native parser candidates, not yet selected

- **[muparser](https://beltoforion.de/en/muparser/):** C++, CMake, bytecode and constant
  folding; a plausible first candidate for compact scalar expressions. Its
  [interface](https://www.beltoforion.de/en/muparser/interface.php) reuses compiled bytecode;
  [variable binding](https://www.beltoforion.de/en/muparser/customizing_muparser.php)
  requires stable externally owned storage. Compile against worker-owned frames,
  not live document memory. Disable optional OpenMP to preserve coordinator ownership.
  Assignment/operators and callbacks require a deliberately restricted expression
  grammar; default availability is not the application contract.
- **[ExprTk](https://www.partow.net/programming/exprtk/index.html):** C++ expression
  compilation, named scalar/vector variables, conditionals and richer operations.
  A stronger candidate if actual indexed vectors become required. Its
  [configuration](https://github.com/ArashPartow/exprtk/blob/master/readme.txt)
  can disable control structures. Loops, assignments, I/O and uncontrolled callbacks
  must not become accidental product features.

The inspected formulas need only arithmetic, sine, constants and multi-input references.
An unbounded *number of named scalar variables* does not by itself require vector-index
syntax or a scripting language. Neither candidate was compiled or benchmarked in this
research stage. Compare startup/compile cost, slider reevaluation, curve batches,
memory, concurrent ownership and invalid-expression diagnostics before selection.
Dimensional validation is an application responsibility; neither candidate here is
being proposed as a complete CAD unit system.

## Research questions resolved by the confirmed specification

This is the historical question set that motivated the interview, not an outstanding
product backlog. The [final contract](specification_030.md) resolves these topics and
records superseded alternatives. Parser qualification and the required evidence below
remain implementation tasks, not claims made by the inventory.

1. **Editing a driven target:** expose its formula/controlling value, or allow an
   explicit override that disables the relationship? Avoid silently accepting a value
   that the next calculation immediately overwrites. Multiple writers need a defined
   conflict policy, including overlapping vector/component targets.
2. **Scope and presentation:** object-local versus document-wide virtual controls;
   how exposed controls are grouped, searched and shown for shared construction.
3. **Geometry edits:** what moving a point means for a formula-defined curve. Prefer
   parameter editing while that engine is active; don't silently replace equations
   with sampled points or introduce inverse fitting without a separate decision.
4. **Fibers/junctions/deformers:** define endpoint anchoring and shared junction behavior
   for a formula engine, and where Hook/Lattice act. Existing two/three-authored-point
   assumptions cannot determine this correctly. Formula evaluation and attachment
   deformation can be separate stages, but the resulting visible behavior needs agreement.
5. **Units, sampling and domain:** angle convention, parameter interval units, radius/
   tilt fields, absolute/relative tolerance and maximum work. Reject nonfinite results
   and discontinuous paths with useful locations. Adaptive sampling must preserve
   material correspondence, not bind attachments to transient sample indexes. A few
   midpoint probes cannot certify arbitrary high-frequency formulas.
6. **Attachment edit policies:** explicitly decide whether the observed Pubis override
   and Cheekbone back-solve are needed in 0.3 and represent them in the shared attachment
   subsystem. They are not reproduced by formulas alone.

## Evidence required from a future implementation

Use the captured pelvic multi-output chain, rib-to-sternum relation, local Hook basis,
world-scale references, uniform sizes and all 80 digit controls as acceptance cases.
Add VCP inflation/part-side properties because these source files do not exercise them.
Test renamed/deleted variables, duplicated shared constructions, cycles, conflicting
writers, invalid formulas, locked topology, undo/cancel, save/reopen and active jobs.
Qualify curve sampling/correspondence and downstream attachments/surfaces under changing
variables; compare actual geometry before claiming Blender-equivalent migration.
Profile compilation separately from repeated native evaluation and downstream geometry.
