# Bundled AVBD runtime

- Task branch: `codex/bundled-avbd-runtime`
- Integration branch: `main`
- Starting revision: `ec2f786b`
- Status: implementation complete; package and full qualification in progress
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
  on this machine. Use the existing relocatable CPython 3.12.12 base with relative `._pth`
  paths and the installed wheel dependency closure. A second compiled worker was rejected
  because dynamic runtime imports and Python subprocess entry points would need invasive
  changes. Numerical sources and solver binaries remain unchanged.
- BR-5: Native helpers retain their internal relative layout inside the private image.
  Bundle app-local VC runtime DLLs, the qualified core native library and regional helper
  dependency. The worker strips Python/native overrides and uses only private/system PATH.
- BR-6: Package checkpoint identity uses the complete manifest, including interpreter,
  wheels, helpers and source provenance. It is independent of installation location.
  Old external-runtime checkpoints conservatively rebuild; accepted saved meshes survive.

Official references: [CPython Windows embedding](https://docs.python.org/3.12/using/windows.html#the-embeddable-package),
[Qt deployment](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html),
[Nuitka standalone guidance](https://github.com/Nuitka/Nuitka).

## Current state and next steps

Discovery/retention tests: 16 passed; application mypy passed. The private interpreter loaded
the AVBD dependency graph (1,231 modules) with only bundle-local import paths and a Windows-only
PATH. A fresh cube completed actual AVBD generation through the application pipeline using
the private runtime, publishing an accepted Draft and durable SCP checkpoint. This was a
source-app prototype check, not packaged or GUI acceptance.

Exact runtime input revision is `b3b92969a39dbf4d1322e4f376f26fd425006445`, with independently
dirty source inputs recorded by file hashes and preserved in the corresponding source ZIP.
Build outputs/evidence are local-only under `build/bundled-avbd-review`.
Remaining: full development gate, release build, relocated package verification and actual
normal-launch GUI skin generation; canonical promotion/source archive; merge/push main.

## Recovery inputs

Implementation checkout: `C:/Users/alexe/.codex/worktrees/general-agent-instructions/anthroforge`.
Shared build venv: `E:/development/anthroforge/.venv`; app native build: `build/skin-pipeline`;
Qt SDK: `E:/development/anthroforge/.tools/qt/6.12.0/msvc2022_64`.
Qualified external runtime: `E:/development/anthroforge/build/application-boundaries`.
Treat that independently dirty runtime and the main checkout's unrelated assembly changes
as read-only. Check current canonical app processes before replacing the package.
