# Initial 0.2.1 curve workflow requirements

- Task branch: `codex/021-curve-workflow-spec`
- Integration branch: `main`
- Starting revision: `1e0dbda`
- Status: requirements investigation and documentation complete; ready to integrate
- Last updated: 2026-10-19, Europe/Bucharest
- Active writer: local desktop chat

## Scope and evidence

Record the user's initial 0.2.1 changes and explain solver controls from implementation.
See [the specification draft](../specification_021.md) for confirmed decisions versus
unconfirmed recommendations. VCP work moves to 0.2.2. User confirmed first click starts
placement; subsequent plain click finishes/exits, Shift-click continues.
The follow-up confirms automatic obstacles, optional exclusions, all authored points by
default with optional subset selection, and comfortable UI at 100+ items.

Inspected drawing tools/QML, conversion validation, typed routing settings, dependency
targets, native sample allocation, collision capture and solve budgets. Current checkbox
conversion drops unselected authored points. Current routing captures every explicit
surface, including a new flattened geometry snapshot; automatic selection requires a
shared input/dependency policy, not just UI changes. No new performance claim was made.

Inspected the addon donor: CollisionOracle automatically enumerates root-associated SCP
mesh geometry, supplements explicit muscle supports and offers bounds-based active sets,
required-collider inclusion and bounded caches. Its runtime consumes oracle.colliders();
this policy was not carried through to standalone ordinary routed curves. Native donor
capabilities must be reused rather than presenting automatic selection as a new invention.

## Validation and continuation

Documentation-only update: reviewed active roadmap references and relative links;
`git diff --check` passes. No runtime changes, package rebuild or new GUI acceptance.
Preserve historical 0.2.0 release records and unrelated untracked root `__init__.py`.
Commit/push and merge normally. Later work should collect the remaining 0.2.1 feedback,
finalize scalable list presentation and prepare implementation. Routing defaults are settled.
