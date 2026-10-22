# 0.3 shortcuts and parametric curves

- Task branch: `codex/shortcuts-parametric-030`
- Integration branch: `main`
- Starting revision: `c74b28085c31f894f6ce343265d999da526a6feb`
- Status: in progress; runtime implementation not yet complete
- Last updated: 2026-10-22, Europe/Bucharest
- Active writer: local Codex implementation chat (direct work)

## Outcome and acceptance

Implement the confirmed [0.3 specification](../specification_030.md) through the
[ordered implementation plan](../implementation_030.md): property wrappers,
driving formulas and attachment policies, native parametric curves, desktop and
headless operations, schema-4 reading/schema-5 writing, and qualified 0.3.0 release.
Preserve existing geometry, attachments, scheduling, undo and resource ownership.

## Current state

Runtime remains 0.2.4; this branch is incomplete and must not be merged yet.
Initial property/wrapper records, stable numerical references, inferred ownership,
discovery/exposure/configuration API, and coherent nested candidate writes exist.
Schema 5 writes these records; schema 4 remains readable with empty shortcut state.
Six foundation contract tests pass. This is scaffolding, not a usable 0.3 release:
desktop exposure, complete semantic property adapters, write guards, expressions,
driver scheduling/policies and parametric evaluation still need integration.
The unrelated untracked root `__init__.py` remains untouched.

## Decisions and relevant files

The specification is authoritative. Property edits and wrapper edits are distinct;
ownership is inferred; only the initiating wrapper applies attachment policies.
Formula evaluation and numerical sampling belong in C++; parser candidates need
qualification against typed/unit-aware semantics before selection. Any junction
locks parametric resolution. Parametric-to-Fiber conversion preserves the exact
accepted finite path as an independent Bezier curve. Older 0.2.4 projects must load.

## Verification

Initial main and origin/main matched after fetch. `uv run --no-sync pytest
tests/test_shortcut_foundations.py -q`: 6 passed. `uv run --no-sync mypy` and
Ruff checks pass for current source. Required full runtime tests, profiler,
native/parity, offscreen GUI and portable packaging have not yet been run.
Validation stays background-only; no interactive desktop acceptance is implied.

## Next actions

1. Complete semantic property adapters (including transforms, cage resizing and
   current-shape curve point edits), common driven write restrictions and desktop
   exposure. Avoid treating generic dataclass replacement as a numerical editor.
2. Qualify expression candidates, then complete each integrated increment in the
   implementation plan. Record checkpoints and actual evidence here.
3. Run full qualification, update versions only after success, build the canonical
   distribution/source archive, and merge the validated branch.

## Recovery inputs

Use repository development setup. Research fixtures and provenance are in
`docs/research/shortcuts_030/`; large original Blender files remain local under
`E:/development/WIP_models`. No source anatomy migration is included in this task.
