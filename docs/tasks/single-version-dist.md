# One distribution per version

- Task branch: `codex/single-version-dist`
- Integration branch: `main`
- Starting revision: `7e1adb1`
- Status: complete; validated workflow correction
- Date: 2026-10-19, Europe/Bucharest

## Outcome

The user requests no multiple distributions of one version. The packaging default now
uses `dist/<version>/AnthroForge.dist`; repository rules prohibit feature/task suffixes.
The existing source-archive default already uses one archive per version. Temporary
qualification copies belong under build/ or the OS temporary directory.

## Existing installations

Read-only inspection found running executables in both `dist/0.2.1-reports` and
`dist/0.2.1-surfaces-reports`. Those installations were left intact to preserve active
sessions. No app was closed, no release deleted, and no new distribution was built.
Consolidation of those running folders was not performed. The README retains its valid
link to the installed latest build and explicitly identifies the historical layout.

## Verification and delivery

Validated the default path and temporary override by importing the packaging module;
neither check created output folders. `tools/check.ps1` passes: 930 tests, three native
CTests, Ruff/format, mypy, native analysis, function limits and native/numerical checks.
Log: `build/single-version-dist-gate.log`. Existing Qt deprecation warnings remain.
This changes delivery configuration, not application behavior, so no executable rebuild
or new distribution was produced. The unrelated __init__.py remains untouched.
