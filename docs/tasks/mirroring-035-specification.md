# Mirroring 0.3.5 specification consolidation

- Task branch: `codex/mirroring-035-specification`
- Integration branch: `main`
- Starting revision: `1acb8ae`
- Status: complete (documentation); reviewed and ready for integration
- Last updated: 2026-10-24, Europe/Bucharest
- Active writer: local Codex session

## Outcome and acceptance

Consolidate the confirmed mirroring interview into specification_035.md and
implementation_035.md, both **Confirmed — not implemented**. Link recommendations,
roadmap, architecture, authoring API and addon audit. Verify decision coverage and
local links. No runtime, version, format, migration, build or qualification changes.

## Decisions and relevant files

Strict source reflection supersedes the addon's independently evaluated mirrors.
Mirrored instances are read-only and absent from trees. Hierarchy rules create
instances; symmetric complete constructions suppress redundant mirrors. Required
construction is shared per source/rule. Attachment conflicts report without changing
reflected geometry. Existing independent counterparts are not automatically paired.

## Current state

Created [specification](../specification_035.md) and [implementation plan](../implementation_035.md),
both Confirmed — not implemented. Updated recommendations (including superseded A07
and asymmetric stacking acceptance), roadmap, architecture, authoring API and addon audit.
Read engineering guidelines, continuity rules and the role-aware provider boundary.
Official Blender 5.0 Mirror documentation is reference context, not product authority.
The unfinished `codex/parity-workflows-034` remains preserved at `e37ff02`;
this task starts independently from main, not from its unfinished runtime work.
The unrelated untracked root `__init__.py` is preserved.

## Verification

Reviewed confirmed interview choices and corrections against specification sections:
rules/coverage/identity (2), strict stages/attachments/stacking (3), mirrored rows and
half-path loops (4), read-only UI/no tree nodes/workspaces/removal (5), revision agreement,
failure retention and persistence (6). Superseded decisions are explicit in section 1.
Implementation ownership, source inventory, delivery increments, headless/desktop
integration, performance and future acceptance are recorded separately from evidence.

Final new/changed local Markdown link check: 23 links, zero missing files/anchors.
Both documents' explicit status labels and Markdown fence balance checked successfully.
`git diff --check` and `git diff --cached --check` passed. Only Markdown is changed;
no runtime, dependency, project or
package versions changed. Application tests/builds are not required or performed.

## Next actions and blockers

No documentation work remains. Integrate this reviewed checkpoint into current main
under the continuity workflow; actual commit/push results establish remote reachability.
Runtime implementation and qualification remain future work under the linked plan.

## Recovery inputs

Use normal repository setup; no native SDK or Blender process required for this task.
Original addon source paths in the implementation inventory are local evidence, not
portable build dependencies. No anatomical assets need to be copied or committed.
