# Mirroring 0.3.5 specification consolidation

- Task branch: `codex/mirroring-035-specification`
- Integration branch: `main`
- Starting revision: `1acb8ae`
- Status: in progress; documentation only
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

Read engineering guidelines, continuity rules, current documentation and the
role-aware surface provider boundary. Official Blender 5.0 Mirror documentation is
reference context, not authority for this specialized product contract.
The unfinished `codex/parity-workflows-034` remains preserved at `e37ff02`;
this task starts independently from main, not from its unfinished runtime work.
The unrelated untracked root `__init__.py` is preserved.

## Verification

Pending: content/decision review, local Markdown links, whitespace and staged diff.
Application tests/builds are not required or performed for documentation-only work.

## Next actions and blockers

1. Write specification and implementation plan; update active documentation links.
2. Verify coverage, terminology, references and planned-versus-implemented status.
3. Commit/push checkpoint, validate against main, merge/push completed documentation.

## Recovery inputs

Use normal repository setup; no native SDK or Blender process required for this task.
Original addon source paths in the implementation inventory are local evidence, not
portable build dependencies. No anatomical assets need to be copied or committed.
