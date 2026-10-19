# Unified tissues 0.2.2

- Task branch: `codex/unified-tissues-022`
- Integration branch: `main`
- Starting revision: `6f33380660c9421585b0898b068d33b4f5232fd3`
- Status: complete; canonical 0.2.2 package qualified
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: desktop chat, direct work (no delegated writers)

## Outcome and acceptance

Implement the user-approved 0.2.2 plan: unified TissueVCP, attached Point/Anchor
and Surface/Membrane construction, native inflation/relaxation/stacking, shared
attachments, desktop/headless workflows, schema 4 and a qualified portable release.
The previous 0.2.1 distribution is preserved. See the
[specification](../specification_022.md) and [implementation plan](../implementation_022.md).

## Confirmed decisions

- One TissueVCP; anatomical labels and presets do not select algorithms.
- Shared Anchor/Fiber/Membrane sources; explicit independent copies.
- Bone anchoring may be indirect through other tissues.
- Stacking requires surface-based providers and receivers; capability contract
  must allow future base adapters without changing the tissue entity.
- Preserve per-part/side settings, current unstacked display on stacking failure,
  and the final-surface dependency barrier; no silent successful fallback.
- Schema 4 only; reject earlier formats, including 0.2.1 schema 3.
- No mirroring, skin, Blender conversion, reconstruction/fitting, or dynamics.
- Preserve scheduler/history/save/startup/export semantics and 15-line functions.

## Current state

Completed the approved workflow and documentation. The full development gate passes;
final post-version regression is **1,288 passed** with 732 existing Qt deprecation warnings.
All 24 full-QML/hidden-GPU scenarios pass. Both temporary and canonical portable suites
pass with minimal PATH, including four ready tissues, automatic stacking, explicit Final
Anchor binding, schema-4 save/reopen, profiles and rendering. No visible desktop input
or hands-on acceptance is claimed. Geometry/parity, profiler and ownership-review evidence
and limitations are consolidated in [development status](../development_status.md#unified-tissues-022).

Deliverables: `dist/0.2.2/AnthroForge.dist` and `dist/AnthroForge-0.2.2-source.zip`.
The executable was built from clean tracked `3b0869c`; following changes are documentation
sign-off only. QML/native assets and dependency notices match. Version metadata is 0.2.2.0.
Only the unrelated untracked root `__init__.py` is preserved outside the task. Local build
logs, captures and profiling reports stay under ignored `build/022-tissue/`; maintained
fixtures/reproduction tools and the complete code/context are committed for recovery.

## Checkpoint journal (earlier pending work is superseded by current state)

Full `tools/check.ps1` now passes: native build/3 CTests, all authored native style checks,
Ruff/format/configured mypy, script checks, **1,287 tests** (732 existing Qt deprecation
warnings, 94.72 seconds), numerical imports and the native doctor. The new separate fresh-
process tissue-example test also passes, proving the complete example does not import
PySide6/Shiboken/Blender; function-length checks pass. It was added after full-suite
collection. All 24 GUI scripts passed after the two targeted fixes below. The explicit
capability matrix, walkthrough and ownership/coupling review are written. Cached profiler
captures are complete with no reported loss, 54 hits/6 misses/6 insertions and explicit
input/candidate invalidation reasons. Portable compilation/checks remain pending.

All 24 full-QML/hidden-GPU tissue qualification scripts now pass. Two failures were
diagnosed: the Anchor test selected a hidden region selector with the same object name,
so its lookup is now scoped to the actual Point inspector; the relaxation scenario used
a thin curved shell that the quality guard correctly rejected (3,150 new crossings),
so its valid-path scenario uses the already-qualified reversed 0.2 m shell. Invalid
retention/recovery remains covered separately. Pouch creation explicitly verifies the
donor-default rejection and explicit recovery. Inspected branched envelope, relaxed
stacked shells and skull-fixture captures. Skull integration is not anatomical fitting.

The complete native style gate exposed missing internal declarations in included stacking
files. Shared helper declarations now live in the internal header; standalone clang-tidy
passes for plan/resolve/group/validation and the owning TU, with the same numerical code.
The full development gate is running again (`build/022-tissue/full-gate.txt`). A temporary
portable candidate is building under `build/022-tissue/package`, not a second release dist.
New `tissue_portable.py` exercises the JSON example, schema 4, four ready tissues, final-role
Anchor, automatic stacking, profiling, hidden GPU rendering and offscreen desktop startup.
It has not passed the packaged executable yet. Version remains 0.2.1. The capability matrix
and migration evidence map are consolidated; final walkthrough/release records are pending.

The new executable example exposed a publication feedback loop that the original parallel
source-creation fixture missed: a second Fiber captures support on an existing Tissue, and
its consumer becomes a stacking candidate. Publishing the first Tissue's plan previously
scheduled that Fiber through the final-output barrier even when final geometry was unchanged.
The reproduction made 973 jobs/1,050 document revisions in four seconds without settling.
Shared publication traversal now stops at the next computed output, crossing only aliases.
Authored invalidation remains transitive. Intrinsic/final failures notify the same frontier
so consumers retain accepted output and fail explicitly. Seventeen dependency, attachment,
stacking and lifecycle checks pass; the same full JSON example now finishes and saves with
four ready tissues, retained final-role anchoring and an automatic stack. No numerical solver
change was needed. The separate full suite before this fix passed **1,285 tests**; it does
not qualify the newer traversal change. Full gate initially found a missing standalone include
in the new quality query's clang-tidy check; fixed, isolated check passes, complete rerun pending.

Pouch investigation now distinguishes actual crossings from normal rotation: the original
curved fixture has 1,229 new transverse triangle-pair intersections, versus zero in rest.
The donor reproduces the invalid output. Two captured raw donor relaxation cases also
introduce crossings; numerical parity remains intact and is not geometry acceptance.
Added a reusable native same-connectivity quality query using the pinned BVH/intersection
kernel. Shared intrinsic publication rejects new crossings/collapses, retains accepted
geometry and reports an Issue. Large rotations remain allowed; no solver/default changes.
The API test covers failure retention and explicit recovery (0.08 thickness, 0.2 sagginess)
on that same curved source. Flat donor-default Pouch remains valid. Two older tests asserted
only pins/finite positions on crossing candidates; their valid cases now use fixed shell
boundaries and lower curve sagginess, alongside explicit invalid-output regression coverage.
32 focused checks, native build/CTest, changed clang-tidy, Ruff and mypy pass. Hidden GPU
rejection/recovery runs pass; inspected the recovered continuous shell, with its exact
backing retained. Full gate and remaining release qualification are pending.

Immutable tissue material preparation is now reused through the existing bounded native
resource cache (64 MiB/64 entries). Keys include accepted material state, side and intrinsic/
final role; eviction preserves job-owned leases. Session shutdown releases cache ownership.
Profiler reports attribute private preparation buffers and shared source meshes separately.
Three cache tests cover reuse, eviction, oversize bypass and observation shutdown; the
20-test cache/group/diagnostic/architecture selection passes. Native build/CTest, changed
clang-tidy, Ruff and configured mypy pass.

Serial counterbalanced cached/uncached/uncached/cached GPU workloads show preparation
calls falling from 60 to 6 and totals from 58.0–58.3 ms to 5.6–5.7 ms. Overall six-edit
means overlap: cached 624–638 ms/edit versus uncached 632–644, with within-run standard
deviations 73–90 ms. No end-to-end speedup is established. System busy fraction was
8.9–10.2%; other processes/thermal state were uncontrolled. Reports are under ignored
`build/022-tissue/profile/`. Observed unique native bytes peak at 8.42 MB cached versus
4.81 MB uncached; ownership categories overlap. Native solve remains dominant. These
measurements include hidden texture readback, not physical display or input latency.
Pouch qualification and complete release checks remain pending.

Support regions now use native material-face lookup and footprint lines on the displayed
revision. Draft selection/hover/cancel do not mutate documents; acceptance uses the shared
relationship operation with topology/part/side validation and one-action undo. Changed inputs
reject the draft. Viewport tool cancellation is coordinated across drawing, calibration,
measurement and support selection. Full-QML and hidden GPU checks pass; the Qt offscreen
harness needed explicit render-model staging before picking. The inspected GPU footprint
matches the selected covering faces. Native build/CTest/changed clang checks, Ruff/mypy and
eight focused region/architecture checks pass. Full regression: **1278 passed**, 732 existing
Qt deprecation warnings, 93.57 seconds. No interactive or release acceptance is claimed.

First runtime profiler workload (`build/022-tissue/profile/before-cache.afprofile.zip`)
records six stacking-parameter edits with hidden GPU frames. Native resolve dominates:
12 calls/3070 ms; planning 24/618 ms; material preparation 60/62 ms. Aggregate edit/wait/render
durations include synchronization and readback and are not display/input latency. Bounded
cross-job material reuse and its ownership attribution were subsequently implemented; they cannot be
presented as a fix for the dominant native solver cost. Pouch geometry and release checks
remain pending.

Tissue inflation controls now use existing native component picking and transform gestures;
side/part selection, cancellation and one-action undo preserve generated geometry's read-only
policy. Base/Rest fields have searchable creation/removal, native batched weight assignment,
topology-qualified selection and zero/partial/full viewport colors. Large weight arrays no
longer enter general inspector projections. Nine focused checks pass, including stale indices,
invalid weights, persistence and read-only vertex transforms. Full-QML field and branch-control
entry points pass; hidden GPU captures were inspected. These are background/offscreen checks,
not interactive desktop acceptance. Native build/CTest and Ruff/mypy pass. Remaining: support
region drafts/footprints, Pouch quality, cache/performance and complete release qualification.

Inflation preview is implemented through the existing read-only candidate/coordinator
contract: desktop/headless start/status/accept/cancel, dispatch capture, stale rejection,
separate native mesh ownership, save isolation and one-action acceptance/undo. GUI parameters
stay drafts until accepted; reset/profile initialization and inactive mode preservation are
tested. The candidate explicitly shows inflated rest before relaxation/crop/stacking.
Full-QML controls pass and their readable capture was inspected. Hidden GPU rendering shows
a separate green candidate; accepted picking remains unchanged and cancel removes staging.
The GPU harness first needed to stage the baseline before comparing picks; no production
picking change was required. Ten focused tests plus Ruff/mypy/function-length checks pass.
Full regression/gate, support-region viewport editing, Pouch visual
qualification, cache/performance and portable release remain pending. Do not merge/release.

Two-sided stacking now uses atomic final groups when whole-tissue order forms a strongly
connected component. Native evaluation follows actual side dependencies, retaining each
receiver's own settings; source/attachment prerequisites remain in the graph, so real
anatomical cycles still fail. The existing coordinator reserves selected outputs, captures
inputs at dispatch and publishes the complete group once. Manual members retain accepted
finals until explicitly evaluated. Changed candidate plans are observed before publication.
Native group parity covers fourteen donor fixtures and per-receiver settings/cancellation.
Application checks cover opposite sides, Manual, failure fallback, real cycles, round trips,
superseding a running group and undo/redo. Hidden GPU views above/below the envelope were
inspected; compatible sides retain continuous envelopes. Full regression: 1259 passing,
747 existing Qt warnings, with only the new inspection tool's 15-line check failing; that
tool was split cohesively and the architecture check now passes. Changed native clang-tidy,
build/CTest and Ruff/mypy pass. Remaining: editing tools, Pouch issue, performance/caches,
complete gate and release. No interactive acceptance or release completion claimed.

Full assembled surfaces now undergo native fold/self-intersection, bone and pairwise
crossing checks after stacking, including shell backing/rims and envelope composition.
Mixed muscle/normal-shell provider/receiver and geometrically relaxed receiver cases pass;
hidden GPU captures were inspected with retained backing and no visible tears or folds.
Picking matches displayed geometry; no visible test windows or interactive acceptance.
Automatic attachment search skips failed surfaces (including pending retries retaining a
failure); explicit references still fail. Independent construction remaps support-region
branch IDs in both owned and external intent. Full suite **1240 passed**, 747 existing Qt
warnings, 63.93 seconds; Ruff/mypy and changed-native build/CTest/clang checks pass.

Previously reproduced (now addressed by the group contract): two-sided tissues with excluded incompatible
cross-side pairs have valid acyclic native side dependencies but a cycle in the current
whole-tissue final graph. Joint native resolution succeeds; individual application jobs fail.
Probes: `build/022-tissue/probe_stack_sides*.py`.
Support-region drafts, remaining editing, Pouch visual qualification, performance and
release evidence remain incomplete. Do not merge/release.

Stacking is connected to shared phase jobs and desktop/headless entry points. A separate
plan output installs actual provider-final dependencies; candidate observations do not create
blanket prerequisite edges. Accepted Manual providers, exclusions, schema-4 intent, unchanged
final-resource reuse, native dependency edges, and current-intrinsic failure display are tested.
The coordinator now handles explicit obsolete-read-set publication conflicts through its
ordinary retry/cancellation contract. Fixed a real retry loop: pending state must retain a
previous failure until successful publication, rather than count as recovery. Empty crop and
disabled inflation sides preserve own output instead of entering the donor's nonempty-domain
ABI. The full suite before those last edge checks passed **1229 tests**, 747 existing Qt
deprecation warnings, 53.90 seconds. Focused edge checks pass; final style pass pending.
Full-QML searchable pair editing/exclusion/undo passes; inspected readable stacking inspector
capture (`build/022-tissue/stacking-inspector.png`). Offscreen UI evidence does not render 3D.
Still required: full-shell/envelope independent validation, mixed/relaxed stack shapes,
support-region viewport drafts, broad lifecycle/cycle qualification, cache/performance review,
the other remaining editing tools and final release qualification. Do not release/merge yet.

Accepted rest, intrinsic and final results now own immutable material provenance: geometry
references, parts/sides, fields, constraints, cropping and frame. Manual authored edits do
not reinterpret retained geometry. Schema-4 storage and resource reachability retain old
material inputs while newer phases run; Make Independent remaps stable branch identities.
Intrinsic construction uses its accepted rest settings. Full suite: **1223 passed**,
1122 Qt deprecation warnings, 45.24 seconds. Ruff/configured mypy/function limits pass.
This remains foundational work; coordinated production stacking is not yet enabled.

Native stacking now separates candidate/order planning from solving selected targets against
frozen accepted provider output. This avoids silently recalculating Manual providers. The
separated path matches all fourteen actual-addon fixtures; missing/failed accepted providers,
cancellation and provider output preservation are tested. Thirty-six focused checks pass;
native build/CTest, changed-native function checks, Ruff and configured mypy pass. Application
dependency integration remains incomplete. Candidate observations must not become blanket
prerequisites: that would create false cycles in valid tissue attachment chains.

Accepted surface results now retain structural material pins from bound Fiber points and
explicit point protection. Native capture maps authored parameters to exact material rows;
refinement preserves the coordinates, and stacking uses weighted equations without pinning
all contributing vertices. Branch/patch provenance, schema-4 ownership, Manual accepted
inputs, moved-Fiber shape preservation, undo and offscreen inspector controls are covered.
The inspected UI capture shows both protection controls. Full regression: **1200 passed**,
615 existing Qt deprecation warnings, 45.09 seconds. Ruff/configured mypy and changed-native
function checks pass. Offscreen evidence does not render the 3D viewport. Production
stacking scheduling, full-shell validation and release qualification remain incomplete.

Native tissue stacking preparation now retains full material variables and exact CSR
correspondence through crops, branches, envelopes and normal shells. Side extraction,
world-space directions, participating faces, exact region/boundary rows and complete
mesh assembly run in C++; shell backing remains unchanged. Canonical triangulation is
retained when connectivity matches. Forty-five focused material/kernel/architecture tests,
native build/CTest, changed-native function checks, Ruff and configured mypy pass.
Structural Fiber-to-material pin preparation was completed in the subsequent checkpoint;
full-shell independent validation and the coordinated application/desktop stacking workflow
are still pending. This checkpoint is
native integration evidence, not production stacking or release acceptance.

The synchronous vector stacking numerical adapter is now compiled against pinned unchanged
addon kernels and the maintained PIQP core. Fourteen actual-DLL reference cases match at
2e-7 with matching rejection status/messages, covering transport, chains, multiple providers,
exact equations, cropped hidden variables, regions, explicit/requested/excluded relationships
and bone-contact failure. Cache reuse and cancellation checks pass. Twenty focused native,
provenance and architecture checks pass; native adapter function-length checks pass. No donor
executor or competing pool is used. This is an incomplete native checkpoint: production
tissue-domain preparation and application/desktop integration remain required.

Target-relative region constraints now capture retained material bindings in native work,
resolve target-frame offsets without changing shared sources, and persist owned binding
batches in schema 4. Explicit bind/rebind/unlink use the shared commands and focused
Constraints inspector. Topology mismatches require explicit rebind; exact structural
backing rejects contradictory moved goals. Nine region workflow checks cover movement,
topology, compaction, undo, cancellation, persistence and profiler memory ownership.
Full-QML capture/unlink/undo passes offscreen; its platform does not render the viewport.

Review found and repaired a shared async history defect: late binding captures could be
installed in earlier parent poses. Historical input mismatches now preserve an unresolved
request and recapture on navigation. Anchor, Fiber and region captures use this boundary;
per-execution immutable resources prevent historical recovery from overwriting redo data.
Cross-parent-edit tests verify actual positions after undo/redo and subsequent movement.
The pre-history-fix regression passed 1147 tests; the complete post-fix development gate
passed **1151 tests**, 615 existing Qt warnings, native checks, typing and function limits.
Production stacking, broader editing and release qualification remain incomplete.

Routing now declares role-aware anatomy dependencies, including automatic tissue-final
obstacles, optional exclusions/manual membership, and source-consumer cycle exclusions.
Explicit cycles remain failures. Native routing still receives owned surface batches;
accepted empty crops contribute no collider while their dependency remains registered.
Advisory authored-Fiber collision checks report tissue roles, keep unrelated findings
when a role is unavailable, and expose that incomplete check separately. Desktop obstacle
lists include tissues through the existing searchable/virtualized choice model.
Six new workflow cases cover routing, revisions, exclusions, cycles, empty crop/restore
and unavailable-role isolation. Hidden GPU top-view capture was inspected: the path
goes around the radial tissue. This is offscreen evidence, not interactive acceptance.
Full suite now passes **1140 tests**, 615 existing Qt deprecation warnings, 49.64 seconds.
Ruff, configured mypy, architecture limits, native rebuild and CTest pass.

Fiber surface bindings now use explicit surface roles and owned material captures.
The dense field may retain multiple captures of one provider: fresh edited influences
use the current real surface while unedited structural pins keep their original capture.
Native pin adoption does not nearest-rebind retained anchors. Current-shape editing,
junction sharing, copying, resource reachability and schema-4 storage use this contract.
Tissue base/final selectors are available in Fiber creation and rebinding. Material
compaction, unchanged endpoints, mixed capture persistence, final-failure retention
and explicit base bindings pass three new workflow checks. Existing Fiber desktop
acceptance and the new full-QML tissue Fiber creation/propagation check pass offscreen.
Full suite: 1133 functional checks passed; its one failure was a 17-line test helper,
now split and verified with the architecture checks. Ruff, configured mypy and changed
native clang-tidy pass. The preceding complete development gate passed 1131 tests.
Production stacking, broader editing and release qualification remain incomplete.

Inspected addon production contracts and current standalone boundaries. The
registry, anatomical queries and attachment candidate paths still assume SCPs.
Numerical ports must include remaining Python mesh/field preparation, not just
the already-native solvers. Existing addon kernels, PIQP 0.6.4 and qualification
fixtures are migration references; Blender is not a runtime dependency.

Specification, migration inventory, implementation plan and active documentation
links are written. Typed Point/Anchor/Membrane/TissueVCP contracts, schema 4,
stage-result ownership and role-aware accepted surface providers are implemented.
All-Fiber surface creation now produces a Membrane. Point creation/editing and
independent Anchor capture/rebind use shared commands, native binding kernels,
the existing coordinator and undo history. Parent movement resolves retained
bindings; deletion protection and workspace association include Anchors.

Point/Anchor desktop creation, inspector, native picking and explicit rebind are
integrated. Membranes retain the existing Surface inspector and staged display.
Tissue phase revisions distinguish base/rest/intrinsic/final invalidation; topology
locks traverse construction consumers through Membranes to tissue attachments.

Native meshes now retain validated material grids and welded branch vertex identities;
deformation, finalization, memory accounting and project storage preserve them. This
supplies exact source correspondence for the upcoming tissue evaluators.

Ordinary loft inflation now uses pinned addon kernels for Distributed, control-point
falloffs and Section Profile directions. Nine addon-generated fixtures match at 1e-12.
Native accepted-grid refinement provides interior samples without source mutation.
Coordinated base/rest/intrinsic/final jobs, phase-aware publications, tissue creation
and inflation commands work for ordinary one-sided loft tissue with stacking disabled.
Five workflow/architecture checks pass, including source motion, base reuse, transform
rejection, deletion/undo and schema-4 stage round trips. Other intrinsic strategies
and stacking currently fail explicitly; they must be completed before release.
Desktop ordinary-loft tissue creation/selection and inspector are now connected.
Tissues appear in Anatomy, not Construction; generated transforms are disabled.
`tools/tissue_editor_acceptance.py` passes full-QML offscreen controls without warnings;
inspected `build/022-tissue/tissue-inspector.png` (offscreen platform has no 3D view).
`tools/tissue_scene_acceptance.py` separately renders the inflated tissue via hidden
GPU texture, with matching hover/click selection; inspected `tissue-gpu.png`.
No desktop windows or user input were used. These qualify only the current ordinary
loft increment, not the entire planned tissue UI or geometry workflow.
Desktop/cancellation checkpoint full suite: **988 passed**, 475 Qt warnings,
32.28 seconds. Active native Section Profile cancellation finishes within the two-second
test deadline; pinned source bytes are checked, and Manual tissue evaluation retains its
previous output until explicit evaluation. Formatting corrected after the gate's first pass.
Inflation/stage checkpoint full suite: **983 passed**, 335 Qt warnings, 31.25 seconds.
Configured mypy, ruff, formatting, three native CTests and changed-adapter clang-tidy
checks pass. No runtime release or full tissue qualification is implied.

Runtime integration remains incomplete: generalized Fiber roles, intrinsic numerical ports, stacking,
full GUI and release qualification are still required. No 0.2.2 release is claimed.
Accepted tissue bases now distinguish an Anchor frame, retained Fiber path and Membrane
mesh without synthetic point/curve meshes. Native outputs retain validated sparse material
correspondence, side/part labels and source faces across deformation, finalization,
memory accounting and schema-4 storage. Twenty base/workflow checks and seven material-map/
architecture checks pass; configured mypy, ruff, formatting and native build/CTest pass.
Radial, sweep and normal-shell kernels now run through shared tissue stages and the
capability-driven desktop inspector. Six addon shell/sweep fixtures match at absolute
1e-12, including cyclic/zero-taper sweeps and authoritative all-zero fields. Four
Blender 5.0.1 unit icospheres preserve radial subdivision thresholds and rounded seed
coordinates. Typed-base motion and round-trip tests pass.
`tools/tissue_shapes_acceptance.py` passes hidden GPU inspection for all three outputs
and twelve delete/recreate cycles; inspected captures under `build/022-tissue`.
It exposed and fixed stale tissue scene records after deletion, plus a reproducible
Qt heap failure when main/outline views shared a Qt geometry across deletion/recreation.
Per-scene Qt wrappers sharing the same native result pass that sequence. This adds a
second Qt/GPU geometry copy; measure it in release profiling. Qt supports shared resources
generally, so do not claim all sharing is unsupported or that an upstream bug is proven.
Full shape checkpoint: **1009 tests passed**, 599 Qt deprecation warnings, 34.34 seconds.
Configured mypy, ruff, function-length checks, native CTest and changed-adapter clang-tidy
checks pass. Full-QML offscreen tissue controls still pass.
Native relaxation checkpoint adds the pinned production Static PBD kernel and native
geometric radial/sweep/shell adapters, source-relative Fixed/Soft regions, feathering,
exact shell backing, custom fields and independent convergence diagnostics. Ten targeted
relaxation/architecture tests pass, plus three native CTests. This is an intermediate
checkpoint: donor relaxation fixtures, desktop controls, target-relative capture and
field topology protection are still pending. No full increment/release acceptance is claimed.
Generic solver adjacency now uses undirected polygon edges, matching the donor; strict
winding validation remains at normal-shell source construction. The donor sweep's cap
winding is preserved by current parity fixtures rather than silently rewritten.
Relaxation qualification adds seven actual addon cases plus separate exact-input static
comparisons: static kernels match at 1e-10 with double goals; geometric source constraints
match at 2e-7. Legacy mathutils precision differences remain recorded, bounded at 2e-5 m.
Fields now retain topology signatures and fail explicitly after incompatible resampling.
`tissue_relaxation_acceptance.py` exercises full-QML relaxation and region add/remove
through shared commands, and `tissue_relaxation_scene.py` renders a constrained static
envelope to a hidden GPU texture. Both pass without QML warnings. Inspected readable
`regions-inspector.png` and `static-envelope-gpu.png`; no visible windows or real desktop
input were used. The initial font-less offscreen capture was replaced after adding the
same explicit Segoe UI setup as the other desktop acceptance tools.
Target-relative constraints, field painting, complete part/side editors and all remaining
release requirements are still pending. Native changed-file clang-tidy passes.
Latest full suite: 1027 passed and one function-length failure in the new GPU acceptance
tool; that helper was shortened and both architecture checks then passed. Configured
mypy, Ruff and formatting pass. Do not report this as a completed release gate.
Multi-part native checkpoint: eight prepared branch fixtures match addon inflation,
shared displacement averaging and Hermite connectors to 1e-10, for both boundaries,
flips, control/distributed modes and nonzero fullness. Native material axes persist
across deformation and storage. Surface accepted kind/part IDs remain separate from
authored branch edits; tissue bases capture those IDs, including Manual prerequisites.
Native accepted-grid refinement now preserves welded branch correspondence and adds
interior samples without mutating sources. A two-root sparse branch otherwise has no
interior vertex to inflate; the integrated refinement addresses that ordinary case.
Seventeen focused branch/tissue/architecture checks pass, with native build/CTest and
configured mypy. New native branch adapters pass clang-tidy; newest envelope/refinement
files still need that check. Envelope composition is integrated but donor composition
fixtures and complete part/side desktop controls are next. No full increment acceptance.
Part/side checkpoint: sixteen additional actual-addon envelope composition fixtures
pass at 1e-10 with exact connectivity, including disabled sides and branched connectors.
First profile initialization respects the amount in the same operation; profile/control
reset and connector commands share validation and transactions. Full-QML offscreen
checks exercise actual part/side selectors, mode changes and resets without warnings.
Hidden GPU captures inspect branched envelopes and a zero side; the visible source
membrane coincides with zero-height output, so source-overlay separation still needs
release interaction review. These captures do not establish general anatomical quality.
Full regression: **1058 passed**, 599 existing Qt deprecation warnings, 39.35 seconds.
Configured mypy and Ruff pass; native envelope/refinement/parameters clang-tidy passes.
Height smoothing, cropping, target-relative constraints, tissue-role Fiber integration,
full stacking, complete editing, ownership review and release qualification remain pending.
Height smoothing checkpoint: pinned PIQP 0.6.4 and unchanged addon numerical core;
batched adapter smooths full independent material sides before envelope composition.
Seventeen actual-donor cases match within 1e-10. Twenty-two focused native/workflow tests
pass, including exact zero/boundary pins, Off bypass, cancellation, undo and persistence.
Settings reuse accepted source paths; per-part/side diagnostics remain distinct from static
relaxation. Full offscreen UI mode/diagnostic checks pass; inspected readable smoothing
inspector capture. Cancellation is checked around synchronous per-part QPs, not within
factorization. Full gate, performance and portable qualification still pending.
Unrelated untracked root `__init__.py` is preserved.

## Verification

Retained Anchor bindings now own their bind-time mesh resource. The shared provider
adapter evaluates only referenced material locations on current tissue output, preserving
offsets and frame orientation across envelope compaction. Native canonical polygon
correspondence avoids treating a changed A/B quad diagonal as lost material. Coincident
envelope sides retain their implicit shared location; radial/sweep outputs retain canonical
angular/profile identities rather than their coarser source-point map. Cropped-away
locations fail explicitly without nearest recapture. Resolution returns a job-owned draft
mesh used only by attachment evaluation, never rendering/picking. Resource reachability
and schema-4 saves include bind-time references. Nine new native/workflow checks plus
Anchor regressions and architecture total 17 passing tests; full-QML final-role selection,
capture and update pass. Changed-native clang-tidy, Ruff and configured mypy pass.
Fiber dense fields and target-relative regions still need this contract integrated.

Tissue Make Independent now uses an owned construction-graph copier: one clone per source,
copied internal junctions, remapped branch identities/accepted layouts and retained explicit
external support targets. Anchor/Fiber/Membrane sources, branch settings, Manual accepted
layouts, source isolation, external parent motion, undo/redo and schema-4 round trips pass
five new workflow tests. Full-QML Make Independent and one-action undo pass. Existing
primitive/surface entry points remain supported. The related historical Surface publication
path now retains the accepted layout belonging to its retained geometry rather than the
new authored layout. Configured mypy, Ruff and function-length checks pass.

Preset creation now applies the actual donor settings for Closed Bulk/Rim/Layer/Pouch,
with source-capability filtering in desktop and API. Classification is an editable label;
changing it preserves all settings. The Layer soft backing default remains recorded while
the structural backing stays exact. Captured donor defaults and seven workflow checks pass;
full-QML Layer/Pouch creation and hidden-GPU rendering execute successfully.
**Visual qualification is not complete:** the Pouch preset on the curved horizontal
membrane fixture produces two large lobes and a collapsed middle. The addon's current
native solver reproduces the result exactly (0 maximum coordinate difference), including
canonical and donor-fan triangulation. It reports ITERATION_LIMIT, not convergence.
Rest geometry is smooth before relaxation. An experiment eliminating near-coincident
refinement stations did not repair the shape and was reverted; do not claim refinement
as the cause. Diagnostic inputs/captures are in ignored `build/022-tissue/pouch-probe*`.
Further geometry qualification and handling of unusable warned results remain required.

Complete suite after crop/smoothing: **1110 passed**, 599 existing Qt deprecation warnings,
40.37 seconds. Preset changes have focused checks but not a subsequent full gate yet.

Material-domain crop is now native and exposed through `tissue.crop` and the focused
inspector. Twenty actual addon fixtures cover ordinary/profile/branched, oblique,
empty and two-sided results at 1e-10. Envelope sides must be clipped before composition;
clipping an already composed envelope changed canonical B-side diagonals and was rejected.
Crop preserves source correspondence and nonzero cut-edge height. Plane changes reuse
accepted rest geometry; incoming attachments lock crop topology. Empty accepted output
has an explicit prepared state, persists safely, renders no chunks and is not an available
attachment surface. Thirty focused crop/workflow/architecture checks, changed-native
clang-tidy, Ruff and configured mypy pass. Full regression pending for this increment.
Full-QML crop controls and hidden GPU crop/empty/restore checks pass. Visual inspection
initially found obsolete outlines in the test: the manual render loop did not deliver
Qt DeferredDelete events. Servicing those events fixes the test evidence; production
rendering was not changed. Mask-count assertions now cover removal/replacement.
The cropped capture was inspected with its independent source Membrane still visible.
No interactive desktop acceptance or release qualification is claimed.

Baseline `uv run --no-sync pytest -q`: **941 passed**, 307 existing Qt deprecation
warnings, 31.89 seconds on Windows. `git diff --check` passed for documentation.
Baseline main matched origin/main before branching.
Foundation full suite: **951 passed**, 307 existing warnings, 30.18 seconds.
Next full suite after attached-point operations/output dispatch: **957 passed**,
307 existing warnings, 34.41 seconds. Point/Anchor lifecycle checks
exercise capture, parent motion, explicit rebind, undo/redo, deletion protection
and persistence. Shared provider and output dispatch changes still require the
next complete regression run. `tools/point_editor_acceptance.py` passes full-QML
creation, explicit rebind and undo without warnings. Its offscreen platform does
not render the 3D viewport; inspected UI capture at `build/022-points/anchor-inspector.png`.
Separately `tools/point_scene_acceptance.py` passes GPU texture-only rendering and
native picking with no visible window; inspected `build/022-points/point-gpu.png`.
Full tissue geometry parity and release acceptance remain pending.
Point/UI foundation full suite: **964 passed**. Material correspondence full suite:
**969 passed**, 335 Qt deprecation warnings, 31.24 seconds. Native build and three CTest
contracts pass; changed native adapters pass the native function-length check. An
over-broad explicit mypy invocation included intentionally untyped desktop modules;
the repository gate uses its configured scopes instead.
Required: development gate, geometry parity, lifecycle, headless, offscreen UI,
profiler and portable acceptance, followed by ownership/coupling review.

## Next actions

No implementation work remains in this plan. Hands-on testing may produce follow-up
reports; use the existing F12 feedback workflow. Schema 4 deliberately rejects older files.

## Recovery inputs

Standalone checkout: `E:/development/anthroforge`. Addon reference:
`C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
Use the existing Windows/cloud setup guides. Original anatomy and source .blend
fixtures remain external; commit compact extracts and provenance only. Validation
must stay background/offscreen, without desktop input or visible test windows.
