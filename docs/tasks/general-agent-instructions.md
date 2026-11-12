# General agent instructions

- Task branch: `codex/general-agent-instructions`
- Integration branch: `main`
- Starting revision: `2ec68ce495cecca0e9f635199784b0ea9663b45c`
- Status: in progress
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

Analysis complete; rewrite and content review pending. Existing project documents stay intact.

## Verification

Pending content review, removal checks and `git diff --check`. Documentation-only change;
application tests, GUI checks and packaging are not required.

## Next actions and blockers

1. Rewrite and review the instructions; verify preserved preferences and removed specifics.
2. Commit, push and integrate the reviewed documentation; update the source AGENTS.md.

## Recovery inputs

No external assets or environment setup needed. Preserve all unrelated source-checkout edits.
The containing commit identifies this checkpoint; inspect remote reachability for push status.
