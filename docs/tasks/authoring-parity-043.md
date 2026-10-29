# Authoring/UI functionality validation — 0.4.3

- Branch: `codex/authoring-parity-043`; integration: `main`.
- Baseline: `3daa3dee`; writer: local direct work.
- Status: audit complete; fixes await discussion. No runtime changes or 0.4.3 release.

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
Final checks: repository-wide Ruff and formatting pass (1,602 files); mypy passes
(624 source files); final architecture checks pass, including the 15-line limit.
All 105 local links in the edited documents resolve; diff whitespace checks pass.
The full native rebuild/development gate was not rerun: this delivery changes only
documentation and standalone audit tools. Existing native runtime was exercised by
the Python and portable suites. No visible windows or desktop input were used.

## Ownership review and next action

Reviewed responsibilities independently of test outcomes. Document edits already enter
shared application operations. The remaining read-model gaps are not a justification
for duplicate algorithms in authoring, direct mutable resource publication, or a second
scheduler. Candidate snapshots belong to existing resource/inspection ownership; JSON
literal encoding belongs to transport; recovery and feedback retain runtime-service
ownership outside document history. Desktop-only presentation is identified explicitly.

Checkpoint `2098ed4d` is pushed. Final delivery includes only docs/tools; production
source, package/schema versions, canonical distribution and user projects are unchanged.
Preserved unrelated root `__init__.py`. Discuss A1–A6 in the audit before implementing
fixes; especially define headless autosave/reset and report-image inputs explicitly.
