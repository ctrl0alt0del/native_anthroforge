# Codex Cloud development

The same repository supports Windows desktop development and Linux cloud development.
Use Codex Cloud for code changes, numerical/core builds, the full pytest suite, captured
Blender parity fixtures, headless authoring and Python package builds while the PC is off.
The repository is `ctrl0alt0del/native_anthroforge`; the shared branch is `main`.

## Create the environment once

In Codex on web or the desktop app, choose **Work in > Cloud > Create environment**
(or **Settings > Codex Cloud > Environments > Create environment**). Select this repository
and request an Ubuntu/Debian Linux environment with root or passwordless sudo for setup.
Use a private environment; no application secrets or OpenAI API key are needed.

Supply this install command from the repository root:

```bash
bash tools/cloud/setup.sh
```

The script installs system/compiler libraries and pinned uv 0.9.29, then uses
`.python-version` (CPython 3.12.12) and `uv.lock` to install development dependencies,
NumPy and PySide6 6.12.0. It builds the C++17 library with the existing `portable-core`
preset and runs the validation gate. CMake compilation defaults to two parallel jobs to
bound memory use. Setup does not modify global shell profiles or change the lockfile.

Allow package-manager network access during setup. In addition to the package-manager
preset, allow `astral.sh` and `releases.astral.sh` for the pinned uv installer. The setup
also needs the configured Ubuntu/Debian apt mirrors, `pypi.org`, `files.pythonhosted.org`,
`github.com` and GitHub release download hosts for Python. A network failure must be fixed
in environment settings; do not disable TLS verification.

Review the setup results and **Publish** the environment. Open a new cloud task from it
and run the checks below to verify the published filesystem, not only the setup session.
If the interface has a startup skill/instructions field, use the new-shell and refresh
instructions below. No background application server is required. For the legacy interface,
use `bash tools/cloud/setup.sh` as setup and `bash tools/cloud/refresh.sh` as maintenance.

## Start or resume work

Read `AGENTS.md`, the confirmed specification and the engineering guidelines. In each new
shell, from the repository root:

```bash
source tools/cloud/environment.sh
uv run --no-sync anthroforge doctor --require-native
uv run --no-sync python tools/check_core.py --native-style
```

The environment file explicitly selects the repository Python environment and the built
native library. Child-process environment changes in the setup script do not persist into
later shells. Outputs stay in ignored `.tools`, `.venv`, `build` and `dist` directories.

After a branch change, new checkout or dependency update:

```bash
bash tools/cloud/refresh.sh
```

Refresh uses locked dependencies, rebuilds the native library and checks it loads. Run the
full gate before delivery. Codex repository refresh does not automatically rerun the install
command. If OS dependencies change, update/retest setup and republish the environment.

## What the gate proves

- Ruff, configured mypy and the authored 15-line Python function limit.
- C++17 build, exported native ABI and CTest contracts.
- Native function-size checks through clang-tidy when `--native-style` is supplied.
- The entire pytest suite, including Blender-reference fixtures, scheduling, save/undo,
  topology, deformers and Qt input-state contracts; tests are not skipped to make CI pass.
- A separate CLI workshop constructing/importing all primitive types, deformers and thickness,
  saving a document and reopening it in another process.
- Python wheel/source builds and packaged QML/type-marker resources.

`build/core/qualification/pytest.xml` and `passed.json` record successful qualification.
The latter includes source revision, platform, versions and lockfile digest. A previous
success report is removed before a new run. GitHub Actions runs the actual setup script
on Ubuntu 24.04 and the shared core gate on Windows. Those are remote CI results, distinct
from a verified Codex Cloud environment.

This setup does **not** build the Qt C++ viewport bridge or launch the interactive desktop.
Windows GUI gestures, GPU presentation/performance and portable executable qualification
still use `tools/check.ps1`, the GUI acceptance tools and Windows packaging. PySide6 is
installed because the full test suite exercises input adapters; numerical headless commands
still do not import Qt. A Python wheel is a development artifact, not a standalone executable.

Future numerical extras (SciPy, scikit-image, Instant Meshes and TetWild) are not required by
0.1.3 or this gate. If a task needs them, install with `uv sync --locked --extra desktop
--extra numerics`, then run `uv run --no-sync python tools/check_numerics.py`. Test that
expanded setup and republish it before relying on it; do not claim those extras were verified
by the baseline cloud gate. Blender and original production `.blend` files are not required
for the checked-in parity fixtures and are not copied from the PC automatically.

## Working through a power outage

Commit and push useful checkpoints before an outage. Only pushed code and explicitly provided
assets are accessible in the cloud; uncommitted PC work, local SDKs, personal skills and local
MCP servers do not appear automatically. Keep lasting decisions in repository documentation.
Start tasks from the published environment using Codex on mobile/web and review their diffs.
Commit/push completed work, then bring it into the local checkout when power returns. Respect
the repository rule requiring authorization for Git remote operations; this guide does not
grant blanket permission to future chats. Avoid concurrent edits to the same branch from both
environments, and do not force-push to reconcile them.

## Evidence and current account setup

The October 17 initial CI run failed Linux mypy on platform-specific file locking; the Windows
job was canceled by matrix fail-fast. The cloud preparation changes use mypy-recognized
platform guards, install the desktop test dependency and run independent platform jobs.
Record the successful qualification run in `development_status.md` once observed.

Creating/publishing the account's Codex Cloud environment is separate from repository setup.
The in-app browser sign-in currently reports an authentication failure. Until a real cloud
setup and fresh task have run, do not label the environment as published or Codex-verified.

References: [Codex Cloud environment setup](https://learn.chatgpt.com/docs/environments/cloud-environments),
[projects and file access](https://learn.chatgpt.com/docs/projects),
[uv installation](https://docs.astral.sh/uv/getting-started/installation/).
