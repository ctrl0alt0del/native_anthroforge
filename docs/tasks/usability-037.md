# AnthroForge 0.3.7 — Project continuity and UI polish

- Task branch: `codex/usability-037`; integration: `main`.
- Starting revision: `552afe2`.
- Status: in progress; not release qualified.
- Writer: direct desktop task; 2026-10-25 Europe/Bucharest.

## Outcome

Add Recent Projects to the menu, configurable periodic autosave in Preferences, and
another pass over cropped text and avoidable UI steps. Reuse shared persistence,
Preferences, project lifecycle and controls. Preserve save checkpoints, ownership,
undo and running edits. Validation remains background/offscreen only.

## Decisions and current state

The user confirmed separate recovery copies, including untitled projects, every five
minutes by default using the latest committed state. Preferences expose enable/disable
and a whole-minute interval. Keep three generated copies per project; no manual project
overwrite or dirty/undo changes. Recovery opening detaches the file and requires Save As.

Implemented first increment: bounded recent-project history, shared atomic JSON writing,
Qt-independent autosave scheduling through the existing coordinator, embedded recovery
metadata/retention, recovery discovery and desktop menu/Preferences controls. Normal
open/save safeguards remain authoritative. No geometry algorithms or format bump.

Thirty focused persistence/Preferences/architecture tests pass. Initial offscreen QML
smoke has no warnings; its platform-default fonts are unavailable offscreen, so use the
existing acceptance tools' explicitly loaded Segoe UI before visual qualification.
Complete recovery UI/gesture tests, broad layout inspection and release checks remain.

Official Qt Text, Control and Layout documentation is the initial sizing reference.
Prefer correct implicit sizes, wrapping where useful and stable reserved geometry;
do not mask controls with unnecessary elision or transient layout changes.

## Acceptance

- Recent project history persists, deduplicates, follows successful open/save, handles
  missing entries and uses the existing unsaved-change/open safeguards.
- Autosave honors configured interval, coherent committed state, document lifetime,
  no overlapping writes, no focus/gesture interruption and atomic persistence.
- Inspect actual QML at narrow/normal widths and enlarged display scale; exercise new
  controls and existing numeric gestures. Record offscreen evidence limits.
- Development gate, portable checks and one canonical 0.3.7 distribution/source archive.
- Preserve unrelated root `__init__.py`; checkpoint/push and validated merge workflow.

## Next actions

1. Complete actual recovery/recent UI tests and audit inspector/menu/dialog clipping.
2. Fix observed owning-control/layout defects; qualify autosave lifecycle and large files.
3. Run development/portable checks, document and package 0.3.7, then merge/push main.

No external project migration or geometry algorithm changes are requested.

## Layout and lifecycle checkpoint

Recent/recovery interactions pass in the real offscreen QML application. Ordinary
open and the unsaved-change prompt remain in use. Recovery opens as dirty/untitled
and is excluded from recent history. Named snapshots use the original filename.

Observed layout defects corrected at their owners: invisible menu rows no longer
reserve height; dialog titles wrap; deletion uses a searchable affected-object list
instead of an overflowing paragraph; primary object controls precede optional mirror
settings. Buttons expose their full label when truncated. Tests inspect narrow and
normal body/Fiber/surface/tissue layouts and keep search-field placement stable.

32 focused tests pass, including queued dispatch-time capture, non-overlap, cancellation,
active gestures, checkpoint saves, atomic failure and retention. Full gate, scaled
layout checks, production-sized recovery and portable packaging remain pending.

## Qualification candidate

- Large assembly recovery is Qt-free; all 12,561 package payloads match explicit saving
  byte for byte, including geometry and attachments. Profiler: 1.58 ms capture preparation,
  4.37 s background writing and 0.09 ms publication. This is one uncontrolled-load trial,
  not an FPS claim. Evidence: build/usability-037/assembly/.
- Offscreen interaction/layout audit passes at 150% scale too. The shortcut-policy probe
  reproduced rows requiring 170 px but fixed at 142 px, visibly overlapping descendant
  labels and controls. Content-sized rows and a scrollbar gutter fix the observed defect.
- Existing Preferences workflow passes; packaged recovery smoke added and source invocation
  passes, preserving manual-file bytes. Version metadata advanced to 0.3.7 for qualification.
- Full development gate running; portable build/suite, final docs and source archive pending.

## Packaged candidate and design review

- Canonical executable built successfully at clean runtime revision `a6e57ef`; subsequent
  changes are acceptance-tool coverage. All 140 packaged QML/native files match source.
- Source layout checks pass with a full 20-entry scrolling Recent Projects menu, explicit
  clear and unavailable-project opening; failure preserves the loaded document/path.
- The native gate passes five CTests and configured style. Full Python suite (2,241
  collected cases) and minimal-PATH portable qualification are running.
- Ownership review: recovery timing/capture and retention are application services; Qt
  only presents them. One coordinator owns execution and cancellation. Ordinary save
  policies remain intact, snapshots retain native resource owners, history is untouched,
  and recent history owns paths rather than project files. No new worker pool, geometry
  algorithm or project schema is introduced.
- First native relink encountered a temporary DLL lock during overlapping validation;
  serial retry after the GUI process exited succeeds. No user process was closed.

- Full portable suite passed, including compiled autosave/recovery and original-file
  preservation. Packaged Preferences/recovery captures inspected. No interactive desktop
  acceptance is claimed; all GUI work remained background/offscreen.
- Broad gate found one outdated failure-injection mock: corrupt_write accepted three
  arguments while storage now passes cancellation/recovery context. Updated the test
  double to match the extended writer signature. Its disk-failure preservation check
  and all 23 interleaving/autosave tests pass; no runtime correction was required.
- Aggregate Python rerun is in progress. Remaining numerical/doctor gate stages pass.
