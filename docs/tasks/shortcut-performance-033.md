# Shortcut performance 0.3.3

- Branch: codex/shortcut-performance-033; baseline: 31fc158; integration: main.
- Status: implementation and qualification complete.
  Preserve unrelated root __init__.py.
- Scope: optimize property UI invalidation, formula observation, redundant document
  reconstruction, then priority bookkeeping. No numerical or attachment behavior changes.
- Evidence: build/shortcut-profile-033/summary.json; four production controls, three
  recorded trials each. Headless medians 8.812/4.549/3.831/1.032 seconds.
- UI bounded sample: 6,330 property queries / 3.116 seconds; 9.022 seconds UI refresh.
- Diagnostic formula filtering: 82,096 to 142 checks, identical dirty sets and fingerprints.
- Preserve graph freshness, undo/redo, driven edit restrictions, topology locks, Manual
  provenance, cancellation and prerequisite urgency (including Ulna).
- Validate each boundary with behavioral regression tests, repeat production profiler and
  exact geometry/attachment comparisons; full gate, background UI/native rendering,
  portable checks. Deliver one canonical 0.3.3 package and source archive after qualification.
- No visible desktop interaction. No delegation. Research: Qt Quick performance guidance
  https://doc.qt.io/qt-6/qtquick-performance.html .

## Implementation checkpoint

Property metadata has independent QML subscriptions with hidden-field gating and bounded
metadata/identity caches. Shared property policies still decide writability. A session-owned
reverse formula read index conservatively narrows candidates; structural changes retain
full evaluation checks. Unchanged shortcut contexts no longer reconstruct documents.
The active job registry maintains provider/consumer links; urgency ranking/donation remains
unchanged. Focused UI, formula, attachment and priority tests pass; mypy passes. Production
performance/preservation, full gate and packaging remain pending.

## Qualification checkpoint

Three serial paired trials for four production controls preserve coordinates, poses,
bindings and oriented connectivity. Median headless reductions: Ribs 16.9%, Humerus
18.6%, Radius 20.5%, Thumb 2.9% (small/no strong claim). Baseline 31fc158, candidate
ab802e9 plus metadata project-reset hardening; same native library. Thumb retains its
existing triangle-enumeration nondeterminism. Ulna remains around 1.8 seconds in inspected
Ribs traces. Raw data: build/shortcut-performance-033/{trials,headless-summary.json}.

Desktop ABBA bounded 30-tick runs average 14.694 -> 10.362 seconds; 492 active jobs
remain in each, errors empty. Metadata work falls from 6,330 calls/3.38 seconds to zero.
This is partial offscreen application-boundary evidence, not displayed FPS or total time.
Four metadata tests and background editor/native texture update/undo checks pass.
Gate and canonical package build are running; logs in build/shortcut-performance-033.

Ownership review: caches/indexes stay in desktop, session and active registry respectively;
none owns numerical algorithms or changes publication guards. Graph signatures include
formula target/input/enabled changes. Registry mutations update both link directions.
Metadata records are retained only for watched IDs in the current document (including
undoable deletions); entries/epochs reset across documents. No geometry resources are
copied into the metadata cache. Native computation, schema, undo/save and urgency rules
remain unchanged. Source render needs the Windows platform for hidden D3D11; the Qt
offscreen platform alone cannot initialize that GPU renderer.

## Final qualification

- Full tools/check.ps1 passed: 2,056 tests, five native CTests, Ruff/format, strict typing,
  native/script style and numerical smoke checks. Gate log records existing non-failing
  native warnings and Qt property-map deprecation notices.
- Canonical 0.3.3 executable passed all minimal-PATH portable workflows, including native
  images, attachments, tissues, profiling, comparisons and isolated replay.
- Relocated compiled QML harness passed driven-property removal and undo subscription
  checks. Source editors passed lock/unlock, numerical units and navigation checks; the
  texture-only D3D11 scene passed consumer update and exact undo. Captures were inspected.
- Both pre-edit and post-edit fingerprints were checked across every paired production
  run; all coordinates, relationships and oriented connectivity match. No source project
  was overwritten. No interactive desktop or physical latency acceptance is claimed.
- Runtime code is captured by 7af1946; package staging records ab802e9 with tracked changes
  because the qualification checkpoint was committed during compilation. No runtime code
  changed after staging; final changes are documentation only.
