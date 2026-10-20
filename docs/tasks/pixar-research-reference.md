# Pixar research reference and untangling assessment

- Task branch: `codex/pixar-research-reference`
- Integration branch: `main`
- Starting revision: `87c24f2`
- Status: in progress
- Last updated: 2026-10-21, Europe/Bucharest
- Active writer: desktop chat, direct work

## Outcome and acceptance

Save Pixar's research library where future development can find it. Explain whether
Untangling Cloth is worth investigating for tissue self-intersections, including its
actual convergence mechanism, failure cases and costs. This is documentation/research;
no runtime algorithm or acceptance-policy changes are requested.

## Decisions and current state

User wants downstream tolerance and smoothing examined before any removal/remeshing.
Any proposed self-overlap treatment is within one TissueVCP only. The current bounded
biharmonic height QP is convex; its geometry is not a collision-aware optimization.
The legacy graphics.pixar.com library URLs redirect to Pixar's technology page;
that official page links the current library at https://research.pixar.com/.

## Verification and next actions

Read primary paper and follow-up evidence, distinguish observations from hypotheses,
save a concise research reference linked from README, validate links/content, then
commit/push and merge the documentation normally. No builds or GUI checks are needed.
Preserve the unrelated untracked root `__init__.py`.
