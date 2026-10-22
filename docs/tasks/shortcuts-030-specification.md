# Shortcuts and parametric curves — 0.3 specification consolidation

- Task branch: `codex/shortcuts-030-specification`
- Integration branch: `main`
- Starting revision: `4029809`
- Status: in progress; documentation only, runtime not implemented.
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
- Product authority: `docs/specification_030.md`; delivery: `docs/implementation_030.md`.
  Prior evidence: [research](../shortcuts_030_research.md), not an implementation report.

## Current state

Repository inspected at the research merge. The only pre-existing local change is the
untracked legacy root `__init__.py`, which remains untouched. New documents and reference
updates are not written yet. No feature code, parser benchmark or geometry validation is
part of this task.

## Verification

Pending: content/decision review, Markdown target/anchor checks, whitespace checks and
documentation-only diff review. Application builds/tests are not required for these edits.

## Next actions and blockers

1. Write the authoritative specification and implementation plan.
2. Reconcile active references and clearly mark superseded research proposals.
3. Validate documents, checkpoint/push, integrate the latest main and merge/push normally.

## Recovery inputs

The confirmed decisions are consolidated in this task's specification, not a chat transcript.
Research inventories are already in Git. Original Blender files remain external reference
assets and are not needed to validate documentation links or content.
