# 0.4.2 status, diagnostics, placement and inspection workflows

- Task branch: `codex/inspection-workflows-042`
- Integration branch: `main`
- Starting revision: `44a80ab` (qualified 0.4.1 plus recommendation audit)
- Status: complete; 0.4.2 qualified
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

All four runtime increments are integrated. The [workflow](../inspection_042.md) documents
shared replacement status, stage-qualified spatial findings, preview/confirmed and bound-point
placement explanations, dimensions/sections, sampled containment and temporary neighborhood
views. Production geometry and attachment behavior remain unchanged. Development, offscreen
and relocated portable qualification pass; delivery details are recorded below.

## Verification

Final qualification passes; intermediate checkpoints below preserve their actual results.
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

## Delivery scope

All selected runtime work is complete. Other audit entries remain unselected. General
whole-surface containment proofs, minimum separating translations and globally guaranteed
escape paths are not claimed by the advisory sampling/local-normal tools.

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

## Runtime completion and qualification checkpoint

- First full gate: 2,618 passed, three failed. One style failure was a newly added test
  exceeding 15 lines. Two stacking-view failures exposed a caller left on the former
  tissue-specific scene helper. Corrected at the shared helper import; all affected tests pass.
- Seventeen spatial tests and the existing stacking/replacement suites pass. Added skin
  witness/measurement coverage and cached idle projection checks. Actual QML rendering exposed
  NumPy scalar presentation; native adapters now return built-in scalar types. JSON exports
  and the displayed normal-distance field are covered.
- Profiler evidence: the 58-SCP/96-tissue project remains the identical document/history after
  all read-only requests. Native metrics/section/placement calls are sub-millisecond; qualified
  sampled volume classification took 6.15 ms in one run. Complete requests took 9–34 ms, with
  unrelated checks active. See `build/inspection-042/production-timings.json` and its profile.
- Dimensions/witnesses wait for their corresponding staged geometry. Neighborhood membership
  refreshes on relationship changes. Frozen export restores clipping, axes and its camera.
- Version is prepared as 0.4.2; final gate and packaging remain. No release/merge claim yet.

## Final qualification and delivery

- `tools/check.ps1` passes: **2,622 Python tests**, **6 native CTests**, native and script
  style, 15-line limits, Ruff/formatting, mypy, numerical imports and runtime doctor.
  The earlier stacking helper regression is corrected and its original tests pass.
- **32 relocated portable checks pass** under minimal PATH with offscreen desktop tests.
  The new packaged check exports and validates dimensions, qualified sample counts,
  confirmed-placement evidence, neighborhood membership and a matching PNG/JSON archive.
- Offscreen 360 px inspection layout and native GPU viewport captures have no QML warnings.
  Actual 96-muscle assembly neighborhood/section views were rendered and reviewed; Restore
  retained the identical document/workspace. Testing used no visible desktop windows.
- Profiler evidence is complete and separates native queries from request wall time.
  There is no claim of a speedup or physical input/display latency. Diagnostic work is
  explicit or enabled by the user; stable measurements re-use their accepted projection.
- Ownership review: eligibility stays with application policies; query strategies use the
  existing coordinator and read-only revision checks. C++ owns repeated geometry queries.
  UI owns temporary presentation. Exports own frozen geometry/evidence. No new numerical
  production algorithm, project schema, scheduler, status manager or automatic repair.
- Current main was fetched and has no intervening changes. Normal merge/push preserves all
  checkpoints; the containing commits identify the delivered code. Root `__init__.py` remains
  unrelated and untracked.
- Canonical executable: `dist/0.4.2/AnthroForge.dist/AnthroForge.exe`.
  Companion source: `dist/AnthroForge-0.4.2-source.zip`.
  Packaged runtime stamp: `ecbac40cf1e699e118ac24bfdcd2d28dd8d1b49c` (later changes are docs).
  Native DLL SHA-256: `4ab1baafa78efa7c3815fea555ce4f40e6bf3943f5a0ac02f8b89054d947781a`.
- Evidence: `build/inspection-042-gate-final.log`, `build/inspection-042/portable/portable-check.json`,
  `build/inspection-042/production.afprofile.zip`, `production-timings.json`, hidden captures
  and archive-verification output in the same build folder.
