# Automatic skin pipeline specification

- Task branch: `codex/skin-pipeline-spec`
- Integration branch: `main`
- Starting revision: `82b46e71404ac11802f84d638c51ce49c079858c`
- Status: specification and documentation validation complete; integration pending
- Last updated: 2026-11-27, Europe/Bucharest
- Active writer: current specification chat

## Outcome and acceptance

Create the confirmed feature specification for exclusive Draft/Final skin update modes,
automatic prerequisite repair and builder-owned settings. Include complementary diagrams,
a behavioral acceptance matrix and explicit implementation limits. No application implementation,
numerical algorithm, release version or schema change is part of this task.

## Decisions and relevant files

The user confirmed the consolidated grilling design through Q30 on 2026-11-27.
The authoritative delivery is [the feature specification](../specification_skin_pipeline.md).
Earlier additive updating and manually required Draft-to-Final recovery were superseded.
The newer AVBD integration was inspected in the separate dirty
`codex/avbd-envelope-cpu` worktree at `b3b92969`; its unrelated changes stay there.

## Current state

A clean existing checkout is reused for this documentation branch. The specification
contains 28 normative requirements, 30 acceptance scenarios and 16 diagrams across eight
families, including builder and stage specialization. README and the consolidated
recommendations index link to it as confirmed future behavior.

Diagram rendering dependencies, standalone HTML, SVGs and review screenshots live outside
the repository in the local `skin-pipeline-spec` visualization artifact directory.
The Markdown contains all diagram sources and remains the durable delivery.

## Verification

- Reviewed the text against all 19 consolidated product decisions and the confirmed
  planner/stage/builder/coordinator responsibilities.
- Verified 28 unique requirement IDs, 30 unique acceptance IDs and acceptance references
  covering all 28 requirements. Acceptance cases describe future implementation checks;
  they have not been executed against application behavior.
- Rendered all 16 Mermaid sources successfully using Mermaid CLI 12.2.0 / Mermaid 12.3.0
  and system Chrome. Compared rendered definitions with the repository source.
- Visually inspected every diagram; corrected context-label overlap and state labels
  that the renderer had interpreted as unintended extra nodes.
- Verified all 13 relative links in the new specification/task record and the new
  README/recommendations links. Reviewed the scoped documentation diff.
- Standalone HTML verification: all 16 images loaded, diagram zoom/open/close worked,
  no JavaScript page errors, no document overflow at 1600px or 390px viewport widths.
- Application automated tests, desktop GUI acceptance and packaging checks were not run:
  application behavior and packaging are unchanged. Preview checks validate documentation.

## Next actions and blockers

1. Commit and push the final documentation, reconcile current `origin/main`, then merge
   and push under the continuity workflow. Verify remote ancestry.
2. Application implementation is a separate future task. Its stage compatibility,
   archive migration and numerical checkpoint equivalence require qualification.

No documentation blockers remain.

## Recovery inputs

The specification contains the agreed rules without requiring chat history.
The separate AVBD worktree includes uncommitted source evidence and is not represented
by its HEAD alone. Generated visual review outputs are local-only and are not application
runtime or packaging qualification.

