# Bundled AVBD runtime

- Task branch: `codex/bundled-avbd-runtime`
- Integration branch: `main`
- Starting revision: `ec2f786b`
- Status: investigating runtime dependency closure
- Last updated: November 27, 2026, Europe/Bucharest
- Active writer: desktop AVBD packaging chat

## Outcome

The version 0.4.3 portable app must generate AVBD skin when launched normally, without
environment variables or a separate worktree. Rebuild and replace the canonical package
in `E:/development/anthroforge/dist/0.4.3/AnthroForge.dist`, refresh its source archive,
and verify actual GUI generation as well as isolated runtime/package checks.

## Diagnosis and decisions

- BR-1: The app currently bundles only its checkpoint adapter. The selected external
  runtime contains Python orchestration, native SCP/VCP solvers and numerical packages.
  Bundle the complete required runtime image; preserve the qualified algorithms and
  worker process isolation rather than substituting a different skin builder.
- BR-2: Package discovery must resolve the bundled runtime first and fail clearly if
  incomplete. Development overrides may remain for source runs; a packaged application
  must not silently depend on those overrides or an editable Python installation.
- BR-3: Build inputs may come from the already-qualified runtime during packaging, but
  all runtime inputs must be copied, identified and checked in the output. Exact source
  provenance, dependencies and notices must accompany the bundle and source delivery.
- BR-4: Do not copy the development venv wholesale: its launcher/editable paths depend
  on this machine. Assess a relocatable private interpreter plus pinned numerical packages
  or a compiled worker, using observed dependency and subprocess requirements.

Official references: [CPython Windows embedding](https://docs.python.org/3.12/using/windows.html#the-embeddable-package),
[Qt deployment](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html),
[Nuitka standalone guidance](https://github.com/Nuitka/Nuitka).

## Current state and next steps

Initial import tracing found runtime skin orchestration, native/core/application helpers,
NumPy/SciPy and visualization-library imports. Native program paths are relative to the
runtime root. Resolve the executable/DLL and subprocess module closure, choose the portable
layout, add discovery and package tests, run generation with sanitized environment and
no source checkout on the module path, then perform normal-launch GUI acceptance.

## Recovery inputs

Implementation checkout: `C:/Users/alexe/.codex/worktrees/general-agent-instructions/anthroforge`.
Shared build venv: `E:/development/anthroforge/.venv`; app native build: `build/skin-pipeline`;
Qt SDK: `E:/development/anthroforge/.tools/qt/6.12.0/msvc2022_64`.
Qualified external runtime: `E:/development/anthroforge/build/application-boundaries`.
Treat that independently dirty runtime and the main checkout's unrelated assembly changes
as read-only. Check current canonical app processes before replacing the package.
