# Pixar research reference and untangling assessment

- Task branch: `codex/pixar-research-reference`
- Integration branch: `main`
- Starting revision: `87c24f2`
- Status: complete; documentation qualified for normal integration
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

## Findings and delivery

Added [research sources](../research_sources.md) and a README link. Inspected the
official 2003 and 2018 Pixar PDFs and the 2006 boundary follow-up. The 2022 explicit
convergence reference is abstract-only and marked accordingly. GIA is not a guarantee
against local traps: some folded regions receive no separating response, boundary
intersections need extensions, and repair has no fixed step bound. Its value for
static constrained tissue remains untested. No application algorithm changed.

## Verification and integration

Primary PDFs downloaded successfully to ignored `build/pixar-research/` for reading;
the web reader could not fetch them, so local PDF text extraction was used. Reviewed
claims against paper sections and the current QP assembly/reconstruction. Reviewed
README/document links and `git diff --check`. No builds, performance experiments or
GUI checks apply to this documentation-only change. Preserve unrelated `__init__.py`.
Commit/push this complete documentation and merge normally after checking latest main.
