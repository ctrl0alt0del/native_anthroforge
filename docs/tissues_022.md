# Building tissues

The [0.2.2 specification](specification_022.md) defines the supported combinations.
See [release validation](development_status.md#unified-tissues-022) for measured evidence
and the limits of background/offscreen inspection.

## Select construction and create

Tissues share one entity and evaluator pipeline. Muscle and soft-tissue labels provide
creation defaults; changing a label later keeps the settings you edited.

| Desired base | Construction steps | Starting preset |
| --- | --- | --- |
| One attached location | Select a Point or Anchor and Create Tissue | Closed Bulk |
| One attached path | Select a Curve or Fiber and Create Tissue | Rim |
| A sheet between attached paths | Select curves, use Patch / Surface, then Create Tissue | Muscle or Layer |
| A closed boundary | Select a closed curve, use Patch / Surface, then Create Tissue | Layer or Pouch |

All-Fiber surfaces become Membranes automatically. Create Tissue converts generic sources
to independent attached construction: Point → Anchor, Curve → Fiber, Surface → Membrane
with its required curves converted to Fibers. New bindings use nearest ready SCP surfaces;
existing Fibers retain their binding intent. Original objects remain unchanged. To create
only attached construction from a generic Surface, use **Create Membrane** in its inspector.

Press **Create Tissue** on the main toolbar or Create menu. The selected construction
supplies the source directly with no modal; the source inspector offers compatible preset
choices. Conversion and tissue creation form one undo action. Capturing and evaluation
run in the background; a failed/canceled conversion leaves no partially created graph.
Already-attached sources are shared live without another copy.
The new object appears in Anatomy. Its source remains in Construction and is shared live.
**Edit construction source** enters the source editor; a Membrane's **Edit curve** buttons
enter its individual Fiber editors. Use **Make Independent** to copy its complete construction
graph. Copies preserve internal junction sharing and explicit external attachment targets.
Deleting the tissue preserves its sources. Referenced sources cannot be deleted first.

## Shape the result

The inspector exposes the main part and any branches, with Side A/B when enabled.
Choose an inflation mode compatible with the source, then edit Amount and its controls.
Control Point mode offers **Move control in viewport** with the usual gizmo and undo.
Section Profile has four station depths/peaks, roundness and direction; it requires an
ordinary open loft. Reversing the side or enabling both sides is explicit. Branch connector
width/fullness and each part's supported inflation settings remain independent.

**Preview inflation edits** shows a green candidate without replacing accepted geometry.
It previews inflated rest before relaxation, cropping or stacking. Accept commits one undo
action; Cancel discards it. Direct transforms or vertex editing of generated tissue are
unavailable. Edit construction or tissue parameters instead; Apply/Bake is unavailable.

Height smoothing belongs to muscle-grid inflation and preserves fixed boundaries, seams
and protected zero-height creases. Radial, Profile and Normal modes instead offer
Geometric or Static PBD relaxation. These are static shape calculations, not dynamics or
general physical contact. The capability matrix explains combinations that are rejected.

For Normal shells, **Weight fields** can define Base-domain `INFLATION` weights. Explicit
zeros remain zero; an absent field uses the boundary-derived defaults. Named Base/Rest
fields are also available as constraint masks. Choosing a field enters point editing.
Ctrl-click to extend selection, then commit **Weight** to update selected points in one undo
action. Mixed values are indicated explicitly. Blue means zero, gold partial and red full weight.
Coordinates remain read-only. Remove/change referencing constraints before deleting a field.

**Constraints** supports Fixed/Soft masks, feathering, strength and offsets. Source-relative
goals are the default; explicit target binding captures another anatomical surface's role.
The structural backing stays exact even if a soft backing region is also authored.
Contradictory fixed goals report an error. **Material crop** clips supported muscle-grid
results in the source domain; cut edges do not become attachments or zero-height boundaries.

## Bind to tissue and stack layers

An Anchor, Fiber binding or target-relative region can explicitly choose Tissue Base or
Tissue Final. Base exists for Membrane construction; radial/sweep tissues expose Final only.
Bindings retain their material location as the target deforms. **Explicit rebind** chooses
a new location; ordinary parent updates never silently capture the nearest surface again.
Incoming bindings lock incompatible topology edits with a reason naming the dependency.

Stacking is a separate relationship. Both participants must use surface construction and
enable stacking. Muscle presets enable it initially; other presets do not. Automatic
candidate detection determines order. In **Stacking**, search for another tissue, choose
the sides and choose Requested/Explicit order or exclude that pair. Each change applies
immediately with Undo; **Reset relationship** removes the override. Requested
order must agree with geometry; Explicit order still undergoes independent validation.

For a local influence, choose **Select support footprint…** after setting an order. Click
covering faces to toggle a green draft; Accept or Cancel completes the gesture. An empty
region means the entire footprint. Stacking preserves qualified exact constraints and
fixed backing, supports multiple providers and evaluates provider-first chains. It does
not guarantee that arbitrary intersecting anatomy or contradictory orders can be repaired.

## Understand status and save

Live, On Release and Manual modes work through the existing coordinator. Outside-workspace
consumers continue at lower priority. Pending calculations keep accepted geometry visible.
The Activity panel shows work; Issues shows actionable failures and convergence warnings.

- Intrinsic failure retains the last accepted geometry.
- Stacking failure displays current **unstacked** geometry. It does not publish a successful
  Final surface; Final-bound consumers retain their output and report the prerequisite error.
- Iteration limit can publish a usable warned result. A newly self-intersecting or collapsed
  relaxed candidate is rejected. Reduce/change parameters explicitly; defaults do not promise
  a valid Pouch for every source. The software does not silently substitute another solver.

Save/checkpoint choices are unchanged. Schema 4 embeds definitions, fields, relationships
and accepted results; earlier schemas, including 0.2.1 projects, are rejected. Opening a
saved document does not trigger blanket recomputation. Product export remains skin-only.

## Repeatable headless example

From the portable application folder, run:

```powershell
./AnthroForge.exe --cli run examples/tissues.json
./AnthroForge.exe --cli inspect tissues.anthroforge
```

The example imports the included cube, creates two stacked surface tissues, a Fiber-based
Rim and an Anchor-based bulk bound explicitly to a final tissue surface. It saves a schema-4
document using the same operations as the desktop. See [API reference](authoring_api.md)
for individual commands. The example demonstrates construction, not anatomical fitting.

For performance investigation, press Shift+F12 before the interaction and again afterward.
Share the `.afprofile.zip`; it includes task stages, invalidation reasons, native calls,
cache activity and retained-resource ownership. F12 remains bug/recommendation reporting.
