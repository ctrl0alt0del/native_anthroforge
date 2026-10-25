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

The existing application is 0.3.6. No runtime changes yet. Inspect project load/save,
background file work, checkpoint lifetime, Preferences and shared QML sizing first.
Autosave destination/behavior is pending user clarification: separate recovery copies
(proposed default: every five minutes, latest committed state) versus overwriting the
named project when calculations finish. Continue Recent Projects and layout inspection
independently while awaiting that decision.

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

1. Inspect persistence/Preferences contracts and settle autosave behavior.
2. Implement and validate integrated project continuity services and UI controls.
3. Measure layout defects, fix owning controls, qualify and package 0.3.7.

No external project migration or geometry algorithm changes are requested.
