# Refresh Cloud workflow at chat startup

- Task branch: `codex/cloud-startup-workflow`
- Integration branch: `main`
- Starting revision: `4fa6f31`
- Status: configuration published and verification complete; integration below
- Last updated: 2026-10-17 (Europe/Bucharest)
- Active writer: desktop chat updating the existing Cloud environment configuration.

## Outcome and acceptance

Update the saved Start skill of **AnthroForge Standalone** so new chats fetch and read
the latest repository workflow without a user reminder. Save and publish the update;
verify the displayed saved instructions. Preserve existing work and environment setup.

## Decisions and current state

- Existing Start skill reads checkout files but does not fetch first; it ends with the
  superseded reminder about per-request Git authorization.
- Fetch and read current origin/main guidance before editing, even when the task branch
  or published filesystem contains older instructions. Preserve task branch identity.
- Do not reset, clean, force-push, or automatically replace a dirty/diverged checkout.
- Keep existing install command, private visibility, network permissions and dependencies.
- Store the exact startup text in repository documentation for reproducible configuration.
- Prepared docs/cloud_startup.md and linked it from the cloud guide; local link checks
  and git diff --check passed. The original published setup chat rejected Save draft
  without identifying a field. Settings > Codex Cloud > Edit accepted and published
  the initial update. Use that normal Edit flow for future configuration changes.
- A local check against the existing single-branch recovery clone showed ordinary
  `git fetch origin` did not create origin/main. The repository startup text now explicitly
  fetches refs/heads/main:refs/remotes/origin/main. Executing that exact fetch/read block
  with Git Bash succeeded, read all three guidance files at `4fa6f31`, and preserved the
  task branch and working tree. The final text with this refinement was then saved and
  published in edit chat 01a14a80-15dc-7005-831b-48252540806a.
- The UI displayed the full final startup text, including the explicit main refspec, then
  All changes saved and Environment published. Reloading retained Environment published.
  Install command, Only me visibility and network/secret settings were preserved.
- The account configuration now contains the text in [cloud_startup.md](../cloud_startup.md).
  Local screenshot evidence: build/cloud-review/startup-workflow-published.jpg (ignored,
  not available in a fresh clone). The published edit chat is accessible in the account at
  https://chatgpt.com/local/01a14a80-15dc-7005-831b-48252540806a.

## Verification and next actions

Documentation links and git diff --check pass. The exact Git Bash bootstrap was tested in
a separate recovery checkout; publication was verified in the account UI. No new development
chat was started to execute the startup skill, and no fresh Cloud runtime test is claimed.

No application code changes or application rebuild are needed. Commit/push this final
record, merge into main and push normally. On recovery, fetch and use
`git merge-base --is-ancestor origin/codex/cloud-startup-workflow origin/main`: exit 0 means
delivery is complete; otherwise finish integration without repeating the environment edits.

## Recovery inputs

Use the already signed-in ChatGPT browser and the existing **AnthroForge Standalone**
environment for `ctrl0alt0del/native_anthroforge`. Source instructions are in AGENTS.md,
docs/work_continuity.md and docs/cloud_development.md. Never modify the other similarly
named environments. The containing Git commit identifies this task checkpoint.
