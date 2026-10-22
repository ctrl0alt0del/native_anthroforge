# Shortcuts and parametric curves — 0.3 specification consolidation

- Task branch: `codex/shortcuts-030-specification`
- Integration branch: `main`
- Starting revision: `4029809`
- Status: documentation complete and validated; ready for integration, runtime not implemented.
- Last updated: 2026-10-22, Europe/Bucharest.
- Active writer: local Codex chat, direct work; no delegated writers.

## Outcome and acceptance

Create the confirmed 0.3 specification and implementation plan; reconcile active
recommendations, architecture, API, roadmap and research references. Preserve historical
release records, source inventories, runtime code, package versions and unrelated files.
Acceptance is complete decision coverage, consistent planned-status labels and valid links.

## Decisions and relevant files

- Property operations remain below shortcut wrappers; only the initiating wrapper's
  attachment policies apply. Ordinary property edits do not acquire these policies.
- Infer a driving shortcut's owning SCP from its controlled properties, including chains
  and shared construction. No manual owner/backsolve-target selector; addon descendant
  overrides and backsolve require an owning SCP.
- Cycles and dependent formulas retain accepted values; independent valid outputs continue.
  Jointly conflicting properties fail together without order-dependent winners.
- Parametric XYZ uses generated points, stored definitions and direct engine switching.
  Junctions lock resolution. Fiber creation uses an independent exact-path Bézier copy;
  Fibers cannot directly use Parametric in 0.3.
- Schema 5 must read existing 0.2.4/schema-4 projects without changing geometry, attachments,
  accepted results or startup behavior. This replaces the proposed rejection-only policy.
- Product authority: [specification](../specification_030.md);
  delivery: [implementation plan](../implementation_030.md).
  Prior evidence: [research](../shortcuts_030_research.md), not an implementation report.

## Current state

Both confirmed documents are written, with final behavior, superseded decisions,
architectural responsibilities, integrated increments and acceptance evidence. README,
recommendations, architecture, API, roadmap and research references identify 0.3 as
planned while retaining the released 0.2.4 behavior and source evidence.

The legacy untracked root `__init__.py` remains untouched. Runtime/native code, tests,
package/lock versions and both source inventories have no diff from `4029809`.
No feature code, parser benchmark or geometry qualification is part of this task.

## Verification

- Reviewed the specification against the confirmed plan and final interview corrections:
  wrapper boundary, inferred ownership, addon override scope, partial/group failure,
  numerical types, generated-point locks, engine restoration, independent Fiber copying
  and schema-4 compatibility. Reviewed responsibility/coupling separately from link checks.
- Inline Python Markdown validation through `.venv/Scripts/python.exe`: changed/new
  documents, new local targets/anchors, fences, whitespace and new-document status/headings.
  Passed: 11 documents, 30 new local links/anchors, zero errors.
- `git diff --check`: passed. Scope review against `4029809`: documentation only;
  runtime, versions and source inventories unchanged.
- Confirmed no internal Markdown references use the renamed research-heading anchors.
- Application builds/tests, parser benchmarks, native/GUI/portable qualification: not run,
  correctly deferred to runtime implementation. No such acceptance is claimed.

## Next actions and blockers

1. Commit and push the validated documentation result.
2. Fetch/reconcile the latest main, merge normally and push; verify remote ancestry.
3. Future runtime implementation starts from the ordered plan and qualification matrix;
   this documentation task does not start it automatically.

## Recovery inputs

The confirmed decisions are consolidated in this task's specification, not a chat transcript.
Research inventories are already in Git. Original Blender files remain external reference
assets and are not needed to validate documentation links or content.
