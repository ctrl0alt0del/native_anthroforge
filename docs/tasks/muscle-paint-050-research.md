# Muscle Paint 0.5.0 — requirements and initial research

- Task branch: `codex/muscle-paint-050-research`
- Integration branch: `main`
- Starting revision: `d03db662df92b4730148c665c013db3a0b48bea1`
- Status: documentation/research complete; validated, ready to integrate
- Last updated: 2026-10-29, Europe/Bucharest
- Active writer: local documentation/research session

## Outcome and acceptance

Document the confirmed interview through Q45, then investigate reusable addon capabilities
and published methods for Muscle Paint. No production implementation, algorithm change,
version bump, schema change or release qualification belongs to this task. Completion
requires decision/content/link review and a research shortlist with limitations and
discriminating experiments rather than unsupported success claims.

## Decisions and relevant files

- [Product specification](../specification_050.md) owns confirmed behavior, including
  session-only paint, explicit generation, existing branches and advisory penetration.
- [Initial research](../muscle_paint_050_research.md) distinguishes inspected existing code,
  published evidence and untested applicability. Native numerical work remains required.
- Isolated checkout: `E:/development/anthroforge/build/muscle-paint-050-docs`.
  The primary checkout has unrelated unfinished muscle-assembly work; leave it intact.

## Current state

Confirmed requirements consolidated with superseded proposals explicitly replaced.
Initial research compares the sparse layout planner, native smooth-base fitter, existing
standalone drawing/painting/loft boundaries and primary literature. It proposes seven
discriminating experiments and separates observed capabilities from untested applicability.
Roadmap, recommendations and research index link the new documents. No final algorithm,
new dependency or implementation plan is selected; no runtime changes are included.

## Verification

Read standalone guidelines/work continuity and reviewed the consolidated product contract
against the interview corrections: explicit generation, temporary paint/no extra close
warning, independent stroke undo, discard triggers, existing branches, explicit closure,
depth filtering and advisory penetration. Ownership/coupling review keeps paint state,
native reconstruction, shared attachment policies and publication responsibilities separate.

On Windows, using `E:/development/anthroforge/.venv/Scripts/python.exe`:

- Checked every relative Markdown link in the specification, research and task record:
  no missing targets. Checked the three index additions against the same files.
- Checked all 19 full addon source paths cited in code formatting: present.
- Checked the six recorded SHA-256 values have 64 hexadecimal characters and recorded
  them from `Get-FileHash`; local addon document modifications are explicitly disclosed.
- `git diff --check`: passed. Primary-source URLs were opened through web research;
  the working PIQP documentation URL replaces the inaccessible short domain.

No numerical, GUI, performance, full development-gate or packaging checks run or claimed.
This is documentation-only acceptance, not qualification of Muscle Paint.

## Next actions and blockers

1. Merge/push validated documentation into main, preserving unrelated work.
2. For subsequent research, begin E1 against the actual standalone loft, then grouping
   and gaps before branches/closed loops. Experiments are proposed, not executed here.
3. Design an implementation plan only after evidence resolves the algorithmic gaps;
   do not silently relax confirmed product policies to accommodate a candidate method.

## Recovery inputs

Addon source is local at
`C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
No production project assets are modified. Research links and exact inspected source
paths belong in the research document. The containing commit identifies each checkpoint;
inspect Git remote reachability before describing it as remotely recoverable.
