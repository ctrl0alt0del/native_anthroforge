# Sternocleidomastoid distortion after Ribs Top Radius

- Task branch: `codex/scm-ribs-distortion`
- Integration branch: `main`
- Starting revision: `4ff1ef8`
- Status: propagation-only smoothing comparison complete; production unchanged
- Last updated: 2026-10-25, Europe/Bucharest
- Active writer: local Codex

## Outcome

Reproduce the reported zigzag/stretching of `Sternocleidomastoid.L continuous belly`
after Ribs Top Radius becomes 3. Distinguish propagation/correspondence defects from
intrinsic inflation/stacking limitations before proposing changes. Preserve source WIP
projects and existing attachments. Do not change attachment/algorithm behavior before
explaining the observed cause and proposed approach to the user.

## Inputs and next steps

Baseline assembly: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
Use read-only package adoption, existing profiler, stage inspection and hidden GPU captures.
Trace bindings -> paths -> surface -> rest -> intrinsic -> final, comparing full propagation
with explicit reevaluation and stage-isolated evaluation. No production changes yet.
Evidence belongs under `build/scm-ribs-distortion/`. No desktop takeover or source-file save.
Preserve unrelated root `__init__.py` and unfinished 0.3.4 branch.


## Observed evidence

Exact tissue ID `fc8df927-2290-4af2-b8e9-882697a8733e`, membrane
`b4e00a6c-5071-4e9e-b2b8-00446a2562fa`; three POLYLINE Fibers, each 73 samples.
Ribs edit reproduces distortion at paths/base, before SECTION_PROFILE inflation.
Stacking is disabled; relaxation NONE. Base maximum edge grows .297 -> 1.992.
Explicit reevaluation produces byte-identical geometry at all four tissue stages.
Authored points, captured owners/weights/bindings and bind path are unchanged.
Middle Fiber: samples 66–71 follow Ribs at weight 1, sample 72 is hard-pinned Spine.
Neighboring Ribs frames alternate strongly; retained offsets around .73–.76 amplify
rotation differences. Automatic support mapping and short terminal blend are implicated.
Existing native weights match addon `core/vcp/fiber_node_attachment_weights.py`.
Historical matching-addon capture `shortcut_update_parity_20261023/blender/SHORTCUT_4`
already has a 2.003 maximum adjacent middle-Fiber gap (app current 1.992), versus .171
baseline. This is existing captured evidence, not a newly executed Blender test.
No production code/attachment behavior changed. Diagnostic ablations/visual inspection next.


## Confirmed scope terminology and causal experiments

User clarification: propagation means the parent-driven Fiber deformation, distinct
from Bezier/Polyline/ROUTED engines, not task/dependency scheduling. This is the owning
layer of the reproduced defect. `curve_evaluation.resolve_fiber` resolves the saved
attachment field; `engine_path` uses that path directly for authored engines and passes
resolved input to routing. No engine switch or tissue repair is implicated here.

Middle-Fiber experiments use unchanged weights and native `af_attachment_blend_frames`:

| Diagnostic | Largest edge | Largest nonterminal edge | Terminal edge |
| --- | ---: | ---: | ---: |
| Production | 1.991823 | .544229 | 1.991823 |
| Hold automatic Ribs support offset orientation fixed | 1.620306 | .346210 | 1.620306 |
| Hold automatic Ribs support motion fixed | .171409 | .171409 | .056324 |

Holding Ribs support motion fixed restores baseline middle-Fiber geometry; this is a
causal ablation, **not a proposed production fix or permission to discard support**.
Holding only offset orientation fixed reduces sawtooth but leaves the endpoint cliff.
Ribs surface motion and rotating off-surface offsets both matter. The final Spine pin
must stay fixed; its neighboring automatic Ribs samples currently carry weight 1.
The inherited C2 owner-transition rule limits width by adjacent owner-run extents; a
singleton hard-pin run can collapse its effective sampled blend to the last edge.

Inspected `fiber-comparison.png` and `base-comparison.png`: the before-inflation base
already exhibits the user's zigzag; the historical matching addon middle Fiber has
the same end stretch. No runtime settings, source project or attachment references
were changed. Exact reevaluation hashes agree at every tissue stage; no failed jobs.

## Continuation

The repair/design belongs to parent-driven Fiber deformation: coherent nearby-sample
support motion and adequate transitions into hard pins, preserving explicit anatomical
bindings. Rotation-only correction is demonstrably insufficient. A replacement must be
tested on this failure plus normal edits, actual surfaces and attachments; no new approach
has yet been qualified. Discuss the approach before changing attachment behavior.
Background evidence/probe scripts: `build/scm-ribs-distortion/`; original WIP source
remains intact. Full application gate/rebuild not needed for this investigation-only edit.


## Research follow-up: candidate replacements, not qualified fixes

The current local formula has smoothstep transitions but does not ensure a coherent
whole-curve deformation. Singleton endpoint-owner runs can leave no interior sample
in the transition. Facet-dependent rotated offsets remain discontinuous even with
smooth owner weights. Neutral-pose reconstruction conceals this until supports deform.

Primary published references inspected:
- Jacobson et al., [Bounded Biharmonic Weights (2011)](https://homes.cs.washington.edu/~jovan/papers/jacobson-2011-bbw.pdf):
  bounded smooth bind-time weights; pose-time blending. A curve/arc-length adaptation
  is a hypothesis, not the published 2D/3D method unchanged. Automatic supports require
  fidelity terms/handle regions: endpoint-only constraints on this middle Fiber would
  otherwise favor Spine everywhere and erase Ribs support. Better weights alone do
  not repair point-dependent target-frame motion.
- Sumner et al., [Embedded Deformation (2007)](https://cgl.ethz.ch/~sumnerb/research/embdef/Sumner2007EDF.pdf):
  neighboring transformation consistency in a deformation graph, with near-rigid local
  maps and positional constraints. Relevant to facet/frame coherence and different
  consumer representations. Nonlinear; costs, stretch allowance and initialization
  require testing on our actual parent edits. No injectivity/contact guarantee implied.
- Sorkine/Alexa, [ARAP (2007)](https://igl.ethz.ch/projects/ARAP/), and
  [Laplacian Surface Editing (2004)](https://diglib.eg.org/items/ee43c2c6-4956-4ff0-9db1-c946306a5b99):
  joint detail-preserving reconstruction under constraints. Curves need an appropriate
  graph/bending/rest-frame adaptation, not a blind call to triangle-mesh ARAP. Plain
  displacement fairing is not automatically rigid-motion invariant. Existing tissue
  height smoothing/PBD are different downstream stages, not this missing contract.

Evidence-driven experiments to compare: (A) arc-length-aware bounded support weights
plus coherent regional parent transport, (B) constrained curve/connected-construction
reconstruction driven by soft automatic-support goals and exact anatomical pins.
Preserve neutral/rest shape, rigid motions, pin references and authored corners; test
SCM, ordinary small edits, large rotations/nonuniform scaling, junctions, loops, sample
resolution independence and consumer surfaces. Record native profiling and failure
behavior. No candidate has been implemented or demonstrated to fix the actual case yet.


## Authorized non-production comparison experiment

User requested current vs improved vs ROUTED shape/timing on SCM at Ribs Top Radius 3,
before any production change. Experimental sources live under
`tools/experiments/scm_propagation/`; standalone native DLL builds only under
`build/scm-ribs-distortion/native`. It is not linked, imported or registered by the app.

Prototype: cached arc-length kernel weights (width .2 of rest length), eight regional
affine maps per support, each fit from 64 fixed bind-topology vertices with a fixed-size
3x3 fit; exact anatomical-pin corrections. No iterative path/global solver. Parent
canonical vertex/triangle correspondence is checked before using this experiment.
Neutral-shape error is below 5e-15. All four current consumer stages reproduce the saved
production results exactly, confirming the comparison pipeline. Existing stages build
the experimental membrane/inflation/crop without implementation changes.

First fixed-camera plots show greatly reduced sawtooth but a remaining lower bulge.
Direct ROUTED (73 retained controls) fails: structural routing point intersects another
surface. Separate endpoint-only ROUTED succeeds; this intentionally changes constraints
and is not an equivalent engine conversion or a ground-truth anatomy claim. The reference
retains accepted endpoint bindings and uses persisted material stations for consumer
correspondence. Results under `build/scm-ribs-distortion/comparison/`.

Initial profiled serial/counterbalanced medians for all three Fiber paths: current
6.47 ms, prototype 3.53 ms, endpoint-only ROUTED 10.59 s. These are preliminary: native
instrumentation boundaries differ, so unrecorded timing and full consumer timing must
be collected before drawing performance conclusions. First native/experimental Python
build and function-size checks pass. Remaining: rigid-motion/pin checks, quality metrics,
unrecorded timing, final visual comparison, source preservation and honest recommendation.


## Completed comparison — final evidence

Review: `build/scm-ribs-distortion/comparison/review.html` (self-contained images and
method/timing notes). Matching-camera base/final/context plots and path projections
were inspected. Final prototype uses cubic B-spline interpolation of regional affine
maps; the first linear interpolation showed visible joins, so this experimental-only
refinement makes the transform field C2. No runtime application/library integration.

Final unrecorded measurement includes dynamic parent-vertex packing and unchanged
consumer stages. Six serial trials cover every ordering permutation; a separate
12-trial unrecorded run from prepared data agrees with the ordering. Background load
was uncontrolled. SCM-only, after parent geometry is available; excludes other anatomy,
scheduling, file IO and viewport publication.

| Method | Three Fiber paths, median | Paths + membrane + tissue, median | Total min–max |
| --- | ---: | ---: | ---: |
| Current | 4.289 ms | 21.000 ms | 18.263–23.501 ms |
| Experimental | 3.713 ms | 16.016 ms | 13.046–18.333 ms |
| Endpoint-only ROUTED reference | 10,704.927 ms | 10,725.197 ms | 10,496.381–10,963.805 ms |

ROUTED uses CUSTOM, 153 eligible surfaces, 73 requested samples and original path warm
start. All outputs have 73 samples in this case. This is deliberately two anatomical
pins per Fiber, not equivalent to direct conversion with all 73 authored constraints.
Direct conversion fails on an intersecting interior structural point; its failed time
is not a performance reference. Persisted material correspondence is explicitly mapped
for the endpoint-only diagnostic; the retained crop consequently has different spatial
extent after its different path shape. Inspect uncropped base and paths too.

Actual results:
- Middle-Fiber largest sample gap: 1.991823 -> .171409; total length 9.553 -> 4.513
  (baseline 3.742). The third Fiber still has a broad lower bulge.
- Anatomical pin residuals are exactly zero. Neutral and global-rigid sample/control
  position errors stay below 7e-15. This is not qualification of all path frames/scales.
- Automatic Ribs support is retained; peak middle-Fiber Ribs weight is .627 and its
  arc-length integral .309, versus original 1.0/.521. Support was not simply frozen.
- Advisory transverse self-crossing pairs: base 222 -> 28, final 245 -> 39. No collapsed
  faces. Endpoint-only ROUTED has 27 base crossings and zero after the retained crop.
  Touching/coplanar contact and containment are outside that diagnostic.
- Native path checking reports the original Spine first-segment contact; fresh baseline
  checks also report segment 0 for all three Fibers. It is not introduced by this trial.
- Fresh capture directly from the archived source reproduces all eight before/after
  tissue meshes exactly, including connectivity. Current isolated consumer stages also
  match the saved production stages exactly. Original source SHA256 remains
  `308c216c85d9458d83e163bc3ed2ab85338bccd3adeb496981ffe35ec8275dac`.

Evidence: `packed-summary.json`, `packed-timings.json`, `invariants.json`, `audit.json`,
`support-audit.json`, `geometry-findings.json`, `production-equivalence.json`,
`fresh-reproduction.json`, `manifest.json`, `prototype-v2.afprofile.zip` in the comparison
folder. Earlier profiled timings are attribution evidence only, superseded for speed
claims by unrecorded runs. Cold prototype cache creation from prepared inputs totals
about 25 ms including DLL load; source import and anatomical capture are not included.

Verification: standalone C++ build, configured clang-tidy function-size check, experimental
Python Ruff/format and both architecture tests pass. Embedded report images/values, JS
syntax and HTML data keys checked. No application rebuild/version/dist change was made;
production src/native/build definitions remain byte-unchanged from main. A full runtime
regression gate was not rerun for this isolated experiment. Unrelated __init__.py and
unfinished 0.3.4 work remain untouched. Tool reproduction instructions are in
`tools/experiments/scm_propagation/README.md`.

Conclusion: the cheap approximation is substantially cleaner and remains inexpensive
for this case, but remaining bulge/crossings and untested wider cases prevent claiming
a complete replacement. No production algorithm change is authorized by this experiment.
Next action: user reviews the concrete visual comparison before any production design.

## Follow-up: low-step routing and the rejected constraints

User proposed a small routing pass before/after cheap propagation. Production remains
unchanged. `hybrid_probe.py` uses the existing native route inspection boundary; no
optimizer or collision-query loop was introduced in Python.

The previous batch-level ROUTED failure description was incomplete. Testing all three
Fibers separately with all 73 controls gives: first fails, middle succeeds, third fails.
The failed traces have zero optimization attempts/trials: rejection is in `corridors`
before SQP, not failure to converge. Every authored control is a fixed routing constraint;
only the two endpoints are actual anatomical bindings.

`pin_probe.py` batches native advisory checks using 1e-7-long segments at the controls
(not a signed penetration-depth measurement). On the first/third Fibers, zero-based
point 1 intersects Spine; it is unbound. Endpoint 0 also has Spine contact, but has the
appropriate binding. Middle has no control-point hits. Retaining endpoints plus point 1
reproduces the structural-point rejection, including with Spine as the only obstacle.
This localizes the offending interior constraint without disabling production checks.

Endpoint-bound hybrids seeded with either current or improved propagation were tested
at 1 and 4 accepted steps. Every seed failed native warm-start validation and fell back
to replanning (`warm=false`). All completed, with final traced endpoints exactly equal
to their input goals. One-step totals for the three paths were 9.64/9.78 seconds;
four-step totals 10.54/10.05 seconds, respectively. Summed SQP-reported elapsed time was
about 78-110 ms. These are diagnostic, trace-enabled single passes, with uncontrolled
background load; they are not a controlled speed benchmark. The major cost lies outside
the short iterative solve, in validation/planning/preparation. Reducing accepted steps
does not impose a wall-time limit on those stages (nor on rejected trials).

Interpretation: a hybrid remains a justified experiment, but calling unchanged ROUTED
with a low step count does not currently exploit the cheap seed. Interior guide points
must be movable rather than accidental hard constraints; genuine anatomical bindings
must remain fixed. A useful refinement requires a cheaply obtained admissible seed or
a separately designed collision-recovery contract. Do not silently grant anatomical
owner exemptions to the interior controls. Also compare coherent surface shape, not
only individual collision-free paths, before claiming improvement.

Evidence under comparison: `hybrid-probe.json`, `pin-probe.json`. Captures retain bounded
native trace records and report truncation; wall timings include diagnostic overhead.
Ruff/format and explicit 15-line function checks cover both new experiment scripts.

Baseline follow-up (`baseline-route-probe.json`): the first-interior-point Spine contact
and the first/third direct ROUTED rejections also exist before the radius edit. They are
not evidence of a new bone penetration caused specifically by setting radius to 3.

A control experiment seeded from the already solved endpoint-only paths accepted the
middle warm start but still rejected the first/third (`valid-seed-probe.json`). Therefore
do not describe every rejected warm start as proof that the supplied accepted route was
invalid: `routing_warm.cpp::remapped` resamples each span by arc length before validation.
That may cut corners/change contact spacing. This is an observed warm-start inconsistency
with a source-backed hypothesis, not yet a demonstrated resampling defect. Investigate
that handoff and near-endpoint Spine contact before choosing collision recovery behavior.
No exemption expansion or production change was made.

## Active follow-up — current endpoint preference and low-step hybrids

User requests repeating the small-step experiment after the endpoint-default conversion
fix. Main through `1dd7bf3` is merged into this experiment branch; no experiment is promoted
into production. Reuse the isolated native C2 trial and unchanged native ROUTED backend.
The earlier `hybrid_probe.py` already manually selected anatomical endpoints, despite
the later conversation conflating that experiment with the all-control conversion.
Repeat using the current shared conversion command, explicitly verifying two controls,
retained bindings and warm-start status. Test 1/4 accepted steps after current/C2
propagation. Also test routing at the baseline before capturing a new propagation field;
this before variant necessarily recaptures support influences for the changed baseline.
Compare full uncropped base/rest as well as cropped final shape, stage findings, input
pins and measured work. Source projects and production code remain unchanged.

User correction: the hybrid must not invoke a planner. Normal ROUTED calls were stopped;
their automatic fallback is not a valid measurement of the requested local refinement.

Completed solver-only experiment: `solver_only.cpp` is a separate DLL which includes the
unchanged production `routing_solve.cpp` stage, with owned copies of the same 153 surface
inputs and matching owner/collider IDs, scales, tolerances, reference objective and frames.
It feeds the exact 73 propagated samples directly into SQP, with two endpoint pins. No
planner, pre-validation rejection or warm-path resampling runs. Rejected outputs are
diagnostic candidates only; none were published to the application. The captured runtime
profile contains zero production route/planner entrypoint calls. Straight-path parity
against production ROUTED covers all 11 sample channels to 8.44e-15.

Results at Ribs Top Radius 3 (uncropped transverse-crossing pairs, not collision certificates):

| Candidate | Base | Inflated rest | Cropped final | Native path-clearance passes |
| --- | ---: | ---: | ---: | --- |
| Current propagation | 222 | 245 | 245 | No post-update solver |
| Experimental C2 propagation | 28 | 39 | 39 | No post-update solver |
| C2 then 1 direct SQP step | 27 | 8 | 8 | 2/3 |
| C2 then 4 direct SQP steps | 0 | 47 | 21 | 2/3 |
| C2 then 24 direct SQP steps | 0 | 0 | 0 | 2/3 |
| 1 baseline SQP step, recapture, then C2 deformation | 19 | 45 | 45 | Baseline 3/3; no post-update solve |
| 4 baseline SQP steps, recapture, then C2 deformation | 9 | 58 | 58 | Baseline 3/3; no post-update solve |

Both original-current-seed after variants were also tested; they retain 227/241 inflated
crossing pairs at 1/4 steps. The quality of the propagated seed matters. Endpoints remain
exact for every candidate; no degenerate triangles or truncated finding lists were found.
The third path misses the SQP clearance check: maximum violation about .00147/.00135 at
1/4 steps and .000845 at 24. This is separate from tissue-surface self-crossings. More
steps do not monotonically improve the loft/inflation because the path objective does
not optimize the assembled tissue surface.

Two serial unrecorded passes in forward/reverse order, from prepared inputs: C2 alone
2.17 ms paths /12.82 ms with tissue; after-C2 +1 step 34.64 ms solver /48.66 ms solver and
tissue; +4 steps 40.82/54.68 ms; +24 steps 74.00/87.69 ms. After measurements begin with
the already propagated seed: add the C2 path preparation cost when composing an update.
These are descriptive local measurements, not controlled frame
or input latency benchmarks. They exclude scene capture: the two 153-surface scenes cost
485 ms (edited pose) and 450 ms (baseline). Changed geometry requires the corresponding
scene. Before variants also pay baseline routing and roughly .2-.3 s recapture once, plus
the fitted cache; recapturing changes support weights, and amortization across edits is
not assumed. Shape after deformation did not improve over C2 alone in these before cases.

Evidence: `build/scm-solver-only/review.html` (stage-switchable images), `quality.json`,
`summary.json`, `timings.json`, `setup.json`, `scene-preparation.json`, `qualification.json`,
and `hybrid.afprofile.zip`. Actual base/rest/final candidates were inspected in two matched
cameras. The images mark rejected candidates explicitly. Touching/coplanar contact and
containment are outside the transverse crossing check.

Validation: isolated DLL build and configured clang-tidy pass; experiment Ruff/format and
both architecture checks pass. The initial adapter frame conversion differed from ROUTED;
it was corrected to use the production Z/Y initialization and native frame construction
before the final timings/shapes were generated. No production source changes, app rebuild,
version change or merge of this experimental branch into main. Remaining work is a product
decision about further refinement/clearance investigation, not an approved production fix.

## Active investigation — smoother cheap propagation

The user requests improving the propagation itself, independently of ROUTED. Compare
the existing C2 regional prototype with wider support blending and a cached linear
differential reconstruction. The latter retains locally transformed rest curvature,
soft propagated goals and exact anatomical pins. It is not a collision solver and has
no planner or iterative optimization. Research basis: Laplacian surface editing and
smooth skinning weights; this curve adaptation is an experiment, not claimed paper parity.
Production, source projects and package versions remain unchanged. Validate neutral and
rigid transformations, endpoints, complete uncropped tissue, bone contacts, and timing.
Evidence is under `build/scm-smoothing/`; code remains on the experiment branch.

### Observed result and method

The existing C2 prototype guarantees smooth interpolation of its weights/maps, not a
bound on curvature or relative motion of adjacent fibers. Widening support interpolation
from .20 to .35 of rest arc length lowers inflated crossings but increases base crossings.
It does not adequately address the remaining broad bend and fold.

The more promising experiment adds one curve reconstruction to the regional transport.
For rest samples p, propagated goals y and local affine maps A, minimize
`||q-y||_M^2 + ell^4 ||D2 q - A D2 p||_M^2`, with exact anatomical pins eliminated.
M is rest arc-length quadrature; D2 uses nonuniform stations normalized to 0..1. The
small positive-definite system is factorized at bind time and solved directly for XYZ.
There is no planner, nonlinear iteration, contact scene or collision penalty. This is a
curve-specific differential-coordinate experiment inspired by
[Laplacian Surface Editing](https://graphics.stanford.edu/courses/cs468-07-winter/Papers/sgp2004_laplace.pdf),
not a reproduction of that paper's rotation-invariant mesh editor. The role of smooth
weights is also discussed in the [skinning course](https://www.skinning.org/automatic-methods-compressed.pdf).

The first neutral test failed because the initial adapter collapsed dormant Polyline
handles onto their knots. Corrected before final runs: transport those offsets with the
original regional field and add the reconstructed knot displacement. Neutral/global
rigid errors over samples and stored controls/handles are below 7.8e-11; pin error is zero.

| Method | Path ms, 3 fibers | Consumer ms | Base crossings | Uncropped inflated | Cropped final |
| --- | ---: | ---: | ---: | ---: | ---: |
| Production | 3.87 | 13.45 | 222 | 245 | 245 |
| Earlier C2 regional prototype | 2.02 | 11.24 | 28 | 39 | 39 |
| Wider weights (.35) | 1.92 | 10.28 | 40 | 21 | 21 |
| Reconstruction ell=.05 | 2.16 | 10.49 | 22 | 18 | 18 |
| Reconstruction ell=.10 | 2.49 | 10.41 | 10 | 13 | 13 |
| Reconstruction ell=.20 | 2.40 | 10.29 | 0 | 0 | 0 |
| Wider weights and ell=.10 | 2.51 | 10.52 | 5 | 16 | 16 |

Fourteen serial balanced-order unrecorded trials after warm-up, prepared parent inputs.
Times include native transport, direct reconstruction, path adoption and separately
measured full isolated consumer stages. Exclude parent packing, project loading, bind
capture, unrelated anatomy, scheduling and viewport. Background load is uncontrolled;
these are descriptive fixture timings, not whole-app responsiveness evidence. Typical
cached setup is about 5 ms for three curves; first reconstruction DLL load was about
30 ms. Profile `smoothing.afprofile.zip` covers path boundaries separately from timing.

Actual base/rest/final shapes inspected from two fixed cameras, plus bone-context views
and individual path plots. No truncated diagnostics or degenerate triangles. Crossings
are transverse triangle pairs, not touching/coplanar/containment certification. Strong
reconstruction reduces the third path length from 7.05 to 4.92 (C2 comparison), removes
its lower bulge and makes the three paths more coherent in this case. No anatomical
acceptance claim follows from that reduction.

All-segment native checks against the same 153 surfaces, with zero requested clearance
and no endpoint exemptions, found the original Spine contacts: segments [0,1], [0],
[0,1] before the edit. Production/C2 keep those contacts. ell=.20 has [0,1], [0], [0].
No new intersecting segments were found. This does not satisfy the stricter .002-clearance
ROUTED contract and does not repair the remaining baseline near-endpoint contact.

Freezing only automatic Ribs support geometry is a diagnostic ablation, not a candidate.
The third path's mean Ribs-induced displacement is .6393 for C2 and .4934 for ell=.20;
peak response falls 2.0601 to .7197. Ribs influence remains, with the sharp response
spread/reduced by curvature regularization. This is a shape-preservation tradeoff.

### Ownership and remaining limits

If selected, reconstruction belongs in the existing native attachment-field evaluator,
with bind-owned rest operators/factorization and per-update resolved support goals. It
must not become a second scheduler, recapture bindings during evaluation, or repair
inflation after the fact. The experimental dense 73-point system is banded; a production
implementation should retain that compact structure. Every fiber remains independently
evaluated here; no membrane-wide solve or new sharing is introduced.

This does not qualify loops, interior pins, junctions, arbitrary authored corners,
different sampling, topology changes, shared consumers or wider anatomical fixtures.
The .20 scale is a tested candidate, not an approved default. Obstacle avoidance and
valid inflated surfaces remain unguaranteed for arbitrary edits.

Validation: separate native build and clang-tidy, experiment Ruff/format, both architecture
tests, exact source hash, production diff and report-link checks. Production algorithms,
projects, versions and distribution remain unchanged. No full runtime gate or packaged
GUI acceptance is claimed. `review.html` provides stage switching and all raw evidence.
