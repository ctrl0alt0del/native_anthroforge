# Power-outage development continuity

- Task branch: `codex/power-outage-continuity`
- Integration branch: `main`
- Starting revision: `4301134`
- Status: implementation and verification complete; see integration recovery below
- Last updated: 2026-10-17 (Europe/Bucharest)
- Active writer: this desktop chat; no cloud writer for this task.

## Outcome and acceptance

Make interrupted standalone development recoverable from GitHub on another machine.
Record the user's standing authorization to create a branch per task, commit and push
useful intermediate results, and merge completed, validated work into the integration
branch. Code and enough context to continue must travel in the same checkpoint.

Acceptance: consistent repository instructions; a compact reusable handoff template;
desktop/cloud recovery instructions; a pushed intermediate checkpoint; successful
recovery in a separate checkout; and completed documentation merged and pushed to main.

## Decisions and constraints

- Scope is `ctrl0alt0del/native_anthroforge`, not the separate Blender addon.
- Use Git-tracked Markdown for authoritative task context. An online database or RAG
  service is not needed for this first workflow; any future index should be rebuildable.
- Preserve unrelated root `__init__.py`; do not add it to any commit.
- Keep shared main qualified; checkpoint branches may be incomplete with limitations
  stated explicitly. A checkpoint is not a claim of release acceptance.
- Resume an existing task branch after an outage; create a new branch for new work.
- One active writer per task branch. Never force-push away another machine's work.

## Current state and evidence

- Local main and fetched origin/main both pointed to `4301134` at task start.
- At task start, AGENTS.md required per-request remote authorization; cloud_development.md
  repeated that rule. Neither defined a branch-specific recovery record.
- Official OpenAI guidance supports durable AGENTS.md rules and separate task context;
  Git's branch/commit/push model provides versioned remote checkpoints.
- No application behavior changes are needed. Documentation/link review is the relevant
  gate, not another C++/GUI build.
- Initial scope/next-step checkpoint `057d976` was pushed successfully to the task branch.
- AGENTS.md now records standing authorization and checkpoint/resume/integration rules.
  README.md and the cloud guide link to [work continuity](../work_continuity.md).
- [The reusable handoff template](TEMPLATE.md) covers decisions, acceptance, relevant files,
  actual verification, immediate next actions, blockers and unavailable inputs.
- `git diff --check` passed; a Python pathlib/Markdown-link check resolved local links
  in all six affected documents on Windows. Content review checked authority scope,
  checkpoint-versus-acceptance semantics and preservation of divergent/unrelated work.
- No application tests were rerun for these documentation-only changes.
- Workflow checkpoint `e4a9af91e04935f5fc6d117a76ec68b073a1df0a` was pushed and recovered with
  `git clone --single-branch --branch codex/power-outage-continuity --depth 5
  https://github.com/ctrl0alt0del/native_anthroforge.git build/continuity-recovery-e4a9af9`.
  The fresh checkout was clean, HEAD matched the source and remote tip, and SHA-256
  comparisons matched all six instruction/context documents. Its diff from `4301134`
  contained only those six documents. The actual recovered task record was inspected.
- The recovery checkout is ignored and remains available locally for inspection. This
  demonstrates retrieval from GitHub without the original chat or uncommitted files;
  it is not a simulated power failure or another cloud-runtime qualification.

## Integration recovery

No implementation work remains. Commit/push this verification record, then merge into
main and push normally. A final record cannot assert that its own future push succeeded.
After fetching, use `git merge-base --is-ancestor origin/codex/power-outage-continuity
origin/main` to determine delivery: exit 0 means the task is integrated remotely; otherwise
finish the documented integration steps. Do not repeat completed setup or recovery checks.

## Recovery inputs and limitations

Read AGENTS.md, docs/cloud_development.md and this file on the task branch. The
checkpoint is the Git commit containing this file; use Git metadata for its hash and
remote reachability instead of a self-referential hash inside the document.
No secrets, external assets or machine-local setup are required for this docs-only task.
Work after the latest successful push is not recoverable while the PC is unavailable.
