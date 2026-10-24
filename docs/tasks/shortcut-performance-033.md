# Shortcut performance 0.3.3

- Branch: codex/shortcut-performance-033; baseline: 31fc158; integration: main.
- Status: implementation started. Preserve unrelated root __init__.py.
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
