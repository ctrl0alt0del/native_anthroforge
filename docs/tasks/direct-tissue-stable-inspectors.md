# Direct tissue creation and stable editing layouts

- Task branch: `codex/direct-tissue-stable-inspectors`
- Integration branch: `main`
- Starting revision: `6f72018aae47e85a281fb9a45311c1d8615d41f3`
- Status: in progress
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: local desktop chat, direct work

## Outcome and acceptance

Transient calculation/status messages must not move editing controls horizontally or
vertically. Present short-lived feedback in a bottom-right overlay without stealing a
numeric drag or focus. Keep persistent diagnostics available in Activity/Issues.

Create Tissue acts on selected construction without a modal. Generic Points, Curves
and Surfaces obtain attached construction automatically using shared application
operations. Surface-to-Membrane conversion must also create Fibers from its ordinary
source curves, including when requested independently of Tissue creation. Preserve
original construction, internal sharing, editable parameters and coherent undo.

## Decisions and relevant files

The latest user request supersedes the old specification's prohibition on automatic
attached-source conversion. Existing Point/Curve conversion creates independent copies;
reuse that behavior and nearest-SCP defaults. Do not introduce UI-specific conversion,
blocking waits, numerical Python loops or partial authored graph publication.

Qt 6.12 Overlay/Popup documentation was consulted. Existing transient inspector labels
use conditional visibility inside layouts; Create Tissue still opens a source modal
for generic construction. No standalone Surface-to-Membrane command currently exists.

## Verification

Implemented shared atomic attached-graph jobs, nearest-SCP defaults, direct Tissue and
Membrane actions, multi-output creation selection, and layout-independent notices.
Initial API tests pass for Point/Curve/Surface conversion, independent shape preservation,
single undo, and missing-target rejection. Development gate and GUI not yet qualified.

Pending: mixed fibers/branches/junctions, failures, cancellation,
undo/redo and persistence; background QML numeric-drag/layout and direct-action checks;
development gate, canonical portable package and source archive.

## Next actions and blockers

1. Trace creation/publication contracts and transient inspector feedback.
2. Implement reusable attached-construction conversion and direct desktop actions.
3. Qualify layouts, lifecycle, geometry and package; then merge/push normally.

## Recovery inputs

Preserve unrelated root `__init__.py`. Keep all GUI validation background-only.
Local evidence belongs under `build/direct-tissue-stable-inspectors/`.
