# Bundled AVBD runtime

- Task branch: `codex/bundled-avbd-runtime`
- Integration branch: `main`
- Starting revision: `ec2f786b`
- Status: implementation, validation and canonical delivery complete; ready for main integration
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
- BR-7: Final review found build-metadata deletion could select development discovery.
  Use Nuitka's documented module `__compiled__` marker as well as build metadata. Two
  regressions failed before the one-line correction; the packaged damaged-bundle check
  removes build identity too. The final compiled package passed this regression check.

Official references: [CPython Windows embedding](https://docs.python.org/3.12/using/windows.html#the-embeddable-package),
[Qt deployment](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html),
[Nuitka standalone guidance](https://github.com/Nuitka/Nuitka).

## Current state and next steps

The complete development gate passed: 3,010 Python tests, six CTests, Ruff, mypy across 712
source files, native/PowerShell style, 186 QML files / 46 model types, numerical checks and
native doctor. The full suite began before the final compiled-marker guard; after that change,
29 focused AVBD/runtime/checkpoint tests, lint and typing passed. Both new guard regressions
failed before the fix and passed afterwards. Packaged and normal-window acceptance were
repeated on the final clean build revision `59adb7a4`.

A reused, deployment-mutated PySide spec was rejected by its safe-path check during an earlier
rebuild; regenerating it through the normal configuration function resolved that attempt.

Relocated executable: minimal-PATH generation passed for root SCP, attached limb and VCP.
The final portable pipeline check passed fresh construction, damaged-runtime failure with
missing build metadata and retention of accepted Draft, checkpoint reuse despite an invalid
external override, ordinary save and Final deformation with fixed Draft/topology/reference.
All 8,536 runtime files match their manifest; 1,166 file-backed imported modules stay within
the private image. No files were added or changed by generation.

Canonical package promoted to `E:/development/anthroforge/dist/0.4.3/AnthroForge.dist`.
Executable revision: `59adb7a4a62b9267fb4df8e3e5247acee57b7001`, clean tracked source.
Executable SHA-256: `5e2c8ca3a2c1a994b888a8157a456b8b61efb92337922e9c1d1c1d6c37c3a0e3`.
Previous complete package retained at `build/bundled-avbd-delivery-20261127/previous-build`.
The earlier qualified candidate is retained in that directory's `pre-guard-build` sibling.
Normal launch without arguments/environment setup passed: open embedded bone/muscle fixture,
select AVBD in the UI, observe changed skin and current/applied status, save. Saved GUI mesh:
690 finite vertices / 1,376 triangles. The final headless fixture has 1,054 quads. The saved
test app was closed. The user's original project was saved and closed by the user before
replacement; unrelated source changes and prior packages were preserved.

The matching `dist/AnthroForge-0.4.3-source.zip` was refreshed and its complete ZIP integrity
checked. It includes the compiled application source, exact AVBD source archive, dependency
notices and manifest. Subsequent qualification-document edits do not change compiled code.

Exact runtime input revision is `b3b92969a39dbf4d1322e4f376f26fd425006445`, with independently
dirty source inputs recorded by file hashes and preserved in the corresponding source ZIP.
Build logs are local-only under the implementation checkout's `build/bundled-avbd-review`;
portable/GUI evidence is under `E:/development/anthroforge/build/bundled-avbd-release-check`.
The first prototype source-archive experiment included unnecessary Boost test/docs data and
was stopped; the qualified bundle archives the used headers/licenses instead.
Final evidence: `pipeline-final/qualification.json`, `normal-launch-final-accepted.png`,
`normal-launch-final-accessibility.txt`, `normal-launch-final.anthroforge` and
`saved-final-mesh-results.json`. These ignored artifacts are local-only.
Remaining: commit/push the final qualification record and merge/push main; verify remote
ancestry. Native solver/GPU requirements are unchanged; these small fixtures do not establish
whole-body numerical quality or compatibility with other GPU architectures.

## Recovery inputs

Implementation checkout: `C:/Users/alexe/.codex/worktrees/general-agent-instructions/anthroforge`.
Shared build venv: `E:/development/anthroforge/.venv`; app native build: `build/skin-pipeline`;
Qt SDK: `E:/development/anthroforge/.tools/qt/6.12.0/msvc2022_64`.
Qualified external runtime: `E:/development/anthroforge/build/application-boundaries`.
Treat that independently dirty runtime and the main checkout's unrelated assembly changes
as read-only. Check current canonical app processes before replacing the package.
