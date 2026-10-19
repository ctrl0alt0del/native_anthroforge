# Selection-based surfaces and report browser

- Task branch: `codex/surface-report-browser`
- Integration branch: `main`
- Starting revision: `7af77fd`
- Status: complete; validated for normal merge
- Last updated: 2026-10-19, Europe/Bucharest
- Active writer: desktop chat, direct work

## Outcome and acceptance

Extend the Patch toolbar action: one closed curve creates a patch; two or more
selected curves/fibers create a standalone loft surface. Preserve source validation,
closed-loop correspondence preview and accepted asynchronous creation selection.
Add Help access to existing feedback reports, description/screenshot preview and
explicit deletion and atomic description editing (user follow-up). Keep the local inbox
independent of app versions and replaceable.

## Decisions and relevant files

Surface construction already exists in shared operations; desktop creation routing
owns the selection-dependent entry point. Reports previously supported submission only;
the separate inbox contract adds read/edit/delete without widening submit-only consumers.
Keep filesystem/archive work off the UI thread and use a
bounded scrolling report list. See engineering guidelines and feedback_reports.md.

## Current state

Implementation is complete. Source offscreen acceptance covers two/three-curve creation,
closed preview, 120 virtualized report rows, screenshot/description preview, text
edit/cancel/failure/retry, delete/cancel/failure, refresh and empty state. Existing
untracked root __init__.py remains untouched. Code checkpoint is `31f9015`.
Gate, clean package and relocated portable qualification passed. Source archive and
bundled documentation are finalized during delivery. Previous distributions are retained.

## Verification

Official Qt ListView/reuseItems and Qt Quick performance documentation reviewed.
Full `tools/check.ps1` passes: 930 tests, three native CTests, style/typing/function limits,
numerical imports and native doctor. Existing Qt constructor deprecation: 272 warnings.
Actual QML passes normal,
1050×680 and 200% scale report browsing, plus existing capture/annotation regression.
Native hidden QQuickRenderControl/D3D11 surface render, picking and retained replacement
checks pass; captures were inspected. No visible windows or desktop input.
Source feedback probe previews, edits and deletes only an isolated QA copy successfully.

Evidence: `build/report-browser-final-small/`, `build/report-browser-edits-hidpi/`,
`build/surfaces-reports-probe/`, `build/surface-reports-editor-final.log`,
`build/surface-reports-render.log`, `build/020-surface-scene/`.
Full logs: `build/surfaces-reports-gate.log`, `build/surfaces-reports-package.log`.
Portable: `uv run --no-sync python tools/check_portable.py <relocated-exe>
build/surfaces-reports-portable --offscreen` passes all checks. The executable was copied
to `%TEMP%/anthroforge-surfaces-reports-31f9015/application`; native DLLs load from that
copy with minimal PATH. `feedback-probe.json` confirms preview, edit and deletion.
The packaged browser capture was inspected. The final source archive is
`dist/AnthroForge-0.2.1-surfaces-reports-source.zip`.

Ownership review: UI surface choice delegates to existing validation and jobs, and
accepted selection observes existing output ownership. Inbox protocols remain Qt-free
and separate from delivery. Worker requests own immutable I/O inputs and one image;
report operations cannot change document revisions, scheduling or history. No idle
polling, per-report screenshot retention or numerical algorithm changes were introduced.

## Next actions and blockers

No remaining implementation or qualification blockers. Deliver the portable folder
`dist/0.2.1-surfaces-reports/AnthroForge.dist`; do not launch a visible app while the user
is using the computer. Inspect Git history for the final validated merge/push identity.

The first narrow-window harness timed out with a Python archive worker still running;
the same 120-entry scan took 36 ms without the harness. Replacing repeated QTest.qWait
with a bounded QEventLoop (matching application GIL release) passes. No production I/O
workaround was added. Explicit UTF-8/LF normalization corrected one inserted menu ellipsis
and accidental doubled CRLF before packaging; the final main-window diff is six lines.

## Recovery inputs

No external assets required. Use isolated temporary report inboxes for deletion tests;
never delete the user's actual reports as part of acceptance.
