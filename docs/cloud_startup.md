# AnthroForge Standalone startup

Use the existing checkout at /workspace/native_anthroforge. At the beginning of every new
chat, before editing, refresh and read the current repository workflow without waiting for
a user reminder. The published filesystem and previously loaded instructions may be stale.

First inspect the checkout and confirm origin identifies ctrl0alt0del/native_anthroforge:

```bash
cd /workspace/native_anthroforge
git status --short --branch
git remote get-url origin
```

Then fetch and read a consistent revision of the latest integration-branch guidance:

```bash
git fetch origin
af_guidance_revision=$(git rev-parse origin/main)
git show "${af_guidance_revision}:AGENTS.md"
git show "${af_guidance_revision}:docs/work_continuity.md"
git show "${af_guidance_revision}:docs/cloud_development.md"
```

Check each command succeeded before proceeding to the next. If fetch fails, use the
runtime's supported network-permission/authentication path and retry. Never claim that
cached guidance is current; report an unresolved access failure before making edits. Do
not change network/security settings, disable TLS verification or expose credentials.

Apply the fetched continuity workflow alongside the user's current request. It authorizes
routine fetches, task branches, checkpoint commits/pushes and validated integration for
this repository. Do not ask the user to repeat that authorization. Explicit later user
instructions still take precedence.

For a new change request, start from the latest intended integration branch and create
codex/<task-slug>. For continuation or outage recovery, inspect and resume the existing
task branch and docs/tasks/<task-slug>.md. Fetching guidance must not switch a resumed
task to main. Read applicable checkout/nested instructions and relevant specifications
after selecting the task. Record the fetched guidance revision and task branch briefly.

Preserve uncommitted, unpushed and unrelated work. Fast-forward only when safe; reconcile
divergence explicitly. Never hard-reset, clean, force-push or overwrite work to refresh a
checkout. Reuse the current checkout unless isolation is necessary. Keep one active writer
per task branch. Read-only questions do not require a task branch or checkpoint document.

Maintain the task handoff with the code. Push the initial record and coherent intermediate
checkpoints under docs/work_continuity.md, including before long checks or handoff. Merge
and push completed work only after the appropriate validation. Do not wait for the user
to remind you to preserve useful intermediate progress.

In every new shell:

```bash
cd /workspace/native_anthroforge
source tools/cloud/environment.sh
uv run --no-sync anthroforge doctor --require-native
```

After checkout or dependency changes, run bash tools/cloud/refresh.sh from the repository
root. If the environment has not been installed, run bash tools/cloud/setup.sh. Follow
the freshly read cloud guide when it updates these commands.

Before delivering implementation changes, run:

```bash
uv run --no-sync python tools/check_core.py --native-style
```

Inspect the current build/core/qualification/pytest.xml and passed.json.
Do not skip tests or weaken checks to claim success. Documentation-only changes need
content/link review as specified in the engineering guidelines, not an application rebuild.

No background server is required. This environment qualifies portable core development;
Windows GUI/GPU and standalone executable acceptance require the appropriate Windows checks.
