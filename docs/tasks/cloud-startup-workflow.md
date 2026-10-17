# Refresh Cloud workflow at chat startup

- Task branch: `codex/cloud-startup-workflow`
- Integration branch: `main`
- Starting revision: `4fa6f31`
- Status: in progress
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
  and git diff --check passed. The original published setup chat allowed editing the
  Start skill, but Save draft was rejected by the service without identifying a field.
  Reopening through Settings > Codex Cloud > Edit accepted the draft; initial publication
  is running in chat 01a14a7c-4326-7624-b719-0559b07cd05f.
- A local check against the existing single-branch recovery clone showed ordinary
  `git fetch origin` did not create origin/main. The repository startup text now explicitly
  fetches refs/heads/main:refs/remotes/origin/main. Executing that exact fetch/read block
  with Git Bash succeeded, read all three guidance files at `4fa6f31`, and preserved the
  task branch and working tree. This refinement still needs application to the Cloud field.

## Verification and next actions

1. Inspect publication status in the current Edit chat. Apply the exact latest text from
   docs/cloud_startup.md, including the explicit main refspec, save/publish and inspect
   persistence. Use the normal Edit flow if the current published draft is no longer editable.
2. Record configuration evidence and merge/push documentation after link/content checks.

No application code changes or application rebuild are needed. No new cloud chat is
requested; validation will distinguish published configuration from fresh-chat execution.

## Recovery inputs

Use the already signed-in ChatGPT browser and the existing **AnthroForge Standalone**
environment for `ctrl0alt0del/native_anthroforge`. Source instructions are in AGENTS.md,
docs/work_continuity.md and docs/cloud_development.md. Never modify the other similarly
named environments. The containing Git commit identifies this task checkpoint.
