# Authoring/UI functionality validation — 0.4.3

- Branch: `codex/authoring-parity-043`; integration: `main`.
- Baseline: `3daa3dee`; writer: local direct work.
- Status: inventory and behavioral audit in progress.

## Outcome

Validate that the public Python/JSON authoring interface supports the functionality
exposed by the desktop UI. Trace UI operations to shared application boundaries,
exercise equivalent workflows and restrictions, and correct demonstrated API gaps.
Keep numerical algorithms and authored semantics unchanged. Distinguish transient
desktop presentation/OS integration from document authoring; report any scope ambiguity.

Follow engineering guidelines, 15-line functions, background-only checks, task checkpoints
and validated merge. Preserve unrelated root `__init__.py` and all user project files.
No subagents or Jira workflow. Target release is 0.4.3; version/package changes follow
qualification, with one canonical executable and companion source archive.

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

Next: build UI/API inventory, identify concrete unreachable functionality and transport
differences, then validate/fix at shared owning boundaries. No parity claim made yet.
