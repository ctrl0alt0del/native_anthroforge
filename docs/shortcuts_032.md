# Shortcut comparisons and reproducible reports (0.3.2)

Select a shortcut, expand **Inspect shortcut → Compare changes**, and choose **Capture
baseline**. This stores one session-only snapshot of accepted outputs immediately.
It does not wait for calculations, edit the document, or create an undo entry.
Capturing again replaces it. Opening another document or closing the application clears it.

**Before**, **After**, and **Overlay** use your current camera and workspace. The historical
geometry is read-only and cannot participate in picking, snapping, or attachments.
Before retains the current view while historical chunks are staged. Editing a shortcut
switches back to After without cancelling the gesture. Clear releases the baseline;
exports and rendering retain their own resources until finished.

**Compare geometry** runs an explicit background comparison. Reports distinguish added,
removed, moved, and geometry-changed objects by stable identity. Mesh fingerprints compare
stored vertex coordinates and oriented triangulation while ignoring triangle enumeration.
Path fingerprints include stored sampled paths. This is exact change detection, not a
vertex correspondence, displacement measure, tolerance test, or geometric-equivalence proof.
Changes in sampling can therefore count as geometry changes even with a similar shape.

## Sharing a report

**File → Export inspection report** includes the active baseline automatically. The report
contains `before.png` and `image.png` (After), captured with the same camera/projection,
plus values, formulas, attachment policies, readiness, Issues, and object differences in
`inspection.json`. `manifest.json` identifies the format/version and SHA-256 checksums.
Selection that did not exist in the baseline is omitted from the Before image.
Without a baseline, the existing single-image inspection format remains available.

The bug-report dialog freezes comparison evidence when the draft opens. **Include comparison**
is selected by default when a baseline exists; it can be unchecked. The resulting
`comparison.afinspection.zip` is streamed into the ordinary `.afreport.zip`. Editing a
report description preserves its attachments; deleting the report removes them too.

**Full starting-project replay is always opt-in.** Enable it in the comparison controls
for direct export, or in the bug-report dialog. It includes all starting-project contents,
not just the selected anatomy. Review that choice before sharing. It adds
`starting.anthroforge` and a bounded `replay.json` semantic journal.

Replay records shortcut edits, gesture boundaries and explicit recalculation. Other authored
changes, undo/redo, execution-preference changes, a baseline captured during active work,
or an unfinished gesture mark it incomplete. The limit is 10,000 events / 16 MiB; reaching
it is reported rather than silently truncating a reproducible sequence. Incomplete captures
are still useful comparison evidence, but the replay operation rejects them.

Replay is explicit, in an isolated headless session with in-memory preferences. It validates
archive members, size limits, checksums, format/application versions, and the operation
whitelist. It neither opens external projects from journal commands nor mutates the active
document. Execution follows semantic order; recorded timing does not guarantee identical
thread scheduling. New geometry-result identities may differ even when shapes match.

## Shared API

```python
session.command("shortcut.comparison.capture", shortcut=shortcut_id)
session.command("shortcut.comparison.inspect", refresh=True)
comparison = session.command("shortcut.comparison.inspect", wait=True)
session.command("inspection.export", path="comparison.afinspection.zip",
                comparison=True, replay=True, wait=True)
session.command("shortcut.comparison.clear")
replayed = session.command("inspection.replay", path="comparison.afinspection.zip")
```

`inspection.export` defaults to `comparison=True, replay=False`. Replay optionally accepts
`output` to save its isolated result; it never implicitly overwrites the current project.
Capture/inspect/clear and replay are Qt-free. Image export invokes the existing isolated
desktop renderer. Cancellation/failure leaves an existing destination intact and retains
the baseline for another export.

## Ownership and validation

The application comparison service owns accepted snapshots and the bounded journal;
the existing coordinator runs read-only native comparison/export jobs. C++ owns bulk
fingerprinting. Desktop models own independent historical rendering leases. Generic
feedback attachments depend on files and streams, not anatomy or the local inbox.
Profiler resource attribution includes comparison baselines, exports and feedback drafts.
No geometry algorithms, attachment policies, scheduling priorities, or schema-5 persistence
behavior change in this release. Historical baseline state is never saved in projects.

Qualification evidence and limitations are maintained in
[the delivery record](tasks/shortcut-comparison-032.md).
