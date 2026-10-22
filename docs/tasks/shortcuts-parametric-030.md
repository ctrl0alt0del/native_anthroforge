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
Ten foundation contract tests pass. Numerical transforms use canonical metres/radians;
curve point changes use native handle editing and cage resizing reuses native interpolation.
Common authored mutation guards reserve active formula components. A first incremental
shortcut panel exposes properties and edits wrappers with default policies. Nondefault
attachment policies explicitly remain unavailable in this incomplete checkpoint.
This is not a usable 0.3 release: complete catalogue coverage/context exposure, formulas,
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

The restricted native expression service is implemented and has 49 passing contract
cases (59 together with shortcut foundations). Candidate probes and the selection
rationale are in [expression qualification](../research/shortcuts_030/expression_qualification.md).
No parser dependency was pinned: one small typed native compiler/evaluator preserves
integer/real/unit semantics without a second floating interpreter. Program caches use
the existing engine ResourceCache; native binding calls retain profiler coverage.
Latest native dimensional bounds/input validation edits were rebuilt successfully;
the combined 59-case run passed. Full integration is pending.

Initial main and origin/main matched after fetch. `uv run --no-sync pytest
tests/test_shortcut_foundations.py tests/test_construction_objects.py
tests/test_interleaving.py -q`: 38 passed. Mypy and Ruff checks pass for current source.
Offscreen desktop smoke and an actual shortcut-panel capture loaded without QML
warnings. Font-directory configuration was necessary for readable offscreen text;
the inspected capture is local-only `build/shortcuts-panel.png`. Required full tests, profiler,
native/parity, offscreen GUI and portable packaging have not yet been run.
Validation stays background-only; no interactive desktop acceptance is implied.

## Next actions

1. Integrate driving operations, graph
   cycles/dependents, coherent coupled candidates, and scheduling/publication through
   the existing coordinator. There is no public driver lifecycle or scheduled formula
   evaluation yet. Replace the explicit nondefault-policy checkpoint rejection in
   shortcut_operations.editable_wrapper when edit contexts are implemented.
2. Finish catalogue coverage, property context actions, structural copy/reference
   handling, and full shortcut edit policies, then complete each increment in the
   implementation plan. Record checkpoints and actual evidence here.
3. Run full qualification, update versions only after success, build the canonical
   distribution/source archive, and merge the validated branch.

## Recovery inputs

Use repository development setup. Research fixtures and provenance are in
`docs/research/shortcuts_030/`; large original Blender files remain local under
`E:/development/WIP_models`. No source anatomy migration is included in this task.
