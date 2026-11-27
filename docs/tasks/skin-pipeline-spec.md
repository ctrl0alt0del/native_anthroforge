# Automatic skin pipeline specification

- Task branch: `codex/skin-pipeline-spec`
- Integration branch: `main`
- Starting revision: `82b46e71404ac11802f84d638c51ce49c079858c`
- Status: documentation in progress
- Last updated: 2026-11-27, Europe/Bucharest
- Active writer: current specification chat

## Outcome and acceptance

Create the confirmed feature specification for exclusive Draft/Final skin update modes,
automatic prerequisite repair and builder-owned settings. Include complementary diagrams,
a behavioral acceptance matrix and explicit implementation limits. No application implementation,
numerical algorithm, release version or schema change is part of this task.

## Decisions and relevant files

The user confirmed the consolidated grilling design through Q30 on 2026-11-27.
The authoritative delivery will be [the feature specification](../specification_skin_pipeline.md).
Earlier additive updating and manually required Draft-to-Final recovery were superseded.
The newer AVBD integration was inspected in the separate dirty
`codex/avbd-envelope-cpu` worktree at `b3b92969`; its unrelated changes stay there.

## Current state

A clean existing checkout is reused for this documentation branch. Diagram rendering
dependencies and generated previews live outside the repository.

## Verification

Pending: decision coverage, source/diagram consistency, Mermaid rendering, visual inspection,
relative links and final scoped diff. Application tests and GUI tests are not applicable to
this documentation-only change and will not establish implementation correctness.

## Next actions and blockers

1. Finish the specification and diagrams.
2. Render and inspect every diagram; validate links and decision/acceptance coverage.
3. Commit, push and integrate only this task's documentation under the continuity workflow.

## Recovery inputs

The specification will contain the agreed rules without requiring chat history.
The separate AVBD worktree includes uncommitted source evidence and is not represented
by its HEAD alone. Generated visual review outputs are local-only and are not application
runtime or packaging qualification.

