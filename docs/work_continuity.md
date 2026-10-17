# Development continuity through power outages

Use a task branch and keep its recovery context in Git alongside the code. This workflow
applies to the standalone repository `ctrl0alt0del/native_anthroforge` on desktop and cloud.
It does not change the application's document-save or calculation-checkpoint behavior.

## Authorization and ownership

The user's October 17, 2026 instruction provides standing authorization for routine fetches,
creating task branches, committing/pushing intermediate work, reconciling desktop/cloud
changes, and merging/pushing completed work into the intended integration branch. Do not
ask again for these ordinary steps. This replaces this repository's previous per-request
remote-authorization rule. It does not authorize unrelated repositories, PR creation,
deleting remote branches, force-pushes, protection bypasses, or discarding someone else's work.

Use one active writer per task branch. A handoff records the writer for orientation; it is
not a distributed lock. Stop work in the old chat before continuing in another environment.
A push rejected because another writer advanced the branch is a reconciliation signal.

## Start a task

1. Inspect status, the current branch, worktrees and relevant instructions. Preserve existing
   unrelated changes, especially the legacy untracked root `__init__.py`.
2. Fetch origin and identify the integration branch (`main` unless explicitly specified).
   Synchronize it without discarding local work. Do not start from an unrelated unfinished
   task branch. Reuse a suitable checkout; use an isolated checkout if existing work prevents
   a safe switch. Never forcibly switch an occupied worktree's branch.
3. For new work, create `codex/<task-slug>`; add a suffix if that name already belongs to
   another task. For a follow-up or interrupted task, use its existing branch instead.
4. Copy [the handoff template](tasks/TEMPLATE.md) to `docs/tasks/<task-slug>.md`, filling in
   scope, acceptance, integration branch, starting revision and next action. Push this initial
   record promptly with `git push -u origin codex/<task-slug>`.

Read-only questions do not require a branch or a handoff document. A small change needs only
a small task record; do not create a new planning bureaucracy or a complete chat transcript.

## Checkpoint while working

Push each coherent increment, even when the overall request is unfinished. Aim for a useful
checkpoint about every 10 minutes of active changes, and before a long build, experiment,
planned handoff or stopping. Split work into smaller increments when this repeatedly slips.
This is an agent working rule, not an unattended autosave service or a hard time guarantee.
If only research progressed, checkpoint the material findings and next step.

Before each checkpoint:

- Review the diff and stage explicit task-owned paths. Never use an indiscriminate `git add .`
  in a dirty shared checkout. Keep secrets, generated environments and large local assets out.
- Update the task record to match the staged implementation: completed work, remaining gaps,
  relevant files, decisions, observed failures, tests run/not run and the immediate next step.
- Run quick checks appropriate to the increment. Full-suite success is not a prerequisite
  for preserving intermediate work. Record untested/known-broken behavior plainly, including
  how to reproduce it; never describe such a checkpoint as merge-ready.
- Commit with a meaningful message (use `checkpoint:` when incomplete), then push the named
  task branch normally. Preserve published commits; use follow-up commits instead of amending
  and force-pushing them.
- Check the push result. Confirm remote reachability before saying the work is backed up.
  If the push fails, keep the local commit, report the last known remote checkpoint and retry
  when access returns. Local commits alone cannot help while that PC is unavailable.

Tests may run after a checkpoint push; the next checkpoint records their actual results.
CI can be red on an explicitly incomplete branch. Resolve required failures before integration;
do not skip required checks merely to make a checkpoint appear complete.

## Resume from desktop or cloud

Use the [cloud guide](cloud_development.md) for environment activation and dependency refresh.
For a known task, this is a sufficient user prompt:

> Continue `codex/<task-slug>` from its latest pushed checkpoint. Fetch the branch, read
> AGENTS.md and `docs/tasks/<task-slug>.md`, then resume the first unfinished step. Keep
> pushing intermediate checkpoints under the repository continuity workflow.

The agent then:

1. Checks for existing local changes and fetches origin. Inspects the remote branch and its
   task record, rather than assuming the environment snapshot is current. Branch history
   and file content are authoritative; an old chat's recollection is supplementary.
2. In a clean fresh checkout, switches to a local tracking branch for the named remote branch.
   If already on that branch without local divergence, fast-forwards to its remote tip.
3. Reads the handoff and only the linked specifications/files relevant to the next step.
   Checks which prerequisites, assets or test evidence are local-only; rebuilds ignored outputs
   instead of expecting them in Git. Refreshes dependencies/native outputs after checkout.
4. Updates the writer/context when work resumes, then continues. Pushes the updated context
   with the next increment. Does not start the task over or create another branch just because
   the machine changed.

If the task branch is unknown, inspect remote `codex/*` branches and their task records.
Match the user's request and check merge ancestry/status; do not choose an unrelated task
simply because its branch has the latest timestamp. Clarify if multiple active tasks match.

When the PC returns, stop the cloud writer first. Inspect local uncommitted and unpushed
work before switching. Preserve task-owned local-only work on a separate recovery branch
(and push it when possible), then reconcile it with the latest task branch using normal
merges or selected commits. Leave unrelated edits untouched. Resolve ordinary conflicts
from the implementation intent, and ask only when that intent is ambiguous. Never hard-reset
or force-push to make the two machines agree. If the task was already merged, synchronize
the integration branch and check whether any local-only changes remain relevant.

## Complete and integrate

1. Fetch the current integration branch. Combine relevant upstream changes into the task
   branch and resolve conflicts before qualification. Preserve any unrelated local work.
2. Run the appropriate development checks and acceptance for the combined result. Follow
   [engineering guidelines](engineering_guidelines.md): documentation-only work needs
   content/link review; implementation work needs the applicable local/cloud gate, plus GUI
   or packaging evidence when those behaviors change. A cloud core pass does not establish
   Windows GUI acceptance. Required unavailable validation leaves the task pending on its
   pushed branch; finish that validation on the appropriate machine before merging.
3. Mark implementation/validation complete in the handoff, with any remaining integration
   step explicit. Move durable product/design decisions into their existing authoritative
   documents rather than leaving them only in a task note. Commit and push the final changes.
4. Update the integration checkout safely and merge the task branch normally, preferably
   with a merge commit to retain its checkpoint history. Push the integration branch. If
   upstream advanced in the meantime, preserve it, reconcile and revalidate affected behavior;
   do not force the push. Respect repository branch protections if present.
5. Verify the remote integration tip contains the task result. Report the branch/commit and
   whether any local-only work remains. Keep the task note and branch history available;
   cleanup is not part of routine recovery. Git ancestry establishes integration even if
   an old branch's note still describes its final pre-merge state.

## Context storage choice

| Option | Role in this workflow |
| --- | --- |
| Git-tracked Markdown | Authoritative task handoff, committed and pushed with the code it describes; readable on GitHub, desktop and cloud without another service. |
| Existing specifications and guidelines | Authoritative durable requirements/design rules; link to them instead of copying their contents into every handoff. |
| Chat history | Useful supplementary discussion; recovery must not require access to the original chat. |
| Hosted database | Possible future need for structured concurrent coordination; adds authentication, synchronization and code-revision association that this workflow does not currently need. |
| RAG/search index | Possible future aid for finding old decisions; rebuild from authoritative records, retain branch/commit provenance and open the source before relying on a result. |

Markdown here is not local-only: the remote Git commit carries both source and context.
Keep each task record concise and current. Capture externally useful decisions, evidence,
failed attempts and next actions, not private reasoning, chat transcripts or a command diary.
Use repo-relative links inside records; name missing assets and their access requirements.
Ignored build logs/screenshots are not cloud-accessible evidence unless explicitly uploaded
to an approved location. Do not claim a result can be reproduced from unavailable files.

No method here recovers edits made after the last successful push during a sudden outage.
More frequent checkpoints reduce that exposure. A separate synchronized working-copy backup
would be a different capability, not something Markdown or an online RAG service provides.

References: [official OpenAI guidance on AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[OpenAI task-context workflow examples](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex),
[Git push](https://git-scm.com/docs/git-push), [Git merge](https://git-scm.com/docs/git-merge).
