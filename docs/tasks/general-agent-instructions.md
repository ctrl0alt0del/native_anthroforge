# General agent instructions

- Task branch: `codex/general-agent-instructions`
- Integration branch: `main`
- Starting revision: `2ec68ce495cecca0e9f635199784b0ea9663b45c`
- Status: complete
- Last updated: 2026-11-12, Europe/Bucharest
- Active writer: desktop chat editing general agent instructions

## Outcome and acceptance

Rewrite [AGENTS.md](../../AGENTS.md) as concise, reusable instructions. Remove product
names, technology mandates, repository paths, release procedures and repository-specific
authorization. Preserve research-first behavior, the 15-line function limit, direct work,
sound design, meaningful validation and careful handling of existing work.

## Decisions and relevant files

- Reviewed the current instructions, README, confirmed specification, engineering
  guidelines and continuity workflow. This request changes agent guidance only.
- [Official instruction-file guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
  distinguishes reusable preferences from repository-specific guidance.
- Preserve the local, uncommitted structural-warning rule by generalizing its intent.
- Use an isolated checkout because the source checkout contains unrelated assembly work.
  Update its requested AGENTS.md after review without switching its branch or staging its files.

## Current state

Replaced the project-specific instructions with four general sections covering research,
implementation, continuity and validation. Reduced the source checkout's 1,054 words to
575 (about 45%). Preserved the local structural-warning edit as a general ownership rule.
Existing project documents stay intact; no runtime or computational behavior changed.
The source checkout's AGENTS.md now matches the reviewed version. Its active branch,
staging and unrelated tracked edits were preserved; this copy remains an uncommitted
change on the separate assembly branch until that branch incorporates the cleanup.
The cleanup is integrated. An integration mistake also published the pre-existing local
documentation commits `ffe39e58` and `d3e1b948`; their content changes were reverted without
rewriting history. The final change from the starting remote main contains only AGENTS.md
and this task record. The original commits and files remain on the source assembly branch.

## Verification

- Passed manual content review against the requested scope and preserved preferences.
- Passed `git diff --check` on Windows for the rewritten instructions and this record.
- A search of AGENTS.md found no product names, technology mandates, repository paths,
  build commands or repository-specific authorization from the previous version.
- Reviewed the local AGENTS.md link and opened the official documentation link.
- Application tests, GUI checks and packaging were not run: documentation-only change.
- Verified the final diff against starting revision `2ec68ce4` contains only the two
  intended documentation files; the unrelated documentation content matches that revision.

## Next actions and blockers

No implementation or validation work remains. Verify the correction push and archive
the temporary worktree; Git ancestry establishes integration.

## Recovery inputs

No external assets or environment setup needed. Preserve all unrelated source-checkout edits.
To publish the separate design work later, account for its integration revert: merging
the original commits again will not reapply their content automatically.
The containing commit identifies this checkpoint; inspect remote reachability for push status.
