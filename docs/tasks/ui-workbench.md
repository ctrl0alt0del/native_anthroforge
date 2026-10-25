# UI workbench implementation

- Status: complete; implemented and qualified for normal merge delivery.
- Branch: `codex/ui-workbench`; integration: `main`; baseline: `9701c8c`.
- Qualified runtime: `37da18e`; subsequent changes are documentation only.
- Scope: implement the approved [workbench design](../ui_overhaul_design.md) in 0.3.7.
- Direct work, no agents. Keep all validation background/offscreen/hidden.
- Preserve unrelated root `__init__.py`; checkpoint/push and validated merge authorized.

## Delivery sequence

1. Shell: menu, viewport-local workspace/tools, stable bottom calculation/status area,
   persistent pane dimensions and Focus editor presentation.
2. Context editor: Shape / Shortcuts / Inspect, remembered per category; move existing
   controls rather than duplicating operations. Tissue shaping and curve engine first.
3. Purpose-first copy and explicit enum labels, retaining stable data/API IDs and all
   restrictions. Optional relationships and diagnostics stay accessible.
4. Qualification: action-retention inventory, real interactions, numerical drag/focus,
   narrow/high-DPI captures, profiler comparison, development gate, portable package.
5. Update walkthrough/design status and one canonical 0.3.7 package/source archive.

## Contracts

No geometry, attachment, engine, shortcut-policy, save/undo or scheduler changes.
Existing Qt controls, command catalogue, capability enforcement, keyboard manager,
Issues, Activity, profiler and staged viewport remain the owners. Hiding a page must
not commit/cancel an unrelated gesture or repeatedly recreate a draft/editor. Active
tools remain reachable and explicit user page changes preserve existing transactions.
Desktop layout is local presentation state, never document data or an undo action.

## Initial evidence

Read Main, Inspector, Construction/Primitive/Tissue inspectors and the approved design.
Source confirms two mixed global toolbars, setup actions before tissue shape controls,
and raw enum labels. Shared UiSection already retains expansion while instantiated;
reuse it with explicit state keys rather than creating a parallel disclosure system.
Qt's existing SplitView supports persistent sizes; native focus scopes and visibility
must be tested with the actual keyboard and editing code.

The retention checklist included all currently reachable actions, including
source replacement/split, optional inflation preview, mirror inspection, reports,
recovery and workspace management; a simpler default must not remove those features.

## Shell/editor checkpoint

Implemented the menu/viewport/status shell, context pages and persisted local layout.
Moved primary tissue shaping ahead of optional settings, grouped Fiber support controls,
and added display-only enum labels without changing command identifiers. Existing
editors stay instantiated across pages; document state and computations are untouched.

Source smoke, project recovery/recent workflows at two sizes, architecture checks,
and initial workbench interactions passed. Added explicit tests for layout persistence,
enum dispatch, preview retention, on-demand geometry inspection and curve editing.
Fixed new icon/encoding issues found during these checks. Full gate, profiling,
portable qualification and final visual/copy review remain pending. No release claim.

## Interaction and profiling evidence

Workbench acceptance passes at 1440×900/1050×680 and 150% scale: page changes and Focus
editor preserve document identity; curve editing and inflation previews survive page
changes; friendly update-mode labels still dispatch raw enums. Numerical acceptance
passes decimal/comma entry, dragging, cancel/deactivation and one-action Undo. Tissue
authoring/preview, Fiber editor, shortcut workflow, section/painting and Preferences
checks pass. Layout scans found no cropped text in the recorded workbench views.

The moved comparison display exposed per-field notification ordering: maximum could
arrive before mean/RMS. Presentation now formats unavailable individual values safely.
Rechecked stage comparison and unchanged anatomy pass. Updated the old relationship
acceptance fixture to use anatomical workspace members (it previously tried to include
a Hook, silently failing workspace creation); focused navigation and export now pass.

Serial ABBA recordings, using the actual assembly and Ribs Top Radius=3 with the same
30 controller ticks, took 15.35/14.59 s before and 14.92/14.49 s after. All captures have
526 active jobs at the bounded endpoint, no calculation errors, zero property queries,
9 model replacements, and 15 row insert/remove events each. Data-change counts ranged
1252–1315. No repeatable regression is demonstrated; these runs do not establish a
speedup, full-update completion or physical frame/input latency. Individual binding
outliers varied (up to 90 ms); inclusive durations were not added together. No profiler
run overlapped the development gate. Reports: `build/ui-workbench/profiles/` (local).

At that checkpoint, the full gate, package, final action inventory and combined-source
qualification were pending. Source/geometry algorithms had not changed.

The full development gate passes 2,248 Python tests, five native CTests, typing/style,
numerical and runtime checks. The first relocated portable build passes the complete
minimal-PATH suite, including hidden GPU geometry, reports, mirroring and authoring.
Final design review then added bounded searchable relationship lists (100-consumer search
and stable-layout acceptance pass). This required refreshed package and desktop checks.
All application/native Python/C++ behavior remains unchanged.

Navigation completion: Construction search uses a Qt proxy over the existing incremental
records (no copied authored data or new selection model). Anatomy hover actions and full
name tooltips restore room for names. Search rename/insert/remove tests pass; real Qt
tests confirm unchanged selection/document identity and buttons remaining visible when
the pointer enters them. Final-source profiling and refreshed qualification follow below.

## Final qualification

- Final Python suite: **2,250 passed**, including search propagation, layout persistence,
  shared edit restrictions, and existing geometry/attachment contracts. Ruff, format and
  mypy pass. The complete development gate previously passed 2,248 tests and five native
  CTests, native style, PowerShell, numerical and runtime checks; only desktop navigation,
  two tests and documentation changed afterward. Native code is unchanged.
- Runtime `37da18e` built successfully into the canonical 0.3.7 folder. A relocated copy
  under `build/ui-workbench/Portable App/` passes the complete minimal-PATH portable suite.
  It exercises packaged authoring, attachments, tissue stages, mirrors, profiles, reports,
  and project recovery. Result: `build/ui-workbench/portable-final/portable-check.json`.
- Final workbench interactions pass at 1440×900, 1050×680 and 150% scale. Text audits
  find no cropped labels in ten recorded views. Numerical entry/drag/cancel/Undo, tissue
  previews, Fiber editing, shortcut workflows and inspection remain functional.
  Action inventory finds **zero removed command IDs, named controls or adapter calls**.
- Final serial ABBA profile: before **15.106 / 15.562 s**, after **15.259 / 15.710 s**.
  All captures retain 526 active jobs at the same 30-tick endpoint, with zero calculation
  errors/property queries, nine model replacements and 15 row insertions/removals.
  Data-change counts are 1297/1315 before and 1321/1280 after. Reports and comparison:
  `build/ui-workbench/profiles-final/`. Runs did not overlap builds or test gates.
  Ranges overlap; two observations per condition and uncontrolled background load do
  not establish a speedup or rule out small regressions. Individual binding outliers
  reach 92.6 ms. This is bounded UI workload evidence, not completed-update or frame
  latency. Inclusive overlapping durations were not summed.
- UI captures and hidden GPU images were inspected. Offscreen window captures alone do
  not validate 3D scene pixels; the portable render check uses hidden QQuickRenderControl.
  Physical desktop interaction, display latency and gaming-load behavior are untested.
  No visible application windows, physical input or OS registration changes were used.

## Ownership and delivery review

WorkbenchState owns local layout only. ConstructionFilter uses the existing incremental
model; RelatedObjects owns bounded presentation. Editors, selection, commands, capability
policies, calculation lifecycle and native geometry retain their original owners. Enum
labels do not alter command values. No application/core/native source changed. Existing
public behavior, schema 6 and version 0.3.7 remain intact; root `__init__.py` is preserved.

Documentation links, current-versus-historical qualification and action retention were
reviewed separately from test results. Delivery uses one canonical
`dist/0.3.7/AnthroForge.dist` and `dist/AnthroForge-0.3.7-source.zip`. Temporary captures,
profiles and qualification copies stay under ignored `build/ui-workbench/`.
