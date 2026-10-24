# Shortcut comparison and reproducible reports 0.3.2

- Branch: `codex/shortcut-comparison-032`; integration: `main`; baseline: `fb299ed`.
- Status: implementation in progress; local desktop writer, no delegated agents.
- Preserve unrelated root `__init__.py`. Background-only checks; no visible test windows.

## Confirmed contract

One explicit session-only baseline, captured immediately from accepted outputs. Preserve
pending/failed/provisional status. Before/After use the current camera/workspace; Overlay
adds non-pickable historical geometry. Shortcut edits switch Before to After without
interrupting gestures. Capture replaces atomically; clear/reopen/close release ownership.
No document schema, numerical algorithm, attachment or scheduler-policy changes.

Extend inspection export and existing bug reports. Default evidence includes frozen
before/current state, comparable images, formula/policy/status evidence and differences.
Replay is opt-in: complete starting project, shortcut gestures, explicit recalculation,
transaction boundaries, timing and execution preferences. Unsupported authored edits,
undo/redo, changed execution preferences or initial active work mark replay incomplete.
Journal cap: 10,000 events / 16 MiB. Replay is explicit in an isolated session/process,
never automatic; validate paths/checksums/versions/operations. No deterministic scheduling claim.
Existing report text edits/deletion preserve/remove all attachments. Old reports remain readable.

## Implementation order

1. Baseline ownership, native comparison, shared capture/inspect/clear operations.
2. Desktop modes and staged historical rendering, then focused interaction checks.
3. Frozen report extensions and streamed feedback attachments.
4. Bounded recording and isolated replay through shared operation/transaction boundaries.
5. Production preservation/profile, full gate, portable qualification and canonical delivery.

Public additions: `shortcut.comparison.capture`, `.inspect`, `.clear`; comparison/replay
options on `inspection.export`; `inspection.replay`. Reuse the current read-only coordinator,
frozen inspection contexts, resource leases, native numerical work, controls and theme.
Keep functions within 15 physical lines. Record computational boundaries in CH history.

## Verification and delivery

Pending. Cover lifecycle, modes, journal completeness, archives and reports, resource release,
headless/no-Qt operation, background native renders and actual packaged workflows.
Production controls: Ribs, Humerus, Radius, Thumb in the 96-muscle assembly; preserve current
standalone results. Deferred addon parity discrepancies remain outside scope.
Release only after qualification: `dist/0.3.2/AnthroForge.dist` and companion source archive.

## Recovery

Read this record, AGENTS.md and engineering guidelines. Current first step is foundations.

Foundation checkpoint: session baseline ownership, comparison operations, native mesh/path
fingerprints, and bounded semantic journal implemented. Ten focused tests and configured
mypy pass; native build has five passing CTests. No desktop modes/export/replay delivery
claimed. Next: desktop staged historical geometry and controls, then frozen archives.

Desktop/export checkpoint: Before/After/Overlay and shared capture controls are connected;
background native-render harness verifies mode switching and clear/release. Frozen exports
include paired images, comparison evidence and SHA-256 member checksums. Optional replay
uses an isolated session and in-memory preferences with a strict operation whitelist.
Feedback drafts freeze evidence on opening; generic file attachments stream through the
consumer. 27 focused tests pass. Remaining: real export/feedback UI qualification, broader
lifecycle/security coverage, production profile/preservation, full gate and packaging.

## Qualification progress

- Core gate: 2,044 tests and five native CTests passed before final hardening; configured
  typing, native/script style, numerics and doctor passed. Final suite is running.
- Real background D3D11 rendering, paired-image export, isolated replay and feedback
  attachment generation run through tools/shortcut_comparison_acceptance.py. Existing
  feedback UI regression passes offscreen. No physical interactive acceptance claimed.
- Production native comparison initially failed on ControlResult (no surface asset).
  Fixed the generic geometry-availability query at its owning boundary; regression added.
- All four 96-muscle cases now compare successfully. Baseline capture 24–37 ms; explicit
  background comparisons 431–587 ms. Coordinates, poses, bindings and oriented connectivity
  match qualified 0.3.1 evidence. Thumb triangle enumeration alone differs as before.
  See build/shortcut-comparison-profile/preservation.json and four afprofile archives.
- Source version is now 0.3.2 for packaging qualification; release/merge not yet complete.
- Review: properties/document state stay independent; native comparison owns bulk scans;
  feedback attachment storage remains consumer-independent. Historical geometry never
  enters picking. Report resource attribution includes baseline, exports and draft leases.

Final source review: full suite passed 2,045 tests. Added two more regression cases for
replay respecting an already-open output project and cancellation during snapshot writes.
Snapshot serialization now wraps its existing writer with bounded cancellation checks;
format and numerical arrays remain unchanged. Final package rebuild includes these fixes.
