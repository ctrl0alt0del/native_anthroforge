# Direct UI workflows and report review

- Task branch: `codex/ui-direct-workflows`
- Integration branch: `main`
- Starting revision: `bad422f0193f2f871f05e16a0815da2377f76eb4`
- Status: in progress
- Updated: 2026-10-20, Europe/Bucharest
- Writer: local desktop chat; direct work, background validation only

## Confirmed scope

Implement the reviewed simplifications using shared application policies and coherent
undo: direct stacking settings, direct closed-loft creation with Realign, source editing,
Hook member selection, image tracing, nonmodal workspace presentation and inline naming,
direct report text editing, and discoverable Tissue creation.

User decisions:
- Fiber creation is available without curve edit mode and defaults to nearest SCP
  bindings. Explicit optional target/role/interior-point overrides remain available.
- Delete confirms only when other objects are affected; all entry points share policy.
- Choosing a tissue weight field enters editing; committing a weight applies to selected
  points in one undo action.
- Focus immediately creates a workspace for selected anatomy and descendants with an
  automatic name. Rename and membership options remain available afterward.
- Closed lofts create immediately in one undo action; Realign remains available.

Keep optional inflation previews, coherent region/gesture drafts, explicit anatomical
conversion, save-revision choices and permanent report-file deletion confirmation.
No geometry algorithm substitutions, source mutation on inspection or dummy SCPs.

## Reports

Three inbox reports inspected read-only, all from 0.2.1:
- `16203ca77e2744b9b2dbfc4fa2eae8dd`: excessive ellipsis.
- `22301967f3f5478595777eb751c93263`: Anatomy/Construction should be tabs.
- `2f4815be5165470680437e032b2c0966`: misaligned icons.

Compare annotated captures with current shared controls before changing behavior.
Preserve original report archives. Resolve still-reproducible defects in this task.

## Ownership and acceptance

Shared commands/policies own nearest binding, deletion impacts and validation. Desktop
adapters own navigation and selection; QML dispatches explicit user edits, never writes
on initialization/refresh. Reuse native nearest queries, coordinator and transactions.
Validate API policies, single undo, rejected edits, selection, dense lists and offscreen
QML. Inspect captures at representative DPI/layout sizes, run the development gate,
qualify the single canonical 0.2.2 package and source archive, then merge/push.

## Current state and next steps

Implementation and interaction qualification (not release-ready):
- Native nearest-SCP pin capture inside the existing Fiber creation job, with optional
  explicit overrides and dispatch-time provenance. No Python geometry loop.
- Shared deletion-impact query, direct closed surface creation/Realign, source/member
  navigation, tracing, weight editing, workspace focus/presentation and direct report text.
- Direct stacking controls and toolbar/menu Tissue creation with searchable source chooser.
- Fiber options use a virtualized point list rather than one target control per point.
- Focused core checks, direct stacking, fields, surfaces and report text interactions pass.
- Actual QML verifies automatic and explicit Tissue Final Fiber bindings, source editing,
  direct Tissue creation and searchable chooser, conditional deletion and workspace focus.
  A modeless workspace panel preserves keyboard camera shortcuts; the shared selector
  now restores the active index after model replacement/rename.
- Report labels, real tabs and icon centering pass at 150%/200% scaling, including
  1050-logical-pixel width. Existing shared controls already fix the reported defects.
  Inbox originals remain untouched. Image-plane tracing and its independent one-action
  undo now pass. Field re-entry/mixed selection and root/leaf keyboard/tree deletion pass.
- Shared Hook member navigation passes for curve controls, base vertices and lattice
  points as well as imported vertices. Selection changes neither geometry nor history.
- Updated specifications, API and walkthroughs. Full Windows gate passed: 1,317 tests
  (87.63 seconds, 829 existing Qt deprecation warnings), native CTests, type/style/function
  checks and numerical/native doctor. Portable qualification and final delivery remain.
- The additional packaged command protocol passes in the source launcher: automatic
  endpoints, independent copy, undo/redo, impact inspection and saved ready output.
- An additional search regression exposed misleading defaults after filtering an explicit
  surface choice. The shared selector now retains authored/draft selection across filtering
  and Qt model replacement. Actual Fiber overrides and Anchor creation/rebind checks pass.
  This final runtime change is QML-only; compiled Python/native sources are unchanged.
- First portable run passed through tissue rendering and the new API checks, then failed
  because its compiled report probe still expected the removed Edit text button.
  Updated that opt-in probe to focus/edit directly; source packaged-style capture/edit/
  delete now passes. Rebuilding the executable is required before repeating portable QA.

Prior ignored audit probe reproduced unapplied stacking checkbox changes, hidden Fiber
creation, per-point selector clutter, source navigation without editing and Hook member
selection doing nothing outside edit mode.

1. Finish full Windows gate and portable qualification.
2. Record final evidence, install the single canonical package and source archive.
3. Merge and push validated changes.

## Ownership review

Automatic target choice belongs to shared Fiber creation, using native batched queries
inside the existing cancellable worker and complete captured read set. Explicit target
semantics, independent copy and publication/undo ownership are unchanged. Deletion-impact
inspection reuses shared editability/reference/binding checks; actual deletion revalidates.
Desktop navigation and selection compose existing application operations. QML writes
only on explicit interaction and restores accepted choices after failed edits or undo.
No new scheduler, numerical Python implementation, document preview layer or report
storage format was introduced. Report drafts remain separate from document undo.

## Recovery

Use the normal repository Windows environment (`.venv`, native build). Evidence and
experiments under `build/ui-direct-workflows`; reports under the user's local
`AnthroForge/Reports`. Preserve unrelated untracked root `__init__.py`.
