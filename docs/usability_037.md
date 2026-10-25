# AnthroForge 0.3.7 — Project continuity and UI polish

Status: implemented and runtime-qualified as 0.3.7.

**File → Recent Projects** keeps the latest 20 successfully opened or saved projects
across launches. Entries show their folder and expose the full path on hover. Opening
uses the existing unsaved-change prompt; an unavailable path reports an error without
discarding the current document. Clear removes history, not project files.

**Edit → Preferences → Projects** enables recovery autosave and sets a whole-minute
interval from 1 to 1440. The default is enabled, every five minutes. This is a runtime
preference shared across projects. It creates separate copies, including for untitled
projects, under `%LOCALAPPDATA%/AnthroForge/Autosaves` (beside the preferences file when
its location is explicitly overridden). The latest three copies per project are kept.

Autosave never overwrites the manual project, clears its unsaved flag, commits a gesture,
or changes Undo. The coordinator captures the latest committed revision when the job
actually starts. Pending/running calculations use the existing checkpoint; an active
gesture can require an earlier committed revision. Unchanged or already manually saved
revisions need no new copy. Only one recovery write runs at a time; busy workers can
delay a scheduled save. Failed saves report an error and retry on a later interval.

**File → Recover autosave…** or the Preferences button opens a searchable recovery list.
Opening a copy uses the normal unsaved-change prompt, then detaches it from its recovery
filename and requires **Save As**. It does not replace the original or add the recovery
filename to Recent Projects. Copies are ordinary project packages with small embedded
recovery metadata. They survive restart; this is periodic recovery, not a guarantee of
preserving changes made after the latest completed copy.

UI corrections include wrapped dialog titles, a searchable list of affected objects in
deletion confirmations, no blank rows from hidden menu items, and full-label tooltips
for clipped buttons. Primary object controls appear before optional mirror settings.
Shortcut attachment-policy rows grow for long descendant names instead of overlapping.
Preferences scroll at shorter window heights. Search/filtering does not move the delete
dialog's input. Existing confirmation restrictions, editing and calculation behavior remain.

## Evidence and limits

Focused tests cover committed capture, active gestures, queued dispatch, non-overlap,
cancellation, retention, atomic failure and retry, preferences and recent history.
Offscreen interaction tests exercise actual menus, Preferences, recovery and the existing
unsaved-change prompt. Layout captures cover 1440×900 and 1050×680 windows, minimum-width
inspectors, long names and 150% scale. Dynamic names in the outliner intentionally elide;
complete names remain available. Offscreen captures do not certify physical desktop use.

The production assembly (59 SCPs and 529 construction/tissue objects, including 96 muscles
and 326 Fibers) round-trips all 12,561 serialized payloads exactly. The runtime profiler
measured 1.58 ms preparation, 4.37 s background execution and 0.09 ms publication in one
uncontrolled-load run. These are task timings, not frame latency or a speedup comparison.
Core recovery runs without Qt. Schema 6 and all numerical geometry algorithms remain
unchanged. Development checks pass 2,241 Python tests, five native CTests, configured
style/typing and numerical/runtime checks. The full minimal-PATH portable suite passes,
including compiled recovery capture, discovery and original-file preservation. Packaged
Preferences and recovery captures were inspected. The runtime build is `a6e57ef`;
later changes concern acceptance tools, a test-double signature and documentation.
Gate and executable evidence are tracked in the
[task record](tasks/usability-037.md).

Delivery uses one `dist/0.3.7/AnthroForge.dist` and one
`dist/AnthroForge-0.3.7-source.zip`.
