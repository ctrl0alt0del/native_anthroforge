# Inspecting shortcuts (0.3.1)

Use the information/status button beside a shortcut, or **… → Inspect shortcut**.
The existing editor opens with its value still editable. Selected SCP/VCP and All
remain the only shortcut tabs. Expand the sections you need:

- **Affected anatomy:** direct targets and downstream outputs, searchable and paged.
  Locate navigates to the object or driving shortcut. Context objects remain read-only
  under the existing workspace rules. Influence means a dependency relationship; it
  does not claim that every affected object moved spatially.
- **Formula values:** expression, target, retained result, failure, current inputs and
  captured evaluation values. The evaluated expression and capture revision distinguish
  old accepted evidence from a newly edited expression. Prerequisite drivers are
  navigable; cycle participants are distinguished from downstream blocked formulas.
  Numerical evidence uses canonical metres/radians, independently of display units.
- **Attachment effects:** authored settings, initiating shortcut overrides, captured
  effective bindings and owner backsolve. Prospective policy is labelled as such;
  inspection does not capture new bindings or change attachment behavior.
- **Update details:** related active jobs, blockers, failures and published outputs.
  Completion includes downstream computation. Desktop additionally indicates geometry
  waiting to be displayed; the headless API makes no display claim. Historical pending
  input provenance remains available without pretending it is a currently running job.

**Show effects** is off by default. It highlights direct targets in gold and downstream
geometry in cyan. Authored anchor pairs are green; captured effective pairs are pink.
Anchor markers are shown only against matching displayed geometry/frame revisions.
The overlay cannot be picked and changes no selection, authored colors, visibility,
workspace, geometry, undo history or project data. Leaving the editor/panel clears it.

Status/details occupy fixed rows. Full elided diagnostic text appears on hover; pending
calculations do not insert rows above the numeric field. Optional sections expand only
through deliberate user actions.

## Shared operations

All clients use the same read-only operations with a stored shortcut or driver ID:

```python
session.command("shortcut.effects", shortcut=key, search="", offset=0, limit=100)
session.command("shortcut.formulas", shortcut=key)
session.command("shortcut.attachment_policy", shortcut=key)
session.command("shortcut.progress", shortcut=key)
```

Effects accept a nonnegative offset and a limit of 1–500. Unknown identities fail
explicitly. Inspection never starts an anatomical calculation. Anchor rendering uses
the existing cancellable read-only query service and native attachment queries.

Runtime observation retains the latest 64 edited shortcuts, up to eight influence
closures, and up to 1,024 formula input records (32 KiB of encoded inputs per record;
oversized evidence is explicitly unavailable). Active-job causal records live until
those jobs end. Captured evidence is unavailable after eviction, undo/redo or reopening;
current values are never presented as historical inputs. No geometry snapshots or
native handles are added to that evidence. Schema 5 and startup behavior are unchanged.

Comparison/replay reports and the deferred Ribs/Thumb parity corrections are outside
this release. [Qualification and limitations](tasks/shortcut-inspection-031.md).
