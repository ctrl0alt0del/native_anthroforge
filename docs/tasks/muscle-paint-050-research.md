# Muscle Paint 0.5.0 — requirements and method research

- Task branch: `codex/muscle-paint-050-research`
- Integration branch: `main`
- Starting revision: `d03db662df92b4730148c665c013db3a0b48bea1`
- Status: expanded research complete and documentation validated
- Last updated: 2026-10-29, Europe/Bucharest
- Active writer: local documentation/research session

## Outcome and acceptance

Document the confirmed interview through Q45, then investigate reusable addon capabilities
and published methods for Muscle Paint. No production implementation, algorithm change,
version bump, schema change or release qualification belongs to this task. Completion
requires decision/content/link review and method research for every identified unresolved
area, with alternatives, existing-code consequences and discriminating experiments rather
than unsupported success claims.

## Decisions and relevant files

- [Product specification](../specification_050.md) owns confirmed behavior, including
  session-only paint, explicit generation, existing branches and advisory penetration.
- [Method research](../muscle_paint_050_research.md) distinguishes inspected existing code,
  published evidence and untested applicability. Native numerical work remains required.
- Isolated checkout: `E:/development/anthroforge/build/muscle-paint-050-docs`.
  The primary checkout has unrelated unfinished muscle-assembly work; leave it intact.

## Current state

Confirmed requirements consolidated with superseded proposals explicitly replaced.
Research compares the sparse layout planner, native smooth-base fitter, existing standalone
drawing/painting/loft/history boundaries and primary literature. R1–R14 cover each identified
method family, including alternatives, recommended formulations and integration requirements.
E1–E12 discriminate the remaining empirical questions and separate observed capabilities
from untested applicability.
Roadmap, recommendations and research index link the new documents. No final algorithm,
new dependency or implementation plan is selected; no runtime changes are included.

The first delivery's research coverage was incomplete. The expanded review now covers
projection/coverage, merging, charts/flow, gaps/normals, true branch assembly, periodic
loops, adaptive fitting, attachment strips, accuracy and execution/lifetime.

New inspected findings: `surface_correspondence.cpp` and its application adapter reject
closed explicit material maps; closed alignment preserves a phase/direction but defaults
to arc-length stations. `surface_branches.cpp` blends a seam correction into child rows,
so independent patch fitting is not sufficient evidence for the final assembled shape.
These require researched integration approaches, not a claim that fitting alone solves them.
The native fit review also distinguishes Python numerical preparation from the native solve,
and identifies permanent equality activation in `ordered_solve`. A simple analytic example
demonstrates the latter's optimization limitation; it is not an anatomical failure replay.
Paint-only undo requires transient history participation because the current History only
commits changed Documents. All these findings remain documentation, not runtime changes.

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

Expanded-review checks: all 25 local links in the research resolve; R1–R14 each have one
coverage row and a detailed method section; E1–E12 each have an explicit experiment row.
`git diff --check` passes. Re-read native branch assembly, correspondence, curve split/frames,
addon spline/ordering kernels and application history directly. External evidence includes
official API documentation, author project pages, paper sections and indexed abstracts;
large SurfaceBrush/StrokeStrip/Sketch Retopo PDFs were not newly downloaded in full when
the web tool hit size/time limits. No full-paper-review claim is made for those sources.

No numerical, GUI, performance, full development-gate or packaging checks run or claimed.
This is documentation-only acceptance, not qualification of Muscle Paint.

## Next actions and blockers

1. For experimental qualification, begin E1 against the actual standalone loft, then
   grouping/gaps/flow before branch and periodic assembly. E11/E12 cover history and cost.
2. Use the R1–R14 findings in implementation design, including the shared-boundary gaps.
   No new generic literature pass is needed merely to identify methods for the four
   originally highlighted gaps. Numerical defaults, actual anatomy quality and cost
   remain empirical questions; do not silently relax product policies to make a method pass.

No production changes are authorized by this research continuation. Git merge ancestry and remote reachability record
integration status; do not infer runtime completion from this document's task status.

## Recovery inputs

Addon source is local at
`C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
No production project assets are modified. Research links and exact inspected source
paths belong in the research document. The containing commit identifies each checkpoint;
inspect Git remote reachability before describing it as remotely recoverable.
