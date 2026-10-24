# Mirroring in 0.3.5

Runtime implementation; final portable-package qualification is recorded in the
[task record](tasks/mirroring-035.md). The [confirmed contract](specification_035.md)
remains authoritative. Existing independent opposite-side objects are not paired or migrated.

## Desktop workflow

Select source anatomy and enable **Mirror children** in the Mirror section. Its
descendants and required construction receive read-only spatial instances. The owner
itself is not mirrored by its own rule. Use **Inherit parent mirror** for participation,
or enable a nested rule. Axis and shift describe a document/world plane in display units.
Conflicting construction inherits no arbitrarily chosen plane: use its explicit plane
override. Existing accepted placement remains while the conflict is reported.

Select mirrored geometry in the viewport to inspect it; **Select source** returns to
editing. Mirrors add no Anatomy or Construction tree entries. Read-only properties do
not mean dimmed display: only objects outside the workspace use context dimming.
The workspace Presentation section offers **Both sides**, **Source only**, and
**Mirror only**. Instance inspection offers Hide, Isolate and Show all. These choices
change presentation, not anatomy or computation.

Attachments retain roles and material bindings. **Use same target on both sides** is
an explicit midline-sharing choice. Missing counterparts and incompatible retained
anchors report Issues while the mirror keeps exact source geometry. Rule/source removal
is blocked by retained consumers; the dialog has search and navigation.

For a selected open Curve/Fiber, use **Symmetric construction** to choose an existing
rule or a shifted document-axis plane, then **Create symmetric loop**. Both endpoints
must already lie on that plane and the interior must remain on one side. Edit the
authored half; seam-point edits stay on the plane. A closed Fiber retains its ordinary
minimum-one-binding contract. Generated reflected points are not separate editable knots.

**Create mirrored-row surface** accepts one open row. Existing lofts expose **Use mirrored
rows** and plane controls. These create one complete source surface/Membrane, suppressing
redundant surface/tissue mirrors. Plane edits that rebuild row correspondence obey
topology locks. A later plane-row membership change retains accepted geometry and asks
for Realign; it cannot silently change an attached surface's topology. Branched mirrored
rows remain unsupported. Apply/Bake and Make Independent for instances remain unavailable.

Tissue stage comparison, point explanation, section queries and Check Geometry accept
instances. Footprint inspection reflects the corresponding source relationship; originals
may inspect another tissue's mirrored final provider. It does not solve mirror stacking.

## Shared operations

All are `Session.command` operations; desktop controls use the same validation.

| Operation | Arguments / result |
| --- | --- |
| `mirror.configure` | `target`, optional `enabled`, `inherit`, `axis`, `shift`, `override` |
| `mirror.list` | Optional `source`; instance identity/source/rule/plane/revision rows |
| `mirror.inspect` | `target`: source settings or read-only instance metadata |
| `mirror.source` | `target`: existing instance → source identity |
| `mirror.planes` | Existing rule/override planes for source construction |
| `mirror.attachment.inspect` | Instance `target`; retained counterpart mapping and findings |
| `mirror.attachment.share` | Authored `source`, binding key, Boolean `enabled` |
| `mirror.attachment.shared` | Authored `source`, binding key → Boolean |
| `mirror.removal.inspect` | `target` and proposed rule changes → affected consumers |
| `mirror.source.removal.inspect` | Authored `target` → retained-instance/plane consumers |
| `mirror.loop.create` | `curve`; optional `rule` or explicit `axis`/`shift` |
| `surface.create` / `surface.update` | `mirrored_rows`, `mirror_plane={rule,axis,shift}` |
| `view.hide` | `targets`, optional Boolean `hidden` |
| `view.isolate` | `targets`; isolates spatial identities in the current workspace |
| `view.show_all` | Clears per-instance/object hiding |
| `workspace.update` | `mirror_display`: `BOTH`, `SOURCE`, `MIRROR` |

Surface references are `{target, role, instance}`: `target` remains the authored source,
`instance` is its rule identity, and `role` remains `SCP_GEOMETRY`, `TISSUE_BASE` or
`TISSUE_FINAL`. Returned instance tokens are `mirror/<rule>/<source>`; prefer returned
identities. SCP reparenting accepts such a token while retaining its authored structural
parent and a distinct attachment-instance reference. No mirrored geometry writer exists.

Run the Qt-free example from the repository root:

```powershell
uv run --no-sync anthroforge run examples/mirroring.json
```

## Storage and numerical ownership

Project schema **6** reads schemas **4, 5 and 6** and saves 6. Existing source geometry,
engines, shortcuts and retained attachments are preserved. Older applications reject 6.
Rules, sharing choices, accepted conflict placements, symmetric definitions and workspace
presentation are stored; reflected geometry payloads, native handles and undo history
are not. Opening does not launch independent mirror calculations.

Core resolves identities, inheritance and required sharing. Application owns references,
read-only policies, dependencies, transactions and persistence. Native code owns numerical
reflection, seam constraints, row ordering and queries. Desktop uses cached projection,
shared resource leases and the existing staged publication/picking boundary. Negative
frames reverse render-only triangle indices to preserve lighting; authored/material
connectivity and native source geometry remain untouched.

## Evidence and limits

`tools/mirroring_qualification.py` creates hidden GPU captures and a normal runtime
`.afprofile.zip` under `build/035-mirroring`. Source/mirror images were inspected;
the initial dimming/winding defect was corrected and captures reinspected. Hover/click
agree on the displayed mirrored tissue. Plane edits preserve exact source arrays and
the trace contains no independent mirror inflation, routing or relaxation calls.
Repeated warm plane edits measured 121–343 ms including settling, refresh and eight
GPU frames/readbacks, under variable uncontrolled background load. This is not physical display/input latency or a hard responsiveness guarantee.

The existing 59-SCP/96-muscle assembly produced **620 instances in 49 ms**, settled
under **0.7 seconds**, allocated **zero new source geometry assets**, and reported no
scheduler errors in the headless rule-enable/profile experiment. The input was read
without a write lock and was not saved. This validates reflection/index reuse, not
anatomical correctness or the unresolved source/addon parity cases.

Tests cover retained bindings/plane updates, source removal, shared-target mismatch,
conflict persistence, exact stage frames, source-only stacking writers, on-demand findings,
read-only selection, independent hiding, loop seams, single-binding closed Fibers and
mirrored rows. A shifted stacking provider remains rejected when it contradicts fixed
receiver boundaries; mirroring does not weaken preservation constraints.

Offscreen evidence does not establish interactive acceptance on the user's desktop.
Qualification never takes over the desktop. See the task record for gate and packaged
results; historical Blender independently evaluated mirrors are an intentional difference.


## Ownership review

Reviewed the implementation separately from its test results: immutable mirror
identity/rule resolution lives in Core; application policies own reference safety,
read-only enforcement and source-only dependency aliases. Providers expose spatial
identity without fabricating SCPs. Numerical seam, frame and query work remains native.
Desktop projection shares source leases and uses the existing staged RenderModel;
render winding correction does not modify the document. Serialization stores metadata
and source results, with no mirrored asset catalogue or worker pool.

Shared cause fixes belong at those boundaries: measurements now resolve surface roles
and construction/stage frames consistently; shared-junction projection runs before
atomic member expansion. Existing algorithms remain authoritative for source geometry.
The mapping/index code intentionally handles relationship metadata in Python; native
geometry is batched. No blanket Qt dependency was added to Core or headless operations.


## Development qualification

The release-candidate development gate passes **2,102 Python tests**, all **five
native CTests**, typing (405 source files), configured style/function limits,
numerical checks and doctor. Log: `build/mirroring-035-gate-final.log`.
The complete portable executable is qualified separately; see the task record.
