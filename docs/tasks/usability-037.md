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
