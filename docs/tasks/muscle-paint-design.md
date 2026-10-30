# Muscle Paint design and implementation plan

- Task branch: `codex/muscle-paint-design`
- Integration branch: `main`
- Starting revision: `2ec68ce495cecca0e9f635199784b0ea9663b45c`
- Status: complete — documentation only; local integration
- Last updated: 2026-10-30, Europe/Bucharest
- Active writer: current desktop chat; direct work, no delegation

## Outcome and acceptance

Design Muscle Paint on the implemented Painting System, then provide ordered delivery
increments, ownership, concrete numerical methods, qualification decisions and tests.
Preserve the confirmed [product contract](../specification_050.md); distinguish proposed
implementation from implemented/qualified behavior. No runtime changes or rebuild.

## Decisions and relevant files

- Read [engineering guidelines](../engineering_guidelines.md), the product contract,
  [research](../muscle_paint_050_research.md) and [Painting System](../painting_system.md).
- Inspected current painting, history, command/service composition, authored publication,
  surface records and native correspondence. History currently requires a Document change;
  explicit surface material correspondence currently rejects closed paths.
- Proposed design belongs in `docs/design_050.md`; ordered work in
  `docs/implementation_050.md`. Numerical alternatives remain evidence-qualified candidates.
- Current checkout reused: `build/application-boundaries`, clean at task start. Preserve
  unrelated assembly code, AGENTS/guideline edits and root `__init__.py` in primary checkout.
- Latest supplied instruction forbids Git remote contact without explicit request. This
  task uses local branches/checkpoints only; no fetch, push, pull or remote API calls.

## Current state

Design and P0–P7 delivery plan written. Added links from specification/research, Painting
System, roadmap, architecture, authoring API and recommendations. R1–R14 have explicit
delivery and discriminating evidence. No Muscle Paint runtime implementation, numerical
trial, package or project-format change performed.

## Verification

- `git diff --check` / staged diff check: passed.
- UTF-8 Python validation of added Markdown links in the diff from `2ec68ce4`: 42 new
  local file/anchor links across 10 documents, all resolve. External method references
  checked against official StrokeStrip, libigl and CGAL sources during research.
- Content review: every confirmed specification section and all R1–R14 research items
  have owning boundaries and acceptance scenarios. Status/commands/schema are clearly
  proposed; current scalar Painting System behavior remains marked implemented.
- Separate ownership/coupling review: one stroke lifecycle/coordinator, feature adapters,
  one transient/document history chronology, native numerical preparation, shared cyclic
  correspondence, typed panel and existing command/service composition. Corrected an
  overly broad shared-source restriction: compatible generated shape edits still propagate.
- Changed-path review: documentation only. No application/native tests, build, packaging
  or interactive geometry acceptance run or claimed for this documentation delivery.

## Next actions and blockers

1. Runtime implementation remains unstarted; when requested, begin with plan P0's recorded
   fixtures and discriminating numerical experiments, then P1's shared history contracts.
2. Proposed schema 10 is needed only with persisted cyclic material maps; no format has
   changed. Coordinate the schema number if concurrent work uses it first.
3. Commits/integration are local only under the supplied no-remote instruction. No remote
   recovery or pushed checkpoint is claimed.

## Recovery inputs

Existing implementation/research paths are linked from the design. Future anatomy fixtures
are external under `E:/development/WIP_models`; do not modify them during this task.
No secrets, large geometry or generated binaries belong in these documentation commits.
