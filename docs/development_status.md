# AnthroForge development validation

Current source qualification is in [tabs and icon alignment](#tabs-and-icon-alignment-021-follow-up).
The earlier sections retain the evidence and limitations of their respective revisions.

## Tabs and icon alignment (0.2.1 follow-up)

Anatomy/Construction use themed Qt tabs with native keyboard navigation. The shared
button layout centers compact icons/help text and icon-label groups; long labels
retain padding and elide. Custom left-aligned section headers remain supported.

The Windows development gate passes **941 tests**, three native CTests and the
existing static/native checks. Actual offscreen editor checks at 100%, 150% and 200%
cover normal/narrow layouts, hover/focus/disabled states, help contrast, retained
pane state and automatic selection-driven tab switching. Inspected captures and
measured content bounds verify the reported delete/help controls. Existing image,
Ctrl-placement, UI-polish and report-browser checks pass. User reports remain intact.
Portable qualification is pending; see the [task record](tasks/tab-and-icon-alignment.md).

## Three feedback reports (0.2.1 follow-up)

The redundant top Import Mesh button is removed. Anatomy and Construction now use
separate full-height tabs. World image import sits beside the viewport projection
control; Properties imports an image parented to the selected object. Orthographic
axis views set initial world-axis alignment, including beneath rotated parents.
Place Points uses the shared snapping modifier (Ctrl by default), independently of
Shift continuation. Releasing Ctrl restores the configured depth policy.

Code at `9850849` passes the Windows development gate: **941 tests**, three native
CTests, native analysis, Ruff, mypy on 195 modules, function limits and numerical/native
doctor. The 307 QQmlPropertyMap deprecation warnings include the 35 new image-controller
test warnings from the existing deprecated constructor.

Actual offscreen QML checks pass stationary modifier transitions, remapped snapping,
Ctrl+Shift continuation, finish/cancel/one-step undo, the Qt file picker, captured
parent intent, image axis alignment and automatic tab selection. Captures at 1440x900
and 1050x680 were inspected. Existing 120-item curve workflows and Construction editor
checks pass. Hidden QQuickRenderControl/D3D11 image rendering passes orientation,
picking and staged replacement; an additional X/Y/Z fixture verifies actual image
pixels beneath a rotated, nonuniformly scaled parent. No visible windows or desktop
input were used. Native Windows file-dialog interaction and hands-on acceptance are
not claimed; file-picker interaction used Qt's offscreen dialog.

Ownership review: temporary snapping belongs to the native stroke projection and
uses captured displayed geometry, without changing authored points or the configured
depth policy. QML resolves semantic modifiers through KeyboardManager. Shared image
creation/alignment owns ordinary-parent and world-transform semantics; the desktop
captures dialog intent and adopts the accepted object through CreationSelection.
ObjectBrowser owns navigation, keeping both pane models alive. Existing document,
scheduler and persistence contracts remain in use.

The clean `37111d6` build passes the full portable suite from a fresh temporary
relocation with minimal PATH, including hidden rendering and packaged feedback capture,
preview, text editing and deletion of QA reports. An additional packaged headless case
passes X/Y/Z parented-image creation and persistence. The release is the single canonical
`dist/0.2.1/AnthroForge.dist`, with `dist/AnthroForge-0.2.1-source.zip`.
No additional version-suffixed distribution was created. User report archives were not changed.
See [task evidence and commands](tasks/three-feedback-reports.md).

## Surfaces and report management (0.2.1 follow-up)

The Patch / Surface toolbar action now creates a patch from one closed curve or a
standalone loft from two or more selected curves/fibers. It reuses source validation,
closed-loop preview/acceptance and the existing accepted-creation selection lifecycle.
Help → View reports browses the persistent feedback inbox with screenshot/description
previews, atomic text editing and confirmed deletion. Failed saves retain the draft;
malformed reports remain visible for deletion. Report actions never enter document history.

The Windows development gate passes for code at `31f9015`: **930 tests**, three native
CTests, native analysis, Ruff, mypy on 194 modules, function limits and numerical/native
doctor. There are 272 QQmlPropertyMap deprecation warnings, including 72 from the new
surface controller tests; these are the same existing deprecated constructor.

Actual offscreen QML checks cover two/three-curve toolbar clicks, closed preview,
accepted selection, source editing and undo. Report checks use 120 isolated archives,
virtualized rows, screenshot preview, Unicode/plain-text descriptions, edit/cancel/
failure/retry, delete/cancel/failure, corrupt input, refresh and empty state. Normal,
1050×680 and 200% scale layouts pass; captures were inspected. Existing feedback
capture/annotation/shortcut checks also pass. Hidden QQuickRenderControl/D3D11 surface
rendering, displayed-revision picking and retained mesh replacement pass. No visible
windows or desktop input were used; this does not claim hands-on interactive acceptance.

Ownership review: surface routing stays in the desktop creation adapter and uses shared
validation/commands. The separate Qt-free inbox capability leaves submit-only consumers
unchanged. The local inbox owns scoped archive operations; the desktop owns one worker
request, a keyed list and one decoded preview, with no idle polling. Text edits preserve
all image members and report identity, atomically replace the archive and retain the
original on failure. No geometry, scheduler or document model changes were necessary.

The clean `31f9015` build in `dist/0.2.1-surfaces-reports/AnthroForge.dist` passes the full
portable suite from a fresh relocated directory with minimal PATH. This includes actual
packaged report preview, saved text changes and confirmed deletion of a QA copy; the
original report and user inbox remain untouched. Packaged UI assets match source.
The corresponding archive is `dist/AnthroForge-0.2.1-surfaces-reports-source.zip`.
Source/offscreen evidence and exact commands are recorded in
[the task record](tasks/surface-report-browser.md). Previous distributions remain intact.

## Fiber interaction (0.2.1 follow-up)

Whole-fiber translation, rotation and scale are rejected by shared application policy.
Desktop selection projects this capability separately from read-only state; keyboard,
toolbar, numeric transform fields and gizmos use it. Fiber point/handle editing remains
available. Accepted fiber creation exits editing and selects the new object. Its pending
selection intent survives input-driven job replacement but is discarded on changed
context, failure, cancellation or history navigation.

The full Windows development gate passes for the implementation at `1d6af1d`: **916
tests**, 3 native CTests, native static analysis, Ruff, mypy on 191 modules, function
limits and dependency/native doctor. The existing QQmlPropertyMap deprecation produces
200 warnings, including 176 from the new controller interaction tests.

Actual offscreen fiber UI tests verify accepted creation selection, disabled numeric/
toolbar controls, suppressed G/R/S/W/E dispatch, unchanged selection on disabled clicks,
and component G/R/S with cancellation. Existing component movement/rebinding, conversion,
ordinary curve/image transforms, primitive editing and view-gesture scripts pass. The
fiber capture under `build/fiber-transform-policy/` was inspected. Offscreen evidence
does not claim hands-on Windows input or new geometry-rendering acceptance.

Ownership review: object eligibility belongs to the application policy, component
eligibility belongs to the existing authoring adapter, and the keyboard manager owns
generic capability gating. Selection intent is desktop-only and observes existing job
outputs; it does not create another job lifecycle, document edit or undo step. The
viewport toolbar owns pointer interception for disabled controls. No fiber-kind checks
were scattered across QML widgets.

The clean `1d6af1d` executable in `dist/0.2.1-fiber-edits/AnthroForge.dist` passes the
complete portable suite from a fresh relocated directory with minimal PATH. An additional
packaged headless check rejects all six local/world translation, rotation and scale
requests on a fiber and verifies unchanged authored objects. All 94 packaged QML/JS/SVG
assets match source. The corresponding source archive is
`dist/AnthroForge-0.2.1-fiber-edits-source.zip`; prior distributions remain intact.

Supplementary reporting and large curve-workflow tests initially passed their assertions
but exited with Windows `0xC0000409` during teardown. Both harnesses omitted explicit
destruction of the C++-owned Qt application. Adding the same `finally: delete(app)` used
by the desktop entry point and profiler harness produces clean exits: reporting at normal
and 200% scaling, plus 120-point/120-obstacle editors and placement/undo. Production
shutdown code is unchanged. These harness-only corrections pass Ruff and architecture
checks; no application rebuild is needed. Logs are under `build/fiber-policy-*`.
Validation remains background-only.

## Feedback reporting (0.2.1 follow-up)

Help/F12 captures the application window before a modal editor. Red rectangles, arrows
and text share one source-pixel painter for preview/export; Fit and 100% scrolling keep
annotation placement stable. A Qt-independent report/consumer contract and background
delivery service use an atomic local inbox outside installation/version directories.
User feedback is separate from anatomical Issues, inspection exports and profiler files.
Performance recording now uses Shift+F12; earlier sections retain their historical keys.

The full Windows development gate passes at `5768250`: **901 tests**, 3 native CTests,
native static analysis, Ruff, mypy on 190 modules, function limits and dependency/native
doctor. The 24 existing QQmlPropertyMap deprecation warnings remain. Offscreen interaction
passes normal/200% display scaling and 1050×680 layout: F12 while typing or in another
modal, Help action, original capture fidelity, three annotation tools, undo, zoom/scroll
coordinates, failed submission/retry, cancellation and unchanged document history.
Five updated profiler trials pass normal/snapped dragging with Activity closed/open,
cancellation, focus/privacy and New/Open. Source capture/submission probe passes.

Ownership review: the delivery consumer receives immutable PNG bytes, annotation records
and frozen context; no Qt/document dependency enters the feedback package. Its receipt
supports file or service links. Only explicit submission runs a worker, and only pending
delivery polls completion. UI callbacks publish delivery state; document jobs, history and
save checkpoints remain owned by existing subsystems. Modal focus retains ordinary editor
behavior after capture, including cancellation of a pointer drag. No network adapter runs.

The final capture-failure notification correction at `bcd72f7` passes all **901 tests**
again, Ruff, architecture checks and the full feedback interaction script. The clean
`bcd72f7` executable in `dist/0.2.1-reports/AnthroForge.dist` passes the complete portable
suite after relocation under a minimal PATH, including its new feedback capture/editor/
submission probe. All 94 QML/JS/SVG assets match source. Original and annotated PNGs,
annotation records and packaged build identity were verified in the emitted ZIP.

Local captures/logs are under `build/feedback-*`; validation used no visible windows or
desktop input. Offscreen checks validate the feedback workflow; the separate existing
QQuickRenderControl check validates GPU geometry rendering. A never-shown Windows window
returned UI pixels but omitted its Quick3D mesh even with staged geometry, so that
experiment does not establish ordinary Windows window capture of 3D geometry. Hands-on
desktop capture remains unverified. The prior 0.2.1 distribution and source are preserved;
the new corresponding source is `dist/AnthroForge-0.2.1-reports-source.zip`.

## Curve workflows 0.2.1

Released behavior: curve toolbar, click/Shift-click placement, automatic obstacle inputs,
optional searchable exclusions and authored-point subsets, Advanced solver budgets.
VCP/muscles/soft tissues remain 0.2.2. Schema 3 and the native solver are retained.
Older explicit obstacle lists retain Manual mode; switch to Automatic to adopt new inputs.

Full Windows development gate passes: **896 tests** (24 warnings from the existing QQmlPropertyMap API,
including 15 in the new gesture tests). Native builds/three CTests and clang-tidy pass.
New tests cover automatic scene membership, cyclic consumers, new/moved/deleted geometry,
preview staleness, Manual pending provenance, missing accepted geometry, running-job
supersession, visibility/workspace independence, capture reuse/eviction/concurrency and
point-placement history. Ruff, mypy, function limits, dependency/native doctor and script
checks pass. The final QA-only changes also pass function-limit/architecture checks.

Actual QML offscreen tests pass with 120 obstacles/120 authored points: bounded delegates
(including Qt reuse pool), search, stable numbering, duplicate-name context, required-row
protection, scoped bulk edits, retained search/scroll, focused-point highlighting, preview,
accept and undo. Mouse/modifier events verify placement, axis views during placement,
completion and cancellation. Captures inspected with fonts are under `build/021-curve-workflows`.
Software offscreen validates controls/layout; it does not establish Quick3D geometry quality.
Construction/surface editors, existing curve interaction, view gestures and camera restoration
also pass their offscreen acceptance scripts.

Recorded 100-cube routing: one 0.60 ms native capture reused across eight solves; mean solve
72.34 ms versus prior combined capture/solve 72.64 ms. This is capture reuse evidence, not a
meaningful whole-solve speedup. Full-scene native spatial queries remain authoritative.
The large-editor report exposed repeated candidate-graph preparation; descriptions now reuse
structural graph identity. The complete final report has no collector loss or ChoiceModel
resets. Across 72 obstacle-description binding evaluations, inclusive mean is 1.60 ms and
maximum 13.79 ms. Earlier serial comparisons had an incomplete Qt shutdown and are not used
as speedup evidence. Inclusive nested timings overlap; no general frame-rate claim is made.

Ownership review: eligibility/cycle policy and required-point rules are shared core contracts;
fan-out uses the existing coordinator and marks geometry pending before consumers capture
Manual provenance. The engine owns immutable native collision leases and bounded caches.
One Qt choice model/view serves both optional lists. Provisional placement and keyboard
bindings stay in their existing desktop owners; Python gains no numerical solver loop.

The clean `57e1c53` executable in `dist/0.2.1/AnthroForge.dist` was copied to a fresh
temporary folder and passed the complete portable checks with minimal PATH: shared API,
persistence, attachments, primitives, fibers/surfaces/images, Issues, inspection, profiling,
offscreen GUI and invisible QQuickRenderControl rendering. Packaged QML/JS/icons match
the qualified source. The included `examples/automatic_routing.json` also passes there.

That executable opened a copy of the user's `solver_test.anthroforge`, switched to Automatic,
detected both cubes, saved revision 1855 and produced a complete profile. All three authored
points remain unchanged; independent native queries found no centerline intersections with
either cube. Two hidden rendered angles were inspected. The single recorded native capture
took 0.051 ms and solve 28.98 ms; the retained native collision capture was 9,848 bytes,
excluding cache-key and allocator overhead. These are observations, not a universal clearance
or latency guarantee. The original SHA-256 remains unchanged. Local evidence is under
`build/021-*` and `%TEMP%/anthroforge-021-57e1c53`; these ignored artifacts are not in Git.
No visible windows, desktop input or hands-on interactive acceptance were used.

## Routing correction 0.2.0

The user's `solver_test.anthroforge` contained an ordinary routed curve with no obstacle
surfaces. Conversion now exposes obstacle selection before preview and both routing
inspectors identify an empty effective obstacle set. Fiber attachment surfaces remain
automatic. The native adapter resolves numerical contact at unbound surface knots,
validates warm seeds against solid interiors, and retries an infeasible warm solve once
with cold planning. Authored points and anatomical bindings retain their meaning.
See the [task evidence](tasks/solver-routing.md) and [walkthrough](construction_020.md).

Runtime revision `7e146a1` passes the full Windows development gate: **877 pytest cases**,
3 native CTests, clang-tidy, Ruff/formatting, mypy on 181 modules, function limits,
PowerShell checks, dependencies and native doctor. The 9 existing Qt deprecation warnings
remain. Original routing/anatomy parity cases pass unchanged. Six regression cases cover
the actual scene's surface contacts, saved straight warm path, pin preservation, independent
centerline intersection queries, rejected inside/near pins, explicit owners and undo/save.
Source routing-editor and conversion acceptance pass; automatic Fiber obstacle rows are
checked and disabled. All GUI checks used Qt offscreen or invisible QQuickRenderControl.

The clean `7e146a1` portable executable was relocated to a fresh temporary directory and
passed `tools/check_portable.py --offscreen` with a minimal PATH. That same executable
opened a disposable copy of the user's project, enabled its two cubes, evaluated, saved,
recorded a headless profile and rendered revision 1854. The saved path preserves all three
authored points and has no centerline intersections with either cube in the independent
native query. Rendered output was inspected; this is not hands-on desktop acceptance or a
claim of universal curve-clearance correctness. The original project's SHA-256 is unchanged.

Deliverables are `dist/0.2.0-solver-fix/AnthroForge.dist/AnthroForge.exe`, the corresponding
`dist/AnthroForge-0.2.0-solver-fix-source.zip`, and the separate local project
`E:/development/WIP_models/solver_test_routed.anthroforge`. Logs, captures and the profile
are local-only in `build/solver-routing`; the compact reproducer is committed under
`tests/fixtures/routing/surface_pins.json`. The original 0.2.0 distribution is preserved.

Ownership review: numerical contact and continuation checks remain in the shared C++
routing adapter, using existing spatial queries and solver contracts. The two editors
reuse one obstacle-selection component. Python gains no numerical loop, scheduler or
fallback. Numerical contact is transient and cannot mutate an authored binding. Existing
cancellation, accepted-output retention, dependency capture and transaction rules remain.

## Construction objects 0.2.0

First-class curves, reference images, Fiber as an actual Curve subclass, and shared
curve/fiber surfaces are integrated in desktop and headless workflows. The anatomical
hierarchy and Construction view have distinct ownership. Primitive and surface consumers
retain curve references; engine conversion, attachment rebinding and junction edits use
shared operations and transactions. Images are embedded and independent of tracing output.
Schema 3 rejects older projects clearly; legacy conversion is outside this release.
See the [specification](specification_020.md), [walkthrough](construction_020.md),
[API](authoring_api.md), and [implementation record](tasks/020-construction.md).

At `b8e57fc`, the complete Windows gate passes **871 tests**, 3 native CTests, native
clang-tidy, Ruff/formatting, mypy on 181 modules, function limits, PowerShell checks,
locked dependencies, numerical-import checks and native doctor. The 9 existing
QQmlPropertyMap deprecation warnings remain. Log: `build/check-020-release.log`.
The complete construction example also runs without PySide6, Shiboken or Blender imports.

### Geometry, lifecycle and editing evidence

Compact fixtures pin source hashes and actual Blender/addon outputs. Eleven attachment
owner-weight cases cover hard pins, cyclic spans and quintic transitions. Six warm-route
cases cover changed anchors and sample counts. Four cold/warm routes use 9,158 vertices
from the original skull file; outputs agree with fresh addon solves to absolute 1e-10.
Six base-surface and eight branch fixtures match vertex positions to 1e-10 and exact face
indices. Closed correspondence persists; only explicit Realign selects it again. Original
source `.blend` files were read without modification. The compact inputs and regeneration
tools are committed; the large original files and generated captures remain local.

Blender drawing projection/fallback/depth/offset policies and native curve_fit_nd fitting
have direct fixture coverage. Exact triangle picking intentionally replaces raster-depth
sampling; image-plane drawing is an application extension. Fitting cancellation brackets
the upstream atomic fit call. Uniform branch sampling is an explicit extension retaining
junction stations. Lofts do not collision-conform their surfaces or create muscle volumes.
Authored-fiber Issues check accepted sampled centerlines, not continuous curve/radius
clearance. Provenance and intentional differences are in `native/migration` and
`native/vendor/PROVENANCE.md`.

Contract tests exercise independent Fiber copying and substitution, shared consumer frames,
both consumption modes, topology locks, deletion protection, workspace membership, Manual
provenance, missing inputs/cycles, queued/running cancellation, restart after input edits,
undo/redo and historical saves. Historical creation validates the complete captured read
set before publishing accepted output. Resources remain owned through document/history,
checkpoints, jobs, staging and displayed revisions; no native handles enter project files.

Thirteen integrated source editor/renderer scripts pass across Construction, paths, images,
Fibers, routing, junctions, surface previews/branches, consumer sampling and collision Issues.
Existing primitive/lattice/hook editing, insertion/snapping, G/R/S and axis/restore gestures,
snap offsets, reopen and 512-SCP/128-point projection checks also pass. Image visibility
covers aligned/oblique views in both projection types and all three depth layers, including
reflected/scaled/sheared frames and matching picking. Actual inspector buttons are exercised.
The final title label uses the package version through Qt application metadata.

These checks use synthetic events on Qt's offscreen platform and explicitly invisible
QQuickRenderControl/D3D11 captures. Actual rendered paths, lofts, branches, images and skull
context were inspected. Full-QML offscreen captures do not provide the 3D framebuffer;
separate invisible-renderer captures establish that evidence. No visible windows or desktop
input were used, and no hands-on desktop or physical display-latency acceptance is claimed.

### Profiling and ownership review

Serial off/on/on/off profiler trials use 32 controller drag updates over the skull fixture
with four shared loft consumers. Mean work intervals were 15.01/20.20/22.75/19.17 ms and
p95 18.29/29.06/30.99/21.26 ms. They include synchronous GPU readback, not physical frame
or input latency. System busy was about 14–17%; thermal/background load was uncontrolled.
These trials do not establish exact profiler perturbation or a universal speed guarantee.
Both captured reports are complete, with no model resets. Preparation peaked at 0.035 ms,
publication at 1.032/0.484 ms, and viewport activation at 1.545/1.698 ms. Settled jobs and
staging retained zero geometry; New Document plus renderer draining released all observed
native geometry. Document/history ownership overlaps and must not be summed. Reproduce
with `tools/construction_profile_qualification.py`; local evidence is in
`build/020-construction-profile`.

Separate direct ownership/coupling review traced typed registry access, source references,
Fiber substitution, attachment fields, junction dependency aliases, async creation restart,
read-set validation and resource reachability. The implementation extends the existing
coordinator, Issues, command catalogue and staged renderer. Python packs, validates,
serializes and publishes; native work owns numerical preparation, solving, deformation,
surface assembly and repeated queries. No competing queue, Blender runtime dependency or
Python numerical fallback was added. This was coordinator-authored review, not an
independent agent review.

### Portable distribution

The c999896 build passed the complete relocated checker with minimal PATH and developer
Python/Qt settings removed. Tests cover existing primitives/deformers, editing, deletion,
save/reopen, Issues, workspaces, measurements, images, independent fibers, shared lofts,
complete QML loading and headless/desktop profiler reports. A 64-tile embedded PNG remains
renderable after deleting its external source; JPEG EXIF orientation preserves physical
width and adjusts height correctly. The first run rejected an obsolete QA fixture that
put a control into anatomical workspace membership; correcting that fixture retained the
production policy. Final visual inspection found and fixed a hardcoded old header version.
The corrected **b8e57fc** executable then passed the entire checker again in a fresh
relocated folder. Its complete QML capture shows 0.2.0, and the corresponding invisible
loft/image capture was inspected. Final evidence is `build/portable-020-release.log` and
`%TEMP%/anthroforge-020-b8e57fc/work/portable-check.json`. The packaged native DLL is
resolved inside that relocated application; no developer native library is used.

The packaged solver also recalculated all four skull fibers at 80 samples, updated their
loft, saved and reopened it. Its complete Qt-free report records four fresh native route
calls, with 185.64 ms total inclusive duration; this exploratory result under uncontrolled
load is not a latency guarantee. Evidence: `build/020-packaged-skull.json` and
`build/portable-020-final.log`; temporary portable inputs/captures are under
`%TEMP%/anthroforge-020-c999896`. The later header correction does not change those kernels.

Qualified distribution: `dist/0.2.0/AnthroForge.dist/AnthroForge.exe`, SHA-256
`48b6aec55ebdbb8351d3179e4d0ca6a17d6caa326d5722487d2dead8c8261c2f`.
Keep the whole folder together. Corresponding source is
`dist/AnthroForge-0.2.0-source.zip`. The wheel/sdist and archive resource checks pass.
Prior release folders are preserved. Final documentation is newer than the compiled
source revision; runtime source has not changed since b8e57fc.

## UI polish 0.1.9

Shared dark menu, menu-item, dialog, help and scrolling components own presentation
states and spacing. Qt Basic's unassigned light/mid palette roles caused light hover
backgrounds against light text. Popup delegates also used the outer control width
inside a padded popup. The fixes cover the menu bar, creation menu and dropdowns.
Feature panels use concise summaries and explicit disclosures for ruler coordinates,
attachment data and issue evidence. Workspace visibility columns are aligned; keyboard
help is grouped. Measurement expansion survives presentation-model replacement.

The development gate passed 541 tests, native CTest, lock/Ruff/mypy, native/script
style, numerical checks and native doctor. Seven existing QQmlPropertyMap warnings
remain. Follow-up architecture/style checks cover the packaging and acceptance changes.
No application, geometry, scheduling or document semantics changed.

Source editor/ruler acceptance initially ran with native Windows rendering. After the
user requested uninterrupted desktop use, all further GUI checks used Qt's offscreen
platform with Windows fonts explicitly available. UI-polish, ruler/camera, workflow,
Issues, Activity and view/gesture acceptance passed without QML warnings. Captures of
menus, compact panels, coordinates, workspace columns and shortcut help were inspected.
Tests check hover contrast at least 4.5:1, popup containment, actual Close/Cancel/OK
buttons, deletion/undo and preserved coordinate disclosure. Window sizes were 1440×900
and 1050×680. Offscreen Qt does not establish native-window or desktop surface rendering.

Ownership review: shared controls own presentation mechanics; feature panels own
grouping and transient disclosures. Existing commands, lazy relationship inspection,
incremental Activity updates and authoritative data remain their owners' responsibility.
The background portable-test option explicitly records its platform and still checks
surface pixels through the hidden QQuickRenderControl renderer. It does not silently
claim native-window acceptance.

Packaging exposed Qt's long-command wrapper changing the compiled entry-point name.
Explicit Nuitka executable/distribution names now preserve the packaging contract.
The final executable was built from clean source `ddee3cb`, version 0.1.9.0. The
complete relocated portable check passed with minimal PATH and `--offscreen`, including
editing, persistence, primitives/deformers, issues, workspace tools, rulers/bookmarks,
and complete desktop and Qt-free numerical headless profile reports. Packaged UI
captures and the hidden QQuickRenderControl GPU capture were inspected. The latter
renders the expected cube surfaces; no native-window retest was performed while the
user was gaming. Local evidence is under `build/ui-polish-019`, with portable results
in `portable/portable-check.json` and final build output in `package-final.log`.

The qualified executable is `dist/0.1.9/AnthroForge.dist/AnthroForge.exe`, SHA-256
`941618976e03d437b08a2dfdd9f180aaef1f6c9bef4b116badbd298142526ae8`.
Keep the whole portable folder together. Corresponding source is
`dist/AnthroForge-0.1.9-source.zip`; prior release folders are preserved. Final task
documentation is newer than the compiled source revision and does not change code.

## Measurements and profiling 0.1.8

The final two recommendations add frozen two-surface-point rulers (XYZ, delta and
straight-line distance), persistent named workspace cameras, and profiler explanations
for invalidation, Body base-cache activity and native geometry ownership. Shared API
operations serve UI/headless clients; native queries resolve measurement geometry.
Rulers explicitly become stale after a source/frame change. Their values and bookmarks
round-trip with workspace presentation and appear in frozen inspection archives.

`tools/check.ps1` passed: lock, Ruff, strict mypy, C++ build/CTest, native/script style,
540 tests, numerical checks and native doctor. Existing QQmlPropertyMap deprecation
warnings remain. Actual GUI acceptance exercised surface picks, hidden/unpickable
categories, exact camera restoration during a curve move, one undo action, and export
while geometry changes. Existing axis/restore/gizmo/snap gestures and 0.1.7 workflow
acceptance also passed without QML warnings. The ruler viewport and exported PNG were
visually inspected. Evidence is under `build/inspection-018`.

Five desktop profiler reports passed: normal/Ctrl drag with Activity closed/open and
cancelled drag, plus repeated recordings and document replacement. A snapped report
contains 159 input-output invalidations, 73 newer-request cancellations and 73 base-cache
hits. Its peak unique native geometry was 1,091,624 bytes; owners overlap. History,
jobs and displayed viewport are separately attributed. Perfetto imported 31,822 slices
and ten memory counter tracks with zero importer errors. Weak ownership, aliased handles,
recording-off behavior, bounded inventory failures and late worker observations are tested.

Six serial counterbalanced none/dormant/record trials, 100 events per normal and snapped
drag, measured mean frame intervals of 16.48–16.95 ms idle and 18.36–19.10 ms recording.
Input means were 4.25–4.50 ms idle and 6.50–6.97 ms recording; system busy fraction was
9.4–12.1%. These two repetitions per mode do not establish full-body performance or
zero dormant overhead. Recorded inventory spans were about 0.3 ms or less on this
fixture. A QTest waiting loop initially starved Python export; replacing only the
benchmark wait with a real Qt event loop fixed the test. Production export was unchanged.

Ownership/coupling review: annotations are workspace evidence, not anatomy constraints;
the desktop owns transient pointer state and camera rebasing. The recorder observes shared
mutation/scheduling/cache boundaries and weak resource references; it does not own scheduling
or extend mesh lifetimes. Native registry totals include live handles beyond the current
session. AABB bytes are estimated; Python/Qt copies, GPU allocations and between-snapshot
peaks are outside coverage. No new resource queries run while recording is off.

Visual inspection of the first portable ruler caught inverted mm display conversion;
API coordinates were already correct. The new GUI regression verifies XYZ/distance
in m/cm/mm and clicks the actual bookmark Go button during an active edit. Two repeated
passes and the corrected exported PNG establish the fix. A final full suite passed
541 tests after adding explicit native coordinate and 3-4-5 distance checks.

The final executable was built from clean source `d005bda`, version 0.1.8.0. Relocated
portable checks passed with minimal PATH: primitives/deformers/attachments, editing,
save/reopen, rendering, GUI, issues, workflows, rulers/bookmarks and complete desktop
and Qt-free numerical headless profile reports. The packaged ruler PNG was inspected:
its 1.41421356 m diagonal displays 1414.214 mm. Final evidence is under
`build/inspection-018/portable-final`; later source changes affect tests/docs only.
The qualified executable is `dist/0.1.8/AnthroForge.dist/AnthroForge.exe`, SHA-256
`abe23810632bbe72b3381b46f992489bfc5f638d59756d24533a0d1cdad5ad28`.
Keep the whole portable folder together. Corresponding source is
`dist/AnthroForge-0.1.8-source.zip`; prior release folders are preserved.

## Workflow improvements 0.1.7

The five postponed recommendations are integrated: attachment/dependency inspection,
precise cycle-member versus downstream issues, mixed workspace management/category
filters/presets, mm/cm/m display and entry, and frozen image/JSON inspection reports.
The shared API and [walkthrough](workflow_inspection.md) describe the contracts.

The Windows development gate passed **523 tests**, Ruff/formatting, strict typing,
native CTest, native/PowerShell function checks, numerical imports and native loading.
The final source suite passed **525 tests** after adding packaged-launcher and queued
writer reprioritization regressions; typing/style checks also passed after those changes.
Seven existing Qt deprecation warnings remain. Additional coverage exercises frozen
geometry ownership, read-only export, atomic failure/retry/cancellation, deleted
workspace membership through undo, native attachment anchors, full persistence and
cycle causes including a 3,000-output chain. The report checks the observed rendered
camera, projection, selection and revision against its declared snapshot.

Actual GUI acceptance passed unit entry (250 mm stored as 0.25 m), mixed membership,
independent geometry/curve/handle/hook/cage filtering, native picking exclusions,
relationship navigation into read-only context, and exporting while the selected
object is renamed. The Issues GUI regression passed. Rendered workspace, inspector
and report images were visually inspected; final runs had no QML warnings.

Eight serial profiler trials used inspector closed/open/open/closed, with normal and
Ctrl-snapped dragging in each pair. Every report was complete; F12 during the gesture,
confirmation and undo passed. Mean inclusive input dispatch was 7.93–8.76 ms closed
versus 8.68–8.71 ms open for normal dragging, and 8.36–8.97 ms versus 9.38–9.48 ms for
snapping. These recorded times include profiler perturbation and ordinary background
load, not a claim about unprofiled overhead or physical display latency. The small
cube/body fixture does not qualify full-body performance. [Evidence and hashes](tasks/scp-workflow-evidence.json)
retain each trial and frame-submission statistics.

Direct ownership/coupling review: dependency evidence is shared between Issues,
inspection and report export; workspace policy owns reference/editability validation;
presentation filters feed cached native picking indexes. Unit conversion lives at
the dimensional input boundary. The report job owns frozen references and temporary
files/processes under the existing coordinator, without a second worker pool or save
barrier. Geometry queries remain native; Python handles domain graphs and orchestration.
Inspector details are opt-in and revision-gated. Numerical algorithms are unchanged.

The final executable was built from clean tracked source at `190d387`, version 0.1.7.0.
A relocated copy passed the complete portable gate with minimal PATH and developer
Python/Qt settings removed: import, attachments, primitives/deformers, deletion,
subdivision, save/reopen, render pixels, GUI, runtime profiling, verified issue repair,
and mixed workspace/units/image+JSON report export. Packaged viewport and report images
were visually inspected. The report retained revision 36, its selected loft, mixed
workspace, millimetres and selection filters; the other geometry remained transparent.
Executable/report hashes and the exact check list are retained in the compact evidence.

The preliminary relocated report test found Nuitka's `sys.executable` naming an absent
`python.exe`. A disposable interpreter-name alias isolated that launcher failure; the
production adapter now uses the actual compiled application's `sys.argv[0]`. The final
relocated export passed without any alias. The original distribution was preserved;
the qualified executable is `dist/0.1.7/AnthroForge.dist/AnthroForge.exe`, with companion
source archive `dist/AnthroForge-0.1.7-source.zip`. Keep the entire portable folder together.

## Issue reporting 0.1.6

The standalone issue framework adapts the addon's producer-scoped repository,
generation/epoch checks, registered detection, read-only presentation and explicit
verified repairs. The [component map](issues.md) traces the inspected addon sources
and their standalone owners. Current providers cover SCP/control evaluation,
missing accepted attachment surfaces, dependency-blocked outputs and failed tasks.
Fiber/skin geometry detectors await those domain systems; blocked dependencies are
not advertised as exact cycle paths.

At `069a05d`, the complete Windows development gate passed **512 tests**, Ruff,
formatting, typing, native CTest, native/PowerShell function checks, numerical
dependency imports and native loading. Seven existing Qt deprecation warnings
remain. Tests cover stale tickets, failed/malformed provider isolation, cancelled
checks and repairs, retry verification, undo/redo, Open/delete, dismissal, Manual
updates, cycles and retained geometry. Save with every policy remains available
during read-only diagnostic work. A subprocess detects and repairs an issue without
importing Qt or Blender.

Actual Qt GUI checks passed filtering, evidence inspection, selecting/framing
targets, dismiss/restore, explicit recalculation, fresh verification and New.
The Activity GUI acceptance also passed after sharing the incremental row model.
The final Issues run had no QML warnings; its rendered captures were inspected.

Eight serial recorded drag trials used Issues closed/open/open/closed for both
normal and Ctrl-snapped curve editing. F12 toggled inside the gestures; confirmation
and undo passed. All captures were complete and observed zero issue-model changes
during the drag intervals. Mean inclusive input dispatch ranged 6.34–6.68 ms normal
and 6.79–7.19 ms snapped. Recording perturbs timings; these are not unprofiled
overhead or physical display-latency claims. [Evidence and hashes](tasks/issue-reporting-evidence.json)
retain per-trial values and the excluded fixture-run explanation.

Direct ownership review, separately from test results: evidence and freshness have
one repository/reporting owner; detector lifecycle uses the existing coordinator;
registered repairs invoke existing operations and require new verification. The
desktop owns labels, navigation and keyed model projection. No anatomy payload,
undo state, geometry-output reservation or save barrier belongs to diagnostics.
Project/undo resets invalidate prior epochs; retired jobs release captured documents.
No second worker pool, Blender dependency or Python numerical geometry solver was added.

After outage recovery, the Windows executable built from clean tracked source at
`7e98a91`, with file/product version 0.1.6.0. The relocated distribution passed the
complete portable gate under a minimal PATH, including imports, attachments,
primitives/deformers, deletion/subdivision, save/reopen, rendering, GUI, runtime
profiling and the shared issue/verified-repair workflow. The packaged Issues panel
capture was visually inspected; all 30 QML files and three native DLLs match the
qualified inputs. Distribution and source archive are local artifacts under
`dist/AnthroForge.dist` and `dist/AnthroForge-0.1.6-source.zip`. Portable evidence is
under `build/issues-016/portable`; [the task handoff](tasks/issue-reporting.md) records
recovery and integration context.

## Activity presentation 0.1.5

The desktop now owns one stable `ActivityModel`. Its latest 40 jobs retain their
identities while changed roles update in place. The header consumes change-only
summary properties, and diagnostics metrics have a separate notification. Jobs,
scheduling, cancellation/retry eligibility, undo and save semantics retain their
existing owners. There is no second queue, timer or job registry.

Serial comparison against the 0.1.4 source/runtime snapshot at `3fa664d` used the
imported cube plus Body curve fixture, 120 moves per gesture, 1500×950 window at
1.5 pixel ratio on Windows 11. Each unrecorded condition ran baseline/candidate/
candidate/baseline; recording comparisons ran separately. Candidate production code
was `a4501be`, with measurement-tool changes in the working tree. Both sources used
the same native binaries. All 48 gestures passed their snapping and undo assertions.

| Gesture / Activity | Normal handler, before → after | Ctrl-snap handler, before → after |
| --- | --- | --- |
| Mouse / closed | 29.32 → 12.71 ms | 33.39 → 13.55 ms |
| Mouse / open | 31.58 → 13.10 ms | 35.80 → 13.80 ms |
| G-key / closed | 28.80 → 12.71 ms | 33.82 → 13.48 ms |
| G-key / open | 31.43 → 12.87 ms | 35.41 → 13.42 ms |

These are means of two unrecorded runs per version/condition: **55.9–62.1% less
synchronous input handling time**. Mean GUI frame callbacks improved from 55–65 ms
to 24–32 ms across these conditions. They measure GUI receipt of frameSwapped, not
physical display latency or GPU execution. Normal movement precedes Ctrl movement;
this experiment establishes before/after improvements, not a controlled Ctrl-only
cost. Background/thermal state is uncontrolled; system busy fractions ranged
27.3–32.0%, including the application. The nonactivating visible window prevents
desktop focus interruptions. This is a representative small editing fixture, not
full-body or arbitrary-project performance certification.

All eight recorded comparisons stopped cleanly without collector loss. Their 128 MiB
owned-storage budgets evicted older events. Within retained intervals, baseline
Activity model replacement occurred 116–170 times; candidate captures show zero,
with row/data notifications instead. Inclusive Controller.notify means fell from
27.5–33.1 ms to 3.5–4.3 ms while recording. Native snapping calls remain separately
attributed. Inclusive nested timings overlap and cannot be summed. Recording itself
still adds measurable overhead; the main speed claim uses unrecorded trials.

[Evidence JSON](tasks/activity-panel-015-evidence.json) retains run distributions,
load, hashes, profiler costs, retained intervals and scoped model counts. Reproduce
with `tools/activity_comparison.py`, then summarize with `tools/activity_evidence.py`.
After the shared retryability/property cleanup, four final unrecorded confirmations
passed with 12.19–14.17 ms handler means and correct snapping/undo. These are preserved
separately in the evidence JSON, not pooled into the counterbalanced comparison.

The development gate passed with 421 tests, lint/format, configured mypy, native build,
CTest/style, script rules, numerics and doctor. Qt model tests cover stable identity,
changed roles, history bounds, target names and terminal state behavior. Actual GUI
Cancel/Retry, failure messages, hidden updates, rename and New passed; screenshot
inspected. F12 during four drag variants, cancellation, focus/privacy and New/Open
recording passed. Perfetto imported the final snapped/open-panel trace as 84,053
slices with no nonzero error statistics.

The portable Windows executable was built from clean production checkpoint `ce64fc3`
(file/product version 0.1.5.0). A relocated copy passed `check_portable.py` with minimal
PATH and developer Qt/Python variables removed: imports, attachments, primitives,
deformers, deletion, subdivision, save/reopen, GPU image capture, GUI and desktop/headless
profiler reports. The desktop capture was visually inspected. Reports identify the
packaged build and correct collector capabilities. Release artifacts are local under
`dist/AnthroForge.dist` and `dist/AnthroForge-0.1.5-source.zip`; raw validation remains
under ignored `build/activity-015`. Source, evidence and recovery context are in Git.

## Original 0.1 baseline

Implementation and checks performed on 2026-10-16, Windows 11 x64. The original Blender addon
was read and exercised in a separate background process; its source and user scenes were
not edited. No Git remote was contacted through Git and no commits or PRs were created.

## Implemented

The imported-SCP editor includes OBJ/STL/PLY, canonical units, single-root hierarchy,
TRS/gizmos, attachments/locks/recapture/origin relocation, update modes, independent
copies, undo transactions, revision-aware asynchronous work, checkpoint saving, embedded
project storage, focused workspaces, visibility/picking, diagnostics and JSON authoring.
See quickstart.md for the complete user walkthrough and explicit release boundaries.

## Evidence

| Check | Observed result |
| --- | --- |
| Native engine and Qt geometry plugin | clang-cl Release build and CTest passed |
| Python checks | Ruff, configured strict mypy and 143 tests passed |
| Authored function rules | Python, native clang-tidy and PowerShell checks passed |
| Blender-reference attachment comparison | 72 cases; maximum matrix element difference 2.74e-6; acceptance 3e-5 |
| Actual mouse interaction | QTest drag changed the document, created one undo entry, and undo restored the prior transform |
| Desktop persistence | Asynchronous save/reopen preserved the assembly, without QML warnings |
| Visible geometry | Cube assembly and anatomical maxilla captures inspected visually |
| Numerical headless | Import/attachment/save/inspect flow; no Qt or Blender import |
| JSON line server | Publishes background results while waiting for the next request |
| Portable distribution | PySide deployment/Nuitka; relocated minimal-PATH import/save/inspection, GPU capture and desktop checks passed, including surface-pixel assertions; both final captures inspected |

tools/check.ps1 is the repeatable development gate. tools/gui_acceptance.py and
tools/check_portable.py are separate desktop/runtime acceptance gates. Their logs and PNGs
are local build artifacts; they are not source files or evidence of remote CI execution.

Blender reference generation: tools/capture_addon_parity.py, Blender 5.0.1
(a3db93c5b259). Cases cover both parent anchor modes, all three child anchor modes,
all three rotation strategies, follow rotation on/off and positive/nonuniform/reflected
parent scale. The fixture is tests/fixtures/addon_attachments.json. It is a synthetic
oblique tetrahedron, not production anatomy. Tests additionally cover locks, origin
preservation, freeze/rebind, queue overlap, failure, cancellation, saving and undo/redo.

The unchanged source native/migration/attachment_wave_reference.hpp was copied from
the addon's native/fiber_ccd/af_attachment_wave.hpp:
SHA-256 5BAF4DD3681EE327BF184639EAA2A8386DA43228004BE55345988E6F17097750.
Comparison found and corrected triangle corner reordering and negative-scale decomposition
in the new adapters. This qualifies these attachment cases, not all future addon features.

## Viewport measurement

Input: local BodyParts3D_v3_FMA53649_right_maxilla.stl, 14,148 triangles, 32 overlapping
instances (452,736 drawn triangles), 2160 x 1350 capture. During 90 mouse orbit updates:
mean frame interval 18.46 ms (about 54 FPS), p95 25.34 ms, maximum 35.92 ms; picking
p95 0.1115 ms; GUI tick p95 11.70 ms. No QML warnings. The script explicitly pumps the
event loop between input events and uses a high-resolution clock.

This is a local rendering/picking stress fixture with shared geometry and overlap.
It is not a full-body benchmark, a claim of 50 ms end-to-end input latency, or a guarantee
for arbitrary imports. The soft responsiveness targets remain goals for future feature work.

## Filesystem incident

E:/development/anthroforge began rejecting new files/directories with Windows error 112
while reporting about 70 GB free. The cause is unresolved. Source was preserved and work
continued in C:/Users/alexe/AppData/Local/Temp/anthroforge-01-work. Writes later recovered,
and the completed source was copied back to E:/development/anthroforge. The final native
build and development checks passed there. E: rejected large packaging copies again,
so the final Windows package was built in the temporary C: directory from matching source
and copied back to the project's dist folder. The cause was not established. Automatic review rejected removal
of a regenerable E: build cache, stating only "blocked by policy"; it was left in place.

The portable build initially failed with the installed MSVC toolset and with an overly
long MinGW cache path. Explicit MinGW selection and a short user-local Nuitka cache produced
the executable. The native C++ build still uses clang-cl; these are separate build stages.

The initial QT_QPA_PLATFORM=offscreen capture silently used software rendering and had
missing fonts/3D surfaces. It was rejected after visual inspection. Capture now uses
QQuickRenderControl with an owned GPU texture and readback, without showing a window.
Its metadata records the exact revision, finite scene geometry and window visibility;
portable acceptance also requires visible cube surface pixels. A successful exit code
or nonempty PNG alone is not capture acceptance.

## UI refresh — 2026-10-16

The desktop now uses a charcoal theme with compact vector-icon controls, classic menus,
resizable panels, searchable/collapsible outliner, grouped properties with named enum
choices, axis-colored transform fields, viewport tools and orientation shortcuts, an
optional reference grid, and a collapsible activity area. Editor styling stays in QML;
the application and numerical contracts are unchanged.

tools/ui_acceptance.py exercises actual keyboard/mouse input: text-safe shortcuts,
search, numeric commit/undo without reapplying on later blur, hierarchy and property
collapse, view orientation, splitter dragging, compact 1050x680 and normal 1440x900
layouts, and the empty document. Captures were inspected. tools/gui_acceptance.py
continues to cover transform drags, one-step undo, and asynchronous save/reopen.
The full development gate passed with all 143 tests after the refresh. The updated
portable app also passed numerical, desktop, and GPU capture checks with a minimal PATH;
the final desktop image was inspected without QML warnings.

The reference conventions are Blender's area/topbar/status-bar layout and Maya's
compact attribute editing. The implementation uses Qt Quick Controls and SplitView;
icons are project-authored SVGs. This does not reproduce either product's complete UI.

## Dropdown and viewport refinement — 2026-10-16

Dropdown indicators now use a vertically centered SVG chevron instead of a font
glyph. Imported meshes are opaque by default, with camera-relative studio lights,
less ambient fill and much less selection emission. This preserves authored colors
while making faces and concavities easier to read. X-ray is an explicit temporary
view setting (button, View menu, or Alt+Z); outside-workspace context remains faint
and unpickable. Transform handles now refresh their projected positions after
camera movement and framing, instead of remaining at stale screen coordinates.

Compared selected and unselected cubes and the 14,148-triangle right-maxilla fixture
before and after; inspected X-ray, focused context and compact/full-size properties.
The grid/cube overlap is physical intersection with the Z=0 reference plane, not
evidence of failed opaque depth testing. An extra depth prepass and an ambient
occlusion trial were not retained. Captures are in build/shading-before,
build/shading-final, build/ui-xray.png and build/visual-portable.

The full development gate passed (143 tests), alongside actual mouse drag/undo and
save/reopen acceptance. UI acceptance also checks X-ray by mouse and shortcut,
text-entry isolation and unchanged document state. The updated portable QML passed
minimal-PATH numerical, desktop and GPU-capture checks without QML warnings.
The same 32-instance navigation fixture measured a 20.17 ms mean frame interval
(about 50 FPS), 35.01 ms p95 and 0.1092 ms picking p95. This is a local validation
sample, not evidence of a performance improvement over the earlier run.

## Task coordination and parent/child updates — 2026-10-16

One TaskCoordinator now owns job lifecycle, worker capacity, output reservations,
publication and checkpoints. Dedicated attachment, mesh-import, project-open and
project-save schedulers assess metadata before admission and again at dispatch.
Attachment estimates include current document packing, affected objects and recapture
counts; measured timings refine subsequent estimates. File operations remain workers
with zero artificial delay. See architecture.md for the policy limits and extension points.

Bounded Live attachment work can complete before the transform command returns, using
the same native evaluator and publication checks as worker jobs. Larger interactive
requests coalesce for 16–100 ms according to estimated cost. Replacements preserve the
first pending time, including across authored invalidation; resource contention may add
queue time. Diagnostics expose estimated/actual costs, delay and execution mode.

The final development gate passed: Ruff, strict mypy, native build/CTest, style checks,
161 Python tests, numerical headless checks and native discovery. Added regression cases
cover immediate propagation, shared inline budget, measured overruns, fresh dispatch
inputs, complexity changes while queued, maximum coalescing age, overlapping writers,
publication gates, save snapshot estimation, pending-save behavior and undo cancellation.
Actual GUI drag/undo/save/reopen and the UI interaction checks passed without QML warnings.

tools/scheduling_acceptance.py observed the two-cube viewport model at frame signals
during 20 actual mouse-drag updates. All 20 updates completed inline; 29 frame observations
showed a maximum relative parent/child offset error of 3.33e-16 m. The slowest update took
0.175 ms (rounded up). Running the same fixture with background-only policy exposed
0.0396 m of relative lag. Captures were inspected. This verifies coherence on this fixture;
it does not measure end-to-end input-to-photon latency or qualify arbitrary anatomy.

Synthetic 10-update probes at 16 and 64 entities stayed inline, with maximum observed
costs of 0.451 and 1.242 ms. At 256 entities all updates used workers; maximum observed
cost was 7.783 ms and planned delay was 34.607 ms. These are local tuning evidence,
not hard execution bounds. Synchronous work cannot be forcibly preempted; timing
feedback demotes subsequent similar requests after an overrun.

The portable executable was rebuilt on E: from matching final source. Minimal-PATH
native discovery, import, attachment, save/inspect, GPU capture and desktop checks passed;
the desktop capture was inspected. A separate compiled batch verified dedicated import
policies and both immediate attachment edits through the packaged authoring API.
Runtime reports and captures are in build/coordinator-portable. The corresponding source
archive was refreshed after these changes.

## Primitive and deformer release 0.1.2

Implemented on Windows x64 against the confirmed primitives_012.md contract. The release
includes editable imported, connected-loft and curve-deformed body definitions; shared
Hook controls and lattice cages; ordered bindings; Simple Solidify; component editing;
and the same operations through the headless API. Apply/Bake has no command or UI action.
The runnable examples/primitives.json builds a connected shell, a shared cage with a Hook,
a curved capsule and an imported cube, then saves the editable document.

The implementation separates authored construction revisions, SCP poses, accepted geometry
results and presentation. Schema 2 stores source data, all parameters and shared relationships
with the selected revision's accepted meshes. Schema 1 migrates to imported definitions.
Object writers remain exclusive, while dependency reads distinguish pose, control, cage
and geometry outputs. Manual prerequisites supply accepted results with pending provenance;
actual cycles terminate unsuccessfully without suppressing unrelated components.

### Qualification evidence

| Check | Evidence |
| --- | --- |
| Development gate | Ruff, configured strict mypy, native Release build/CTest, native/script function checks, 352 Python tests, numerical headless checks and native discovery passed |
| Native reference coverage | 141 primitive/deformer comparisons: 49 curve/anatomical checks and 92 modifier/resize/shell checks, plus the existing 72 attachment comparisons |
| Actual anatomical references | Rib and mandible sampling, clavicle Hook continuity, brow cage/Hook/tilt and pelvic closed curves; compact pinned fixtures include source hashes |
| Construction and topology | Shared loft seams, caps, thickness winding, canonical triangulation, target-stage ordering, topology locks/unlocking through both application and inspector |
| Lifecycle | Mixed update modes, pending Manual inputs, missing inputs, real cycles, capture-only reads, overlapping writers, dispatch snapshots, cancellation, undo/redo, checkpoint saves and geometry collection |
| Persistence | Schema-1 migration and schema-2 round trips retain original imported vertices, editable curves, controls, sharing and accepted results |
| Desktop workflow | Creation, curve pointer hover/click/Shift selection, inspector synchronization, lattice edits, Hook weights, body-base targeting, hidden/unpickable controls, save/reopen; no QML warnings |
| Coordinate frames | Connected endpoints survive owner motion; follow changes and origin relocation preserve world placement; control gizmo motion under a rotated SCP follows its displayed world axis and undoes coherently |
| Complete example | The headless batch produces all three primitive families; the saved connected loft and curved capsule were inspected in the production GUI |
| Group framing | Empty groups frame visible descendant geometry; native bounds cover rotation, reflected scale and relocated geometry origins |
| Existing editor regression | Mouse drag/undo, save/reopen, text-safe shortcuts, layout/inspector interactions and parent/child scheduling acceptance passed without QML warnings |
| Portable Windows runtime | Final Nuitka executable relocated to a separate C: folder passed native discovery, imports, attachments, primitive/deformer construction, save/inspect, GPU capture and desktop smoke checks with a minimal PATH; final images inspected |
| Distribution | Product/file version 0.1.2.0, Python wheel resource checks and corresponding AnthroForge-0.1.2-source.zip contents verified |

Blender references use 5.0.1, build a3db93c5b259. Synthetic and source-scene JSON fixtures
are under tests/fixtures/primitives; generators are maintained under tools. Numerical
tolerances are explicit in the tests (typically 2e-5, with 5e-5 for source-scene sampling).
Connected loft boundaries are intentionally different from the disconnected Blender
node strips and have separate topology checks. These comparisons qualify their exercised
settings, not arbitrary Blender scenes. Original source .blend files were not saved or
changed. Their verified SHA-256 values are:

- skull_muscles.blend: `4855042F259135C569C3E89B50DF5D0441E6794BEF5E774AEBF924FD8372287E`
- skeleton_comb_base.blend: `1049C9CEF5D0E94735E20E1F3E313CDB845A67C6554CCF3A98E81DA98B813FF2`

### Responsiveness measurements

tools/primitive_acceptance.py --performance exercises a shell with 66,560 vertices,
133,116 triangles, nine render chunks and 1,000 cage points in a 1500 x 950 window.
It performs 19 edits, including 18 rapid superseding edits, and 120 native component picks.
The previous complete mesh remained visible throughout staged replacement. The local run
recorded the following values; milliseconds are wall-clock measurements, not guarantees.

| Operation | Samples | Mean ms | p95 ms | Maximum ms |
| --- | ---: | ---: | ---: | ---: |
| Edit command, including UI refresh | 19 | 25.14 | 43.69 | 44.48 |
| Dispatch preparation | 18 | 0.048 | 0.077 | 0.079 |
| Result adoption | 4 | 0.392 | 0.438 | 0.487 |
| Component picking | 120 | 0.027 | 0.040 | 0.139 |
| Cancellation request | 62 | 0.004 | 0.009 | 0.017 |
| Cancellation completion | 34 | 11.56 | 34.02 | 47.72 |
| Frame interval | 73 | 32.31 | 56.50 | 68.37 |

The two completed native construction jobs took 467.80 and 526.40 ms. Queued cancellation
and active-worker cancellation share the completion sample set; it is not a worst-case
native interruption bound. Initial uncached inspector/publication refresh measured about
264.6 ms mean and 342 ms p95 per edit on this fixture. Caching presentation snapshots and
separating geometry notifications from activity updates removed that repeated work.
The final sample is approximately 31 FPS on average, but p95 frame intervals exceed the
soft 30 FPS goal. This test does not measure OS input-to-photon latency or a full-body model.

### Ownership and coupling review

Reviewed separately from test results. core records own immutable authored data and accepted
provenance; construction_policy and application commands enforce topology and workspace rules
for every client. Native adapters own numerical work and return complete buffers/BVHs.
Task-specific policies estimate work; TaskCoordinator alone owns admission, output reservations,
cancellation and publication. Dependency ports and capture-only observations avoid both
whole-object invalidation and false pose/geometry cycles. Publication merges its declared
outputs into current state rather than overwriting a newer unrelated edit.

Geometry reachability covers current state, undo entries, checkpoints and running snapshots;
viewport staging and displayed frames lease native handles separately. GUI components own
selection and presentation, not alternate deformation rules. The existing SCP asset field
remains a compatibility alias for accepted geometry; central geometry queries replace
imported-asset assumptions. Thin dynamic Qt adapters remain outside the strict application
typing boundary. Initial scheduler coefficients are heuristics refined by measured costs,
and cancellation is cooperative at native checkpoints, not preemptive.

Local qualification reports and inspected images live in build/primitive-review. The
maintained tools reproduce them; generated reports and production anatomical binaries
are not included as source fixtures. Native provenance and source hashes are recorded in
native/migration/BLENDER_PRIMITIVES.md and blender_501_sources.json, with original attribution.
The final relocated-runtime report and captures are under build/primitive-review/portable-final;
the delivered executable is dist/AnthroForge.dist/AnthroForge.exe. Preserve the entire
portable folder when moving it. No Git remote operations or commits were performed.

## Current scope limits

Only Windows was executed locally. The CI workflow is prepared but was not run remotely.
No skin/export, Blender-project conversion, linked mirroring,
crash recovery or persisted undo is claimed. See the confirmed specification for future work.


## Usability release 0.1.3

Implemented and inspected on Windows 11 x64, 2026-10-17. This release changes the existing
editing workflow; it adds no primitive families. The original addon deletion implementation
was inspected: it cleared invalid parent references rather than promoting children. The
standalone now implements the user's requested promotion semantics, including the confirmed
empty grouping root replacement.

- Move: world-axis arrows, plane handles and a view-plane center. Rotate: world-axis rings.
  Scale: local-axis squares and a uniform center. Shift provides precision; Escape cancels.
  Shared deltas compose world rotation correctly and preserve negative scale and pivots.
- Curve-edit transparency is temporary presentation. The selected SCP's orange silhouette
  comes from a depth-tested selection mask and screen-space edge dilation; open lofts,
  curved bodies and imported meshes were inspected in actual GUI captures.
- Central shortcut registry and context policy cover existing shortcuts and Delete. A shared
  dialog serves keyboard, tree and inspectors. Text entry, modal dialogs, active drags and
  blocked saves retain their interaction boundaries.
- Core deletion preserves children/world poses, recaptures their new attachments, detaches
  referenced controls, rejects obsolete output and reschedules surviving dependencies.
  Root replacement, empty documents, focused workspaces, undo/redo and save/reopen are covered.

### Validation evidence

The development gate passed: 364 Python tests, strict typing, Ruff, native build/contract,
clang-tidy, script checks, numerical imports and native doctor. Existing Blender fixture
parity remains passing. The native style run prints upstream-header warning totals; there
were no failing authored-code diagnostics.

`tools/usability_acceptance.py` passed real pointer checks for 45-degree rotation in orthographic and perspective views, axis and
uniform scaling, two-axis/free movement, coherent undo and Escape rollback. It also passed
text-field Delete protection, modal shortcut blocking, keyboard root deletion, tree deletion
and opacity restoration without an authored edit. No QML warnings were reported.
Existing UI, scheduling and primitive interaction/workshop acceptance passed. The scheduling
check observed 20/20 small attachment updates inline with maximum parent-child displacement
error below 3e-16 metres.

`tools/usability_acceptance.py --render` qualified a 512-sample/64-strip thick loft with a
1,000-point cage. The old complete surface remained displayed during staging. Mask delegate
counts matched displayed/staged mesh delegates after replacement, deletion and undo, confirming
that the additional scene does not retain deleted resources. The mask shares the main geometry
objects instead of rebuilding mesh buffers.

The paired orbit run measured frame intervals with outline enabled at mean 17.3 ms / p95
30.8 ms, versus 23.8 / 38.8 ms without it in the preceding pass. These are short, order-sensitive
GUI measurements, not evidence that the added pass speeds rendering up. The large edit command
took 23.6 ms; measured result publication was below 0.5 ms. Full interaction/capture runs include
startup, file operations and screenshot stalls and had p95 intervals around 75–82 ms. These data
support the soft responsiveness goals for the measured orbit, not a universal FPS guarantee.
Captures and machine-readable reports are in ignored `build/usability-review`.

### Ownership review

Reviewed directly in this task, separately from test results. Keyboard mapping/context policy,
gizmo geometry/hit testing, paint, transform application, deletion semantics and silhouette
rendering have distinct owners. Both desktop and headless deletion use application commands.
No authored state carries hover, outline or editing opacity. Native geometry ownership and
staged publication remain authoritative; the new render pass follows the same active chunks.
The existing axis-drag API is retained as a compatibility adapter. No speculative scheduler,
renderer replacement or duplicate hierarchy implementation was introduced.


A perspective-only diagnostic exposed about 5 degrees of error in the first projected-ellipse
rotation approximation. It was replaced with mouse-ray/rotation-plane intersection. The
final 45-degree perspective gesture measured 44.57 degrees with integer-pixel mouse input;
orthographic and perspective regression checks both pass. Edge-on rings retain a screen
tangent interaction where a ray-plane intersection is ill-conditioned.

### Distribution qualification

The Nuitka portable build is `dist/AnthroForge.dist/AnthroForge.exe`, product/file version
0.1.3.0. A fresh copy at `C:/Users/alexe/AppData/Local/Temp/anthroforge-013-qualified`
passed with a minimal PATH and no development Python/Qt settings: imports, attachments,
primitive/deformer evaluation, single-SCP and root deletion, saving, inspection, GPU capture
and GUI smoke checks. The compiled deletion check saved/reopened the promoted hierarchy.
The packaged desktop was visually inspected, including its selected geometry outline.
Reports are under `build/usability-review/portable`. Packaged QML/JavaScript/icons match
the tested sources byte-for-byte. The shader is embedded in the native viewport DLL.

The wheel, source distribution and `dist/AnthroForge-0.1.3-source.zip` were regenerated;
the archive includes the new interaction, deletion and shader sources and excludes the
unrelated legacy root `__init__.py`. Changes remain uncommitted. No Git remote operations
were performed.


### Curve editing follow-up (2026-10-17)

The 0.1.3 follow-up adds held insertion preview, repeated left-click confirmation,
Ctrl surface snapping during direct-point and Move-gizmo drags, and distinct curve/point/handle
colors. Modifier bindings belong to the keyboard manager and can be rebound independently of
interaction code. Ctrl-click extends selection; its click action is deferred so holding Ctrl
before dragging a selected point still starts a snap gesture.

The development gate passed with **387 tests**, including open/closed subdivision with all four
handle modes, transformed closest-curve queries, invalid requests, unchanged attachment mesh
connectivity, undo, editable persistence and held-input lifecycle. Existing native Blender
reference comparisons remain passing. Native/style/type checks passed.

`tools/curve_interaction_acceptance.py` passed actual Qt keyboard/mouse gestures for repeated
insertion, release cancellation, switching snap targets, self exclusion, read-only focused
workspace context, snapping with Ctrl pressed before or during a drag, modifier rebinding,
text-focus suppression, window-deactivation cancellation and one-step undo. Direct dragging
and gizmo snapping were checked in orthographic and perspective views. It reported no QML
warnings. Existing primitive-interaction, gizmo/deletion and staged-render acceptance also
passed. Captures were inspected under `build/curve-interaction-review`.

These tests exposed inaccurate orthographic ray construction and perspective free-drag depth
in the earlier projection helper. Shared camera-based rays and view-plane translation replaced
that helper; surface hit positions and released-snap plane motion now match the displayed
camera in both projections. The editing overlay preserves type colors above the selection
outline, using shared camera parameters and native marker buffers.

The recorded gesture run measured curve projection p95 **0.084 ms** and surface snapping p95
**0.094 ms** on the small, transformed loft/two-SCP fixture. Complete capture runs include
startup, image capture and scripted waits (frame-interval p95 about 78 ms); these are not an
interactive FPS guarantee. The large staged-render regression retained old geometry and passed
resource-lifetime checks; result publication stayed below 0.5 ms in that run.

Direct ownership review: input bindings, transient gesture state, native curve queries,
authored subdivision and presentation have separate owners. Preview does not enter history;
confirmed insertion and snapping use existing shared commands and transactions. Snapping uses
leased displayed geometry, including read-only context, and creates no persistent attachment.
Native query buffers are cached by authored geometry/frame revision. No scheduler replacement
or duplicate Blender runtime was added.

The rebuilt portable application passed all checks from a separate folder with a minimal
PATH and no development Python/Qt settings. The compiled batch check now covers subdivision
and editable save/reopen as well as existing imports, attachments, deformers, deletion,
rendering and desktop startup. Qualification exposed and fixed two integration defects:
offscreen viewports now supply an inactive input context, and batch references can index
the tuple-valued curve collections returned by inspection. The latter has a regression test.
The report and packaged screenshots are under `build/curve-interaction-review/portable`.

### Axis views and continuous editing (2026-10-17)

1/2/3 now centers the active selection in X/Y/Z orthographic views and preserves apparent
zoom. G/R/S starts modal mouse transforms with confirm/cancel. View changes capture a new
gesture reference frame while retaining the original transaction and undo snapshot. Existing
direct-point and gizmo drags use the same recapture boundary. Mouse coordinates are copied
when captured; a Qt value-property alias initially made the modal start position follow the
cursor, which the actual-input acceptance exposed and the value copy corrected.

Surface snapping supports signed normal offset through the wheel, with reset on middle-click
or modifier release. Reset input is consumed before it can become orbit or transform release.
Normals are evaluated natively with nonuniform/mirrored transforms. Rotation/scale of curve
points includes their handles; previously only the selected point positions were transformed.
The correction is shared by keyboard and gizmo transforms and has regression coverage.

The development gate passed **396 tests**, including native axis rotation, transformed normals,
handle transformations/cancellation and captured reset-button release. Native contracts,
type/style and 15-line checks passed. `tools/view_gesture_acceptance.py` verified actual
keyboard/mouse/wheel behavior for zoom/centering, uninterrupted direct/gizmo/modal edits,
axis constraints, one-step undo, signed offsets, target switching and text-entry isolation.
Existing curve-interaction and usability acceptance also passed with no QML warnings.
Captures under `build/view-gesture-review` were visually inspected.

Direct ownership review: keyboard policy owns bindings; physical input capture owns wheel/
button delivery; gesture adapters own pointer mapping; the existing transform adapters own
recapture and shared commands. Native code owns axis-angle conversion and surface normals.
No new history, scheduler or persistence mechanism was introduced. Camera changes remain
workspace presentation state; snapping offset remains temporary gesture state.

The rebuilt portable application passed qualification after relocation to
`%TEMP%/anthroforge-013-views-qualified`, with a minimal PATH and development Python/Qt
settings removed. Imports, attachments, primitives, deformers, deletion, subdivision,
save/reopen, rendering and GUI startup passed. Packaged QML and both native DLLs match the
tested sources/build. The packaged desktop capture was visually inspected; qualification
results and captures are under `build/view-gesture-review/portable`. The detailed gesture
acceptance above runs against the source application, separately from portable smoke checks.

## Codex Cloud preparation (2026-10-17)

Revision `cb51bbc` passed [remote Linux and Windows qualification](https://github.com/ctrl0alt0del/native_anthroforge/actions/runs/39039142051).
Both jobs built the portable C++ library and passed CTest, all **396 pytest tests**, the
separate primitive/deformer CLI save/reopen workshop, and Python wheel/source packaging.
Ubuntu 24.04 ran the exact `tools/cloud/setup.sh`, including host library checks,
ShellCheck and clang-tidy, then successfully ran refresh in a separate shell.
Windows Server ran the same core gate. The local Windows development gate also passed
396 tests, native/PowerShell style checks, optional numerical imports and native loading.

The clean runners exposed platform-specific file-lock typing and compiler diagnostics
inside imported Happly, Eigen and the preserved addon attachment kernel. The fixes keep
warnings scoped to those include boundaries; authored native code retains warnings as
errors. The algorithms and immutable migration reference were not changed.

The actual Codex Cloud setup exposed an unprivileged base image without sudo and a
read-only home binary/cache location. Setup now uses pinned uv, Python, validation tools
and cache under the checkout. It can use existing compiler/runtime libraries, checks
that they load, and retains the complete gate. It does not silently skip missing tools.
The `cloud` dependency group pins clang-tidy and ShellCheck without changing runtime
dependencies or requiring Linux desktop release support.

Ownership review: shell scripts own environment preparation and refresh; `check_core.py`
owns the cross-platform validation sequence; storage owns platform-specific locking;
native include adapters own imported compiler accommodations. Application scheduling,
geometry algorithms and UI behavior are unchanged. Cloud/core checks do not certify
Windows GUI gestures, GPU behavior, standalone executable packaging or new anatomy.
Account environment publication and a fresh-task check are tracked separately from CI.

The actual Codex Cloud setup session also passed at `cb51bbc` on Linux/glibc 2.41:
`bash tools/cloud/setup.sh` exited zero in 136 seconds; its JUnit report recorded 396 tests,
zero failures/errors/skips (4.349 seconds). The report confirmed the owned native library,
Python 3.12.12, NumPy 1.26.4, PySide6 6.12.0 and native style checking. Refresh and native
loading passed in a new shell, with no tracked changes. This was a fresh setup after the
first trial's executor became unavailable, not a report inferred from GitHub CI.

The environment was published as **AnthroForge Standalone**, with **Only me** visibility.
A fresh task then loaded the preserved uv 0.9.29, Python 3.12.12 and native ABI 1 without
setup or dependency installation, and passed the entire gate with `UV_OFFLINE=1` and
Python downloads disabled: **396 passed, zero errors/failures/skips** (4.520 seconds).
Native contracts/style, CLI save/reopen and wheel/source checks passed; Git remained clean.

Offline refresh could not resolve the editable-build helper `editables` from cache. Normal
refresh initially hit the default shell sandbox's network restriction. Retrying through
the runtime's supported additional network-permission path passed with the Package managers
allowlist enforced. Separate-shell doctor and the CLI workshop passed afterward. This did
not change security settings, source files or Git remotes. Dependency refresh may require
package access; fully offline dependency changes are not a promised capability.

Account evidence: [setup session](https://chatgpt.com/local/01a14a2e-948d-7224-908c-a4776cc8a044)
and [fresh-task verification](https://chatgpt.com/local/01a14a36-2da3-7609-8e41-9bab9cffa04b)
are account-private records. Source/build qualification is at `cb51bbc`; later documentation
updates do not change the qualified code. The publication capture is a local ignored artifact
under `build/cloud-review`, not a required runtime file.

## Camera restoration (2026-10-17)

At `a3667ad`, the Windows development gate passed all **396 tests**, native build/CTest,
style/type checks, numerical dependency imports and native loading. The real-window
`camera_restore_acceptance.py` passed perspective and orthographic restoration after mixed
axis keys/buttons and projection/zoom changes, repeat/no-op restore, subsequent snapshots,
the View menu action, text focus, rebinding, workspace invalidation and persisted camera values.
`view_gesture_acceptance.py` passed restore during direct/gizmo/modal editing and Ctrl-snapping,
with no point jump, retained snap offset, one-step undo and cancellation. Neither run reported
QML warnings. Original/restored and active-edit captures were inspected visually under
`build/camera-restore-review` and `build/view-gesture-review`.

Ownership review: the existing viewport owns a bounded, transient camera snapshot and the
shared camera-change/rebase lifecycle. Keyboard bindings remain in the keyboard manager;
buttons and menu invoke the same viewport operation. No anatomical state, scheduler, native
geometry or project-format responsibilities changed. Workspace persistence stores the current
camera using its existing path, while the temporary return point is cleared on camera loading.

The full Windows `tools/package.ps1` rebuild passed. `tools/check_portable.py` passed with
minimal PATH: import, attachments, primitives/deformers, deletion/subdivision, save/inspect,
GPU rendering and GUI smoke checks. Packaged camera QML hashes match the qualified source;
the packaged desktop capture was inspected. Evidence is in `build/camera-restore-portable-check`.
The source archive and portable documentation were refreshed; these build outputs remain local.

## Runtime profiler 0.1.4

Validated on 2026-10-17, Windows 11 x64, Python 3.12.12 and Qt/PySide6 6.12.0.
The recording service, native Qt adapter, UI controls, runtime API and report format
are described in [profiling](profiling.md). The Activity production fix remains deferred.
[Compact qualification evidence](tasks/runtime-profiler-evidence.json) preserves
measurements and capture hashes without committing the large raw traces.

The development gate passes **415 tests**, plus Ruff, mypy, native CTest, native and
PowerShell function/style checks, numerical checks and the native doctor. Coverage
includes normal lifecycle/retry, unavailable collectors, active/queued/interrupted
jobs, cancellation, native hook restoration, repeated captures, byte/time eviction,
delayed batches, bounded pending spans and clipping at recording boundaries. A fresh
headless process creates/evaluates a body and exports a report without importing Qt.

The final portable executable was built from clean tracked source at `55bf4e2`, with
file/product version 0.1.4.0. A relocated copy passed import, attachments, primitives,
deformers, deletion, subdivision, save/inspect/render, GUI and profiling checks under
a minimal PATH with developer Python/Qt settings removed. Both packaged report bundles
were complete; Qt profiling services excluded debugger/inspector. Perfetto imported
the packaged trace as 5,282 slices with no nonzero error statistics. The actual packaged
viewport was visually inspected. Distribution and source archive remain local artifacts
under `dist/AnthroForge.dist` and `dist/AnthroForge-0.1.4-source.zip`.

Actual Qt mouse/key acceptance passed normal and Ctrl-snapped dragging with Activity
both hidden and shown, F12 start/stop inside the gesture, confirmation, cancellation,
undo, repeated recordings and text-focus preservation. Typed text was absent from the
capture. The final five drag reports had no collector loss, and retained intervals
were inside the requested start/stop times. Screenshots were visually inspected.

From the final visible-Activity snapped report alone: Activity.qml:23 binding mean
24.15 ms, Controller.notify 30.79 ms, native pick 0.084 ms and surface-normal query
0.019 ms. There were 250 generic model replacements across observed UI models.
These inclusive timings overlap and include recording perturbation. They establish
attribution, not an unprofiled speed claim or proof of a snap-specific 2x regression.
Perfetto v58.2 imported the final trace as 114,256 slices with no nonzero error stats.

A 34-second stress capture with a two-second window received 641,880 events,
intentionally evicted 611,079, retained exactly two seconds and had zero collector
loss. Default desktop storage is partitioned conservatively: 64 MiB retained event
storage plus 64 MiB reserved for bounded queues, metadata, observers and export.
A default-budget recording separately reached the byte bound, evicting oldest events
while staying below 64 MiB of charged retained storage. Qt's transient producer
allocations are outside this owned-storage budget; it is not a process RSS ceiling.

### Overhead interpretation

Trials ran serially with system utilization recorded, without concurrent builds.
The initial normal/snapped handler means were 24.88/29.18 ms with Qt support disabled,
25.75/29.09 dormant, and 35.25/40.52 recording. Four counterbalanced trials per idle
mode after 60 warm-up moves gave 31.62/32.01 versus 31.30/32.38 ms; run standard
deviations were 0.26–0.57 ms. Warm-up adds Activity history, so absolute values from
these series must not be pooled. Later valid foreground comparisons changed the
sign of the cold idle difference. A separate nonactivating-window series is retained
as supplementary evidence; it changes presentation conditions.

The small cold/first-use differences are not a zero-overhead guarantee. No stable
steady-state idle penalty was resolved above the observed variation in the warmed
series. Recording has a substantial, measured observer effect in this binding-heavy
case; directly measured costs and comparison estimates are reported separately.
Forced disk caching was investigated and not adopted. Two supplementary foreground
trials lost window focus and canceled their gesture; they are excluded, not counted
as passing timing trials. The diagnostic now detects this interruption explicitly.

### Ownership review

Reviewed separately from tests: the recorder owns no anatomy, accepted geometry,
undo entries or scheduler policy. The desktop controller owns the Qt-independent
service across document replacement; headless sessions own or explicitly borrow it. Shared
commands, transactions, native binding registration and coordinator stages supply
coverage. Qt private APIs are isolated in one pinned native adapter. Render events
stay in C++; the generic model observer is installed only during recording. Stop
freezes application spans, clips delayed Qt data, resets periodic flush wiring and
streams bounded records to atomic export. Failure retains a frozen capture for retry;
restarts wait for the previous exporter to finish. No Activity-specific timing marker
or production Activity optimization was introduced. GPU timing, detailed stack
sampling and report viewing remain outside this release.
Final lifecycle review found and corrected New retaining stale recording controls and
headless Open losing task observation. The full GUI acceptance passes after the fixes,
including New before recording and New/Open during recording. Focus and gestures are
preserved; closing a borrowing session releases native observation without stopping
the application recorder.
