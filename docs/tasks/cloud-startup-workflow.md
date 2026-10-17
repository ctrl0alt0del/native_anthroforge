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
  The update is not yet saved/published. Continue through Settings > Codex Cloud > Edit.

## Verification and next actions

1. Open the existing published environment through its normal Edit flow; apply the exact
   text from docs/cloud_startup.md, save and republish, then inspect persistence.
2. Record configuration evidence and merge/push documentation after link/content checks.

No application code changes or application rebuild are needed. No new cloud chat is
requested; validation will distinguish published configuration from fresh-chat execution.

## Recovery inputs

Use the already signed-in ChatGPT browser and the existing **AnthroForge Standalone**
environment for `ctrl0alt0del/native_anthroforge`. Source instructions are in AGENTS.md,
docs/work_continuity.md and docs/cloud_development.md. Never modify the other similarly
named environments. The containing Git commit identifies this task checkpoint.
