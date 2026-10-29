# Authoring/UI functionality validation — 0.4.3

- Branch: `codex/authoring-parity-043`; integration: `main`.
- Baseline: `3daa3dee`; writer: local direct work.
- Status: findings documented; final verification in progress. No runtime fixes.

## Outcome

Validate that the public Python/JSON authoring interface supports the functionality
exposed by the desktop UI. Trace UI operations to shared application boundaries,
exercise equivalent workflows and restrictions, and document demonstrated API gaps.
Keep numerical algorithms and authored semantics unchanged. Distinguish transient
desktop presentation/OS integration from document authoring; report any scope ambiguity.

Follow engineering guidelines, 15-line functions, background-only checks, task checkpoints
and validated merge. Preserve unrelated root `__init__.py` and all user project files.
No subagents or Jira workflow. User clarified: **audit first; discuss fixes afterward**. Do not change application
behavior, package versions or executable distribution during this audit. Findings feed
the planned 0.4.3 release; qualification uses the current 0.4.2 runtime.

## Investigation

Read README, engineering guidelines, existing authoring API and command catalogue.
The desktop already delegates most edits to `Session.command`; numerical modules are
shared. Inventory must include indirect/dynamic dispatch, direct application helpers,
transactions, job control, queries, previews and persisted presentation—not only command
names or existing test counts. Static reachability alone does not prove behavioral parity.

Official references: [Qt separation of UI and business logic](https://doc.qt.io/qt-6/qtquick-bestpractices.html)
and [Qt Quick Test](https://doc.qt.io/qt-6/qtquicktest-index.html). Reuse the repository's
existing test/hidden-render infrastructure rather than introducing another framework.

## Recovery

Use `uv run --no-sync`. Qualified native build:
`C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native`.
Set `AF_NATIVE_BUILD` and `ANTHROFORGE_NATIVE_LIBRARY` consistently for numerical checks.
Temporary evidence belongs under ignored `build/authoring-parity-043`.

## Findings and checks

See [the audit](../authoring_audit_043.md). Static inventory: 364 registered operation
names, 308 literal UI calls / 244 distinct names, no missing literal operation names.
Manual review includes dynamic dispatch and direct application/resource helpers.
Six gap families: current editable state, candidate geometry inspection, contextual
choices/effective values, JSON literal strings, recovery/project-library lifecycle,
and user feedback operations. Existing numerical/application implementations remain intact.

Disposable probes reproduced the Fiber current/authored point distinction, `$` literal
failure, recovery ownership distinction, effective skin settings and candidate status
without candidate geometry. Tool harness corrections were required (asynchronous Fiber
creation returns a job ID; Controller selection needs refreshed models); these were
probe fixes, not application failures or production changes.

Existing relocated 0.4.2 executable passed all 35 portable workflow groups with offscreen
UI/hidden rendering. The packaged code revision is `b3d6f898`; later baseline edits are
typing/docs/tooling. Evidence is under ignored `build/authoring-parity-043`.
Full Python suite passed: **2,763 tests, 3577 warnings, 386.40 seconds**; log `pytest.log`
in that evidence directory. Warnings are existing dependency/Qt deprecations.
Next: finalize audit-tool lint/function limits and document links; record exact outcomes.
Then complete the docs/tools-only delivery without changing any runtime behavior.
