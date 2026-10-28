# 0.4.2 status, diagnostics, placement and inspection workflows

- Task branch: `codex/inspection-workflows-042`
- Integration branch: `main`
- Starting revision: `44a80ab` (qualified 0.4.1 plus recommendation audit)
- Status: in progress
- Updated: 2026-10-28, Europe/Bucharest
- Active writer: local desktop chat, direct work; no delegation

## Outcome and acceptance

The user selected audit items R01, R02, R03 and R06 for implementation. Deliver shared
operation status assessments, spatial findings beyond tissues, placement explanation
and recovery, and more useful anatomical inspection views/measurements. Preserve all
existing geometry, attachment, skin and solver algorithms. Numerical diagnostics run
in C++ on owned inputs. New diagnostics are advisory, bounded and revision-aware;
expensive checks remain on demand. Do not repair self-intersections or change placement.

Use existing Issues, task coordination, native query/inspection services, presentation
and API contracts. Extend owning boundaries rather than adding parallel systems.
Keep testing background/offscreen; no desktop control. Preserve root `__init__.py`.

## Decisions and investigation

- Follow [audit scope](../recommendations_042_audit.md),
  [engineering guidelines](../engineering_guidelines.md), and
  [status-provider inventory](release-041.md).
- R01 begins with Change tissue source and Replace imported mesh: both API guards and
  UI consume the same read-only application eligibility. Reuse lifecycle/events.
- R02 preserves existing skin reports and tissue witnesses; introduce a shared
  spatial-evidence contract and route current consumers through it. Any additional
  containment/clearance measurement must declare method and invalid-input limits.
- R03 explains the existing qualified placement; do not select a new nearest surface
  or change stored bindings to improve a diagnostic result.
- R06 measurement scope and temporary neighborhood view behavior were asked through
  asynchronous questions; independent R01 work proceeds meanwhile.
- Official Qt model notification and CGAL predicate documentation consulted first.
  These guide integration; existing qualified native kernels remain authoritative.

## Current state

R01 first increment implemented: immutable shared Eligibility records, replacement
start/apply assessment shared by API and Qt, and revision/context-keyed desktop
projection using existing refresh events. No additional polling, queue or policy manager.
Replacement approvals, candidate ownership and commits retain their existing semantics.
The UI presents reasons in existing button hints. R02/R03/R06 remain pending.

## Verification

Pending targeted shared API/desktop tests, native diagnostic tests, geometry/attachment
invariance, development gate, offscreen visual evidence and canonical packaging.
Do not claim interactive desktop acceptance from hidden/offscreen checks.

- R01: 30 tests pass across replacement status/view, mesh replacement, tissue retarget
  and skin status using the qualified native DLL. Includes one-undo preservation,
  stale rejection, binding/geometry invariants and no repeated idle status assessment.
- Initial test invocation selected stale `build/dev/bin/af_native.dll` and failed at
  the missing skin ABI symbol, before geometry execution. Use
  `ANTHROFORGE_NATIVE_LIBRARY=C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native/bin/af_native.dll`
  until building this task's native changes. Never report that initial run as a code regression.
- Ruff passed; mypy found dictionary-union inference in command registration, corrected
  before the next check. Full development gate and GUI/package checks still pending.

## Next actions

1. Trace replacement assessment/guard/desktop refresh events and implement R01.
2. Establish shared spatial witness ownership and implement R02/R03/R06 integration.
3. Qualify complete desktop/headless workflows; document evidence and remaining limits.
4. Release one canonical 0.4.2 package only after acceptance, then validated merge/push.

The containing commit identifies the checkpoint; inspect Git history for push state.

## 2026-10-28 inspection checkpoint

- Confirmed: overall extents and section spans, with visible axes; temporary related-object
  inspection and Restore, without workspace membership or priority changes.
- Shared stage-qualified witnesses now cover SCP/construction/skin plus existing tissue
  findings. Generic staged viewport highlighting and frozen report capture are integrated.
- 23 focused geometry/view/export checks passed. New native scale/extent/section-span
  diagnostics compile; six existing native contract suites pass. Native diagnostic tests,
  UI integration, placement explanation, neighborhood views and full qualification remain.
- This checkpoint is incomplete and must not merge into main or be released yet.

## Measurement and placement integration checkpoint

- Added native world extents, section spans and scale/topology measurements, with
  explicitly unavailable volume-containment/penetration classifications.
- Section inspection now accepts SCP, construction and skin surfaces as well as tissues.
- Temporary neighborhood isolation uses the existing dependency graph and a presentation
  filter. A private inspection camera preserves workspace and scheduling state.
- Placement diagnostics reuse production preview/confirmed query meshes and material
  correspondence. Ray and current-binding explanations do not recapture or modify bindings.
- Eleven new API/native/desktop-model tests pass, including a sealed inner cavity,
  unchanged bound fibers, transformed section spans and Restore semantics.
- Native build and six contract suites pass. Full style/gate, frozen export completion,
  offscreen UI inspection, profiling and packaging remain pending; do not release yet.

## Qualified-volume and evidence checkpoint

- Added explicit, bounded vertex sampling against CGAL-qualified closed exterior volumes.
  Reports distinguish inside/boundary/outside and deepest sampled distance. This is not a
  whole-surface containment proof or a minimum separating translation. Invalid, open,
  nested and intersecting volumes return an unavailable reason; no production repair changes.
- Size/section/volume axes, placement witnesses and neighborhood views are integrated in
  frozen inspection exports. Currentness is validated before freezing. Restore retains
  section clipping and a private neighborhood camera.
- New volume and frozen-view tests pass, including mirror orientation, cancellation,
  stale inputs and 100 idle refreshes without native projection work or new jobs.
- `tools/check_inspection_042.py` rendered the new viewport and 360 px inspector offscreen
  without QML warnings or a visible window. Images live in `build/inspection-042/`.
- Full development gate is running; profiling, final ownership review and canonical
  packaging remain. This is an incomplete recovery checkpoint, not release acceptance.
