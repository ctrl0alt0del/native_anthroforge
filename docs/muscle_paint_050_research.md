# Muscle Paint 0.5.0 — method research and applicability

**Status: research, not implementation or algorithm qualification.** Checked 2026-10-29.
The [confirmed specification](specification_050.md) owns product behavior. This document
compares inspected code and primary sources, then proposes experiments. No new numerical,
visual or timing experiments were run for this research. Published results on other
inputs do not establish success on AnthroForge anatomy.

## 1. Finding and research direction

The most directly reusable starting point is the **addon's native smooth-base fitter**,
combined with its separate sparse Fiber-selection idea. It already fits longitudinal
curves jointly against the ruled-strip surface that the native loft actually produces.
This is a closer output match than reconstructing an arbitrary mesh and hoping to recover
editable Fibers afterward. This is a reason to test it first, not a claim that it already
solves painting.

Section 4 researches fourteen method/integration questions end to end: capture and coverage,
background rejection, gap shape and controls, merging, perimeter topology, flow/charts,
sparse fitting, attachments, true branches, periodic loops, accuracy, execution and undo.
It gives concrete candidate formulations and rejected alternatives for each. In particular,
the existing native seam correction, closed-map rejection and document-only undo behavior
identify real integration work. These questions are no longer merely an unresearched list;
their proposed solutions still require implementation experiments and qualification.

Do not conflate three meanings of “surface”: the temporary painted target, the fitted
curve construction, and the final evaluated Membrane. Compare the last against the first.
Increasing mesh tessellation alone cannot repair a deficient Fiber layout.

## 2. Existing capability inventory

Standalone inspection baseline: `d03db662df92b4730148c665c013db3a0b48bea1` (0.4.3).
Addon checkout HEAD: `fae36aba1b208676cf21d7c4a78a20d5b1f68c66`, with local changes;
the inspected smooth-base documentation is modified. Paths in the addon tables are
relative to the addon root recorded in the task note; hashes below identify key inputs.
These are code/document observations, not freshly rerun acceptance results.

### Addon sparse layout planner

| Evidence | Existing behavior and reuse limits |
| --- | --- |
| `core/authoring/fiber_layout.py`, `layout_chart.py`, `layout_patch.py` | A directed disk patch with four ordered boundary landmarks becomes a grid of candidate longitudinal paths. This already expresses an area as candidate loft rows; it does not discover a painted sheet, anatomical heads, loops or branch roots. |
| `core/authoring/layout_reduction.py` | Evaluate the sampled positional error of bands between fixed candidate rows. A shortest path through admissible bands minimizes Fiber count for that fixed candidate set, with control-count tie breaking. No globally minimal arbitrary-layout or continuous error guarantee. |
| `app/authoring/fiber_plans.py`, `base_planning.py`; `docs/authoring_muscle_reconstruction.md` | Existing `anatomy.plan_fibers` / `anatomy.plan_base_fibers` orchestration includes native routing and rechecks solved geometry. That routing workflow must not become an implicit step of Muscle Paint. |
| `tests/unit/test_authoring_fiber_layout.py` | Existing tests describe sparse counts, tolerances, invalid inputs and budgets. They are useful starting fixtures, not evidence for 0.5.0 branches or direction accuracy. |

The raw planner defaults to 17 candidates and 65 samples per Fiber. These are historical
defaults, **not proposed 0.5.0 values**. Band checks use vertices, triangle centroids and
candidate samples with arc-length correspondence. Numerical selection/parameterization
and repeated queries include Python/NumPy; reuse requires native implementation under
the current guidelines. Dense samples must never silently become hard routing constraints.

### Addon joint smooth-base fitter

| Evidence | Existing behavior and reuse limits |
| --- | --- |
| `docs/smooth_native_base.md`; `app/authoring/smooth_bases.py`, `smooth_inputs.py` | Caller supplies shape, directed patches, Fiber counts, qualified endpoint neighborhoods and explicit shared sides. The tool does not choose all these from strokes. |
| `core/authoring/smooth_native.py`; `native/fiber_ccd/af_base_spline.hpp`, `af_base_order.hpp` | Native constrained spline fit combines sample fidelity and fairness, hard endpoints, shared-boundary equality and soft tangent regularization. Inputs are normalized in the current Python adapter. Sampled ordering constraints can fail explicitly; there is no global topology guarantee. |
| `core/authoring/smooth_chart.py`, `smooth_holdout.py`; native base headers | Directed disk charts and independent sampled holdouts provide starting correspondence and validation. Explicit material stations avoid relying on independently normalized arc length for each final curve. |
| `adapters/authoring/smooth_quality.py`, `smooth_publication.py`, `smooth_domains.py` | Evaluate actual native output and publish coordinated Free Fibers/surfaces. Blender-specific publication and some Python/BVH validation must be replaced by standalone services/native queries. |
| `tests/unit/test_smooth_base_native.py`, `test_smooth_holdout.py`; `tests/blender/test_authoring_smooth_base.py` | Existing native-fit/holdout/publication fixtures can seed parity experiments. They have not been rerun in this task. |

Current input limits include 1–8 patches, 2–8 Fibers per patch, 4–8 longitudinal spline
controls and up to 40,000 fit samples. A whole shared longitudinal side is one Fiber
identity used by two coordinated surfaces. **That is not the app's partial-root branched
loft.** Closed and nested branches are not supplied by this mechanism.

The kernel uses a custom dense linear solve plus bounded ordering work; it is not already
a PIQP-based fit. Do not presume another solver is faster without measuring preparation,
solve, validation and publication at these problem sizes. Its regularization produces
positional seams with soft tangent agreement, not guaranteed smooth transverse derivatives.
The inspected Python adapter also computes centering/scale, weights, coordinates and array
assembly. A future port must move numerical preparation into C++ as well as the solve;
“the solver is native” does not establish compliance of the complete new computation.

Addon documentation records that smoothing can reintroduce bone penetration. That remains
a relevant failure class to visualize, but the confirmed Muscle Paint policy permits
penetration with an Issue. Do not copy stricter addon publication gates wholesale. The
addon's publication of uninflated muscles and its Preview/Publish API also do not define
the new user workflow: 0.5.0 explicitly generates only Fibers/Membrane in one action.

### Standalone boundaries already available

| Existing source | Reuse / concrete difference required |
| --- | --- |
| [Native drawing](../native/src/drawing.cpp), [curve fitting](../native/src/curve_fit.cpp) | Surface projection, fallback depth, owned stroke samples and Blender-derived cubic fitting exist. Muscle Paint additionally needs physical-width coverage over a sheet and the agreed depth-threshold semantics. |
| [Weight-stroke coverage](../native/src/painting_stroke.cpp), [visibility projection](../native/src/painting_projection.cpp) | Native occlusion and brush-related infrastructure exist. Current weights are applied to an existing target through projected screen-space coverage. This is not a world-width membrane-construction brush; copying the policy unchanged would violate zoom independence. |
| [Loft](../native/src/surface_loft.cpp), [sampling](../native/src/surface_sampling.cpp), [branches](../native/src/surface_branches.cpp), [core branch policy](../src/anthroforge/core/surface_branches.py) | Existing evaluator and explicit junction constraints define the target representation and final validation. Keep its material correspondence rather than fitting against a substitute surface. |
| [Patch fairing](../native/src/surface_patch_fairing.cpp) | Boundary-fixed four-pass Laplacian fairing exists for closed patches. It does not establish a direction-preserving fit, supported gap model or accuracy bound. |
| [Surface queries](../native/src/surface_query.cpp), [closure](../native/src/surface_query_closure.cpp), [snapping](../native/src/surface_snap.cpp) | Reuse current visible/confirmed exterior placement and qualified retained bindings. Paint footprint membership is not itself an anatomical binding. |

No Muscle Paint workflow or addon smooth-base adapter was found in the inspected standalone
source. Existing weight painting is a different feature. Dependencies already include
Eigen/libigl snapshots, PIQP and CGAL 6.1.1; available headers do not mean every relevant
method is already integrated or qualified. See [notices](../licenses/THIRD_PARTY.md).

## 3. Published methods worth investigating

### SurfaceBrush — adjacent 3D strokes and temporary sheet reconstruction

Rosales, Rodriguez and Sheffer, SIGGRAPH 2019. Inputs are 3D ribbon strokes with positions,
normals and widths. Constrained matching connects locally coherent stroke sequences into
partial surfaces, then joins borders. The project provides papers and example inputs/results;
no implementation download was listed on the inspected page.
[Project](https://www.cs.ubc.ca/labs/imager/tr/2019/SurfaceBrush/),
[paper](https://www.cs.ubc.ca/labs/imager/tr/2019/SurfaceBrush/doc/SurfaceBrush_AuthorVersion_small.pdf).

**Application hypothesis:** its adjacency criteria may help distinguish same-sheet overlap
from nearby crossing sheets. Our inputs also carry SCP identities, contacts and deliberate
branches, which should reduce ambiguity. Its mesh output is not an editable Fiber loft and
its topology-completion rules must not override user intent. Test merge decisions on thin
bones and overlapping layers before considering broader reconstruction reuse. No interactive
performance claim or source-code license is established here.

### StrokeStrip — corresponding stations along overdrawn strokes

Pagurek van Mossel et al., SIGGRAPH 2021. It parameterizes already grouped 2D strokes,
aligning tangents and longitudinal stations while enforcing monotonicity. Orientation is
resolved separately so oppositely drawn strokes can describe one strip. It then fits the
aggregate curve. [Author explanation](https://www.davepagurek.com/programming/strokestrip/).

**Application hypothesis:** adapt the correspondence idea within a known local painted
sheet, especially for differently sampled or reverse-direction strokes. It does not itself
solve our 3D support/gap interpretation, grouping, branch topology or multi-Fiber output.
The paper explicitly discusses ambiguity and local minima; convergence is not proof of the
intended strip. [Paper](https://www.davepagurek.com/content/images/2021/05/cluster_param.pdf).

The C++ implementation is MIT, but requires separately licensed **Gurobi**; bundled third-party
code needs its own review. It is a research reference, not a drop-in dependency. PIQP cannot
replace discrete orientation decisions or the entire iterative parameterization simply by
renaming the solver. [Repository](https://github.com/davepagurek/StrokeStrip).

### StripMaker — learned grouping, a secondary reference

Liu et al., SIGGRAPH 2023. Local and contextual learned classifiers group overdrawn vector
strokes; source/data are linked. **Different work from StrokeStrip.** Our application already
has physical support, layer and explicit branch evidence. First compare deterministic
grouping using that evidence; a learned 2D grouping system would add training/domain-transfer
questions without demonstrated need. Keep its perceptual cues as a reference; do not select
a model or training dataset now.
[Primary project](https://www.cs.ubc.ca/labs/imager/tr/2023/stripmaker/).

### SecondSkin — sketch depth over underlying geometry

De Paoli and Singh, SIGGRAPH 2015. Classifies strokes by their relation to underlying
geometry and reconstructs 3D curves/surfaces. Its shell projection interpolates endpoint
heights; missing projection can use a view-plane construction. The paper reports failures
under occlusion, foreshortening and ambiguous views.
[Project](https://www.dgp.toronto.edu/~depaolic/projects/secondSkin/),
[paper](https://www.dgp.toronto.edu/~depaolic/projects/secondSkin/SecondSkin.pdf).

**Application hypothesis:** use it to compare supported-contact/gap transitions, not adopt
its curve classifier or automatic volume creation. Our explicit gap-depth controls and
background-depth threshold remain authoritative. A camera-dependent planar fallback can
look correct in one view and be wrong in another; require multi-angle evidence.

### Harmonic charts, tangent transport and line fields

[libigl's tutorial](https://libigl.github.io/tutorial/) documents harmonic parameterization,
fixed/equality-constrained quadratic solves and biharmonic displacement fields. These can
support initial charts and gap-depth experiments using existing dependencies. A harmonic
chart alone does not encode painted fiber direction; blindly smoothing positions can erase
the intended shape. A displacement formulation can preserve an unchanged reference at zero
control motion, but still requires constraints and shape tests.

[Geometry Central direction fields](https://geometry-central.net/surface/algorithms/direction_fields/)
explicitly distinguish 2-direction line fields from 4-direction cross fields. **Our inference:**
fiber alignment is axial, so a line field is the natural starting representation; a cross
field would also equate a 90-degree crossing that users want to keep distinct. Its smoothest
field APIs are not already a stroke-constrained Muscle Paint implementation. Singularities
and conflicting constraints must remain visible, not averaged into arbitrary branch choices.

[Vector heat](https://geometry-central.net/surface/algorithms/vector_heat_method/) supplies
tangent transport on an existing surface and reusable precomputation. Consider it only if
local chart/transport experiments fail on curved supports. It cannot infer the missing gap
surface. Geometry Central is C++/MIT, but would add a dependency; it is not currently selected.
[Source and license](https://github.com/nmwsharp/geometry-central).

### Constrained fitting and independent geometric checks

[PIQP](https://predict-epfl.github.io/piqp/) supports convex quadratic objectives with linear
equalities/inequalities through native C++ interfaces. With fixed correspondence/basis,
sample least squares and fairness plus endpoint/seam constraints can form such a problem.
This is an experiment against the addon kernel, not a reason to replace a working small
dense solve. Nonlinear direction, ordering, free correspondence and topology decisions are
not automatically convex or solved by PIQP.

[CGAL 6.1.1 distance APIs](https://doc.cgal.org/6.1.1/Polygon_mesh_processing/group__PMP__distance__grp.html)
include bounded-error directed/symmetric Hausdorff estimates and distance-threshold queries.
These are stronger candidates than checking only source vertices. Their bound concerns the
supplied triangle meshes, not unknown intent between paint samples or exact spline geometry.
Use a separate error allowance for constructing/tessellating the paint target and final
curves. CGAL is already pinned, but this API's build, cancellation and cost need qualification.
Distance alone cannot verify flow or material correspondence.

### Generic NURBS fitting — useful comparator, weaker output match

[PCL's trimmed B-spline tutorial](https://pointclouds.org/documentation/tutorials/bspline_fitting.html)
starts with PCA initialization assuming a roughly planar cloud, then refines a surface and
fits its trim boundary. It is a useful reference for adaptive fitting, but ignores stroke
flow/attachments and its surface is not our ruled Fiber loft. Converting afterward adds
another approximation. Do not add PCL merely to reproduce a capability closer to the
existing native fitter; consider it only if a specific failed fixture justifies comparison.

## 4. Research coverage and concrete approaches

The following covers **every unresolved method family** in the initial review, not only
the easiest open-patch fit. “Recommended” identifies the best-supported approach to take
into design/prototyping; it does not claim a production implementation or measured success.
Local code establishes integration requirements. Literature establishes available methods
and their conditions. Neither substitutes for the anatomical experiments in section 5.

| ID | Question researched | Recommended direction | Important limit/change identified |
| --- | --- | --- | --- |
| R1 | Physical brush capture and multi-view placement | World-space ribbon samples, visible native surface queries and immutable stroke provenance | Existing projected weight painting has different width semantics. |
| R2 | Background-depth rejection | Compare hits against a locally predicted painting layer, with spatial resampling and supported-region continuity | Previous-event depth differences are event-rate dependent; grazing views need explicit uncertainty. |
| R3 | Unsupported gap shape | Contact-constrained view-ray depth interpolation, then optional constrained displacement fairing | A generic hole fill cannot recover the drawn interior course. |
| R4 | Stable gap normal and wheel control | Surface-derivative normals; support-oriented transported frames; a fixed gesture reference | Frenet frames fail at straight/inflection regions; a collapsed sheet has no defined normal. |
| R5 | Stroke merging without joining wrong sheets | Support-aware adjacency with axial directions, correspondence and explicit Keep Separate | Neither proximity nor pairwise transitive closure is sufficient. |
| R6 | Perimeter editing and valid topology | Coverage union/difference in explicit sheet charts; preserve holes and connected-component evidence | Polygon operations do not decide which 3D sheets should merge. |
| R7 | Flow, charts and integrability | Constrained 2-RoSy/power field per part, followed by a checked material chart | Smooth directions need not be integrable; branches must not share one averaged field. |
| R8 | Approximation and automatic Fiber count | Joint ruled-loft fitting plus adaptive across/along refinement | Fixed-row shortest-path optimality does not survive unrestricted joint refitting. |
| R9 | Multi-SCP attachment strips | Ordered strip candidates, batched qualified exterior capture, hard fit pins | No unconstrained nearest-surface snapping after fitting. |
| R10 | True branch roots and seams | Explicit partial-boundary constraints and fitting/validation through native assembly | Native seam correction can change a separately fitted child patch. |
| R11 | Closed loops and persistent alignment | Cyclic spline/Bezier construction with a periodic material-coordinate seam | Explicit closed material correspondence is currently rejected at both application/native boundaries. |
| R12 | Shape, flow and coverage accuracy | Independent geometric bounds plus material/footprint and tangent tests | Coincident surfaces can have completely wrong Fiber direction. |
| R13 | Native execution, memory and cancellation | Sparse/batched local solves, staged accuracy checks, existing coordinator/leases | No timings or defensible interactive budgets yet; some library calls have no cancellation interface. |
| R14 | Paint-only undo, discard and result lifetime | Extend existing history entries with transient state participation | Current History commits only changed Documents; a no-document-change stroke would disappear from undo. |

### R1. Capture physical paint, not a screen-space mask

**Existing evidence:** `drawing.cpp` owns projected stroke samples and surface fallback;
`painting_projection.cpp` does native occlusion testing. `painting_stroke.cpp` applies a
projected radius to vertices of an existing mesh. That latter policy cannot directly satisfy
physical-width construction painting. SurfaceBrush's explicit ribbon samples are the closer
input representation, without requiring its reconstruction algorithm.

**Recommended construction:** capture world positions, an along-stroke parameter, physical
width, support identity/material hit, local frame, view ray and supported/unsupported status.
Keep these immutable after the stroke. Resample by physical travel and geometric error,
including width changes, rather than mouse event count. Store original stroke identity so
grouping never destroys undo information. Use a local support/tangent frame to turn physical
width into visible footprint rays, then evaluate contacts across that width through native
queries. Adaptive footprint subdivision should increase samples near silhouettes/depth jumps.

Compare this with an intrinsic geodesic brush on the support. Geodesic distance is a published
and implemented option, including prefactorable heat-method solvers, but it follows a surface
around corners and cannot cross empty gaps by itself.
[Heat method](https://www.cs.cmu.edu/~kmcrane/Projects/HeatMethod/index.html).
For this contract, use visibility-gated ribbon coverage first; a geodesic disk is a comparator,
not permission to paint hidden bone backs. Physical width and visible projection must be
defined separately at grazing angles. Existing captured samples remain stable across views;
only new input uses the new camera.

### R2. Depth threshold and painting-layer continuation

**Rejected formulation, by inspection:** accepting each new hit if it is within threshold
of the previous pointer event makes a long drop acceptable when divided into enough events.
It also lets one valid brush-center hit conceal background hits at the edges.

**Recommended formulation:** predict the current sheet's depth at each footprint ray from
nearby accepted same-layer support, using a local tangent/low-order continuation expressed
in physical coordinates. Measure the candidate's excess depth along the normalized view
direction against this prediction. Compare to the user threshold. Use a fixed physical
neighborhood for fitting/updating the predictor, not “last K mouse events.” Crossing a
support edge without a compatible continuation enters gap state; a rejected background hit
must not become the next prediction's anchor.

SecondSkin supplies a relevant precedent for using known contacts and view-depth
interpolation; it does not supply this exact rejection policy. The proposed support-aware
predictor is our adaptation, not a published guarantee. Continuous curved supports need
progressive local updates; a frozen first-hit plane would wrongly reject them. Geometry
cannot always determine whether a deep visible bone is intentional. The already-approved
threshold override supplies intent in those cases. At a grazing tangent, ray-plane
prediction is ill-conditioned: retain supported neighborhood information and mark uncertain
gap placement rather than divide by a near-zero denominator or attach to the farthest hit.

Research outcome: there is a concrete spatial continuation model to test, and an analytic
reason to reject the simple event-to-event test. Numerical neighborhood/default-threshold
values still require scale, zoom, silhouette and input-rate sweeps; literature cannot
justify choosing them from unrelated datasets.

### R3. Gap reconstruction: preserve the drawn course

Compare three established families:

| Candidate | Useful property | Why it is insufficient alone |
| --- | --- | --- |
| Linear/Hermite interpolation of view depth between contacts | Keeps the stroke's projected course and fixed ends; Hermite can encode reliable endpoint slopes | Poor contact derivatives can overshoot; width still needs a sheet model. |
| Coons/transfinite patch from four boundary curves | Reproduces compatible boundaries without an iterative global solve | Interior directional strokes are not constraints; skew boundaries can yield folded/poor interiors. |
| Biharmonic displacement with fixed support and handle constraints | Smoothly spreads a depth edit over a provisional sheet | Requires an initial sheet; smoothing alone does not preserve footprint/flow or guarantee no intersections. |

Open CASCADE provides a concrete boundary-fill API for two to four B-spline curves; Eigen
provides spline interpolation with derivative constraints. These demonstrate available
building blocks, not a reason to add either complete CAD stack or interpolate all hand noise.
[Boundary filling](https://dev.opencascade.org/doc/refman/html/class_geom_fill___b_spline_curves.html),
[derivative interpolation](https://libeigen.gitlab.io/eigen/docs-nightly/unsupported/structEigen_1_1SplineFitting.html).

**Recommendation:** construct a baseline from the stroke's view rays and end-contact
depths, using reliable end slopes only where supported. Interpolate the width-side contacts
and preserve captured interior stroke evidence. Apply a displacement-based correction if
needed, constrained at supported ends and measured against the captured course. Coons is a
comparison for simple four-boundary gaps; it must not replace the input with a generic cap.

For perspective rays `o(s)+lambda(s)d(s)`, interpolate a depth coordinate and reconstruct
`lambda` consistently using that ray and the camera forward axis; raw ray length and view
depth are not interchangeable. For several views, already captured world samples constrain
the sheet—do not reproject the entire painting from the last camera. A missing far contact
stays unfinished under the product contract, rather than selecting an arbitrary background
surface. Penetration is reported, not repaired or silently routed away.

### R4. Normal definition and an inexpensive depth handle

The provisional sheet provides a normal from its across/along derivatives. Orient it
consistently with neighboring supported surface samples. For continuing a width frame
through a gap, use parallel transport/minimum-twist frames seeded from valid support.
The app already has such transport in [curve frames](../native/src/curve_frames.cpp);
do not replace its production behavior merely to add a paint control.

Wang et al.'s double-reflection rotation-minimizing-frame method is a relevant alternative
if the existing transport produces a demonstrated defect. It avoids the zero-curvature
failure of Frenet frames, but still needs a regular curve and initial frame.
[Paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/12/Computation-of-rotation-minimizing-frames.pdf).

**Proposed handle calculation:** freeze the baseline sheet and oriented normal field at
gesture start. For normalized gap length `s`, a cheap displacement basis is
`b(s)=16*s^2*(1-s)^2`; apply `h*b(s)*n(u,s)` across the span width. It is zero with zero
first derivative at both supported ends and equals one at the middle. This is an analytic
candidate for the agreed whole-span control, not a new production smoothing algorithm.
For irregular support boundaries, solve a constrained scalar displacement field once and
scale it by wheel depth. Compare that against the polynomial basis before choosing.

Recompute from the gesture baseline plus total wheel displacement, not by repeatedly
moving an already moved mesh; this avoids accumulation and makes reversing the wheel
reversible. Normal orientation persists through that gesture, so the handle cannot flip
sign mid-drag. A zero-width/collapsed patch has no valid normal; report it as unavailable.
If later displacement folds the sheet, show a diagnostic rather than silently changing
depth or adding a repair. Keep one undo action for the complete hold/scroll interaction.

### R5. Merge similar strokes without merging unrelated layers

SurfaceBrush and StrokeStrip provide complementary ideas: 3D adjacency evidence versus
common longitudinal stations. Neither justifies grouping by screen overlap or by a distance
threshold alone. Use an explicit adjacency graph of stroke spans with evidence for:
same sheet/support continuity, overlapping world-width coverage, transported axial tangent
agreement, compatible longitudinal correspondence, and user Keep Separate constraints.

**Recommendation:** resolve grouping before global surface fitting. Preserve original
stroke records and a separate group assignment. Compare directions after local transport;
`abs(dot(t1,t2))` recognizes reverse drawing but must not erase an actual 90-degree crossing.
Do not use only connected components of pairwise “similar” edges: A similar to B and B
similar to C does not establish that the whole group has a coherent direction or layer.
Recheck each proposed group against its correspondence and source constraints. Ambiguous
overlapping groups stay distinct or request the already-approved explicit branch choice.

Do not globally flatten all strokes onto a plane. Local charts can reduce a compatible
group to the domain where StrokeStrip-like station alignment applies, while preserving
support/layer labels. SurfaceBrush-like matching can provide cross-stroke candidate links
in 3D. StripMaker's learned grouping remains a secondary comparator: no current evidence
justifies training a model to infer information we already capture explicitly.

### R6. Perimeter coverage, connectivity and representable topology

After sheet/group assignment, store directional strokes and coverage separately. Apply
Perimeter additions/removals as union/difference in the part's material chart, keeping
operations in stroke order for undo. CGAL's regularized polygon sets represent unions,
differences, holes and multiple components; boundary-only contact is distinct from overlap.
This is a native candidate using an already pinned dependency.
[CGAL polygon sets](https://doc.cgal.org/6.1.1/Boolean_set_operations_2/index.html).

**Recommendation:** use chart-domain polygon operations for authoritative boundaries, with
adaptive triangulation only for display/fitting. A raster mask is a useful display cache,
but its resolution must not decide whether a narrow connection exists. Reject an accidental
point-width bridge as a degenerate fit rather than letting pixels invent a valid loft.
The chart must already be valid; a planar Boolean cannot determine 3D layer relationships.

Classify each region by connected components, boundary loops, orientation and explicit
branch incidences. A disk-like part can use an open chart; an explicitly closed band needs
periodic treatment. A generic erased interior hole is not automatically the user's closed
Fiber loop. Match the coverage against the permitted construction graph and report a
nonrepresentable case instead of filling holes or generating extra objects. Keep Separate
does not waive the confirmed prohibition on disconnected generated construction.

### R7. Direction fields are not sufficient: construct a usable chart

The appropriate local direction representation is a **2-RoSy line field**, because sign
reversal is equivalent while a 90-degree rotation is not. Directional's power-field method
uses complex `q=exp(2i*theta)` values and a connection-aware quadratic smoothing energy,
with hard/soft data constraints. It also separates field design, curl reduction and
integration, including nontrivial topology. This supplies concrete algorithms beyond
“smooth the arrows.”
[Directional tutorial](https://avaxman.github.io/Directional/tutorial/),
[field survey](https://www.graphics.rwth-aachen.de/publication/03315/).

**Recommendation:** work per existing main/branch part, constrain the field from directional
paint and leave perimeter edits out of that data term. Keep local transport in the energy.
Inspect small field magnitudes, singularities and incompatible data rather than normalizing
a zero vector. A branching point is a construction seam, not permission to average its main
and child directions into one misleading field. Do not use unconstrained curvature alignment:
painted anatomical flow is authoritative even when it differs from principal curvature.

Then obtain ordered material coordinates. Compare a directed positive-weight chart with
a stroke-aligned least-squares integration, enforcing fixed attachment boundaries, positive
orientation and monotonic longitudinal stations. Floater/Tutte fixed-convex-boundary maps
offer mathematical injectivity under their stated mesh/weight conditions; cotangent,
LSCM and ARAP alternatives do not universally provide that guarantee.
[CGAL parameterization](https://doc.cgal.org/6.1.1/Surface_mesh_parameterization/index.html).
This guarantees a suitable chart only under those conditions, not fidelity to our flow.

A direction field may have curl or singularities that prevent one ordered family of
noncrossing Fibers from following it everywhere. Use chart Jacobians, field/chart alignment
and boundary correspondence to detect this. Compare the shortest-path/geodesic transport
idea from vector heat only where curvature makes local transport inadequate; it does not
automatically produce an integrable field with the intended constraints.
[Vector heat method](https://www.cs.cmu.edu/~kmcrane/Projects/VectorHeatMethod/index.html).
Do not introduce global integer quad-remeshing merely to get a patch layout: its automatic
singularities and topology are not our editable branch contract.

### R8. Fit the actual loft, then adapt the right resolution

Use the addon fitter as the baseline formulation, but measure the standalone evaluator.
For fixed correspondence, piecewise-linear across weights and cubic longitudinal curves
give a sparse linear map from control coefficients to sampled surface positions. Hard
endpoints, exact shared positions and fixed periodic seam constraints are linear. A
quadratic data/fairness objective fits the existing native linear-algebra/PIQP boundaries.

Directional fitting can initially penalize the component of `S_v` perpendicular to the
prescribed tangent, with a nonzero forward-derivative constraint after orientation is fixed.
That objective does not itself guarantee a maximum angle. Exact normalized angular and
Euclidean-distance inequalities are not ordinary linear QP constraints. Do not advertise
PIQP as solving the entire nonlinear correspondence/topology problem. Independently verify
direction and shape, refine, and fail visibly if the requested tolerances remain unmet.

**Adaptive strategy:** retain boundary rows, attachment changes and branch roots first.
Use fixed-candidate band tests/shortest path to propose sparse interior Fibers; fit jointly;
locate worst residuals; add an across row for transverse error or longitudinal knots for
along-curve error. Refine evaluation tessellation only for evaluation error. Repeat with
bounded work and cancellation, never implicit tolerance relaxation. Knot insertion preserves
the existing spline before the next fit; it is preferable to refitting an arbitrary new
sample cloud. Open CASCADE documents spline-to-Bezier decomposition as a standard operation;
the result can target existing Bezier Fibers without a new public engine.
[Bezier decomposition](https://dev.opencascade.org/doc/refman/html/class_geom_convert___b_spline_curve_to_bezier_curve.html).

The old fixed-candidate optimum is not global optimality of this adaptive procedure. Along
and across controls interact, and there can be local minima when correspondence changes.
Record each refinement's error reduction and do not repeat stalled refinements indefinitely.
Use native dense solves for small baselines and compare sparse/PIQP as size grows; no solver
replacement or speedup is established before actual profiling.

There is a further solver-specific finding: `af_base_order.hpp::ordered_solve` adds the
currently violated halfspace as a permanent **equality**, then resolves, for at most 64
steps. It does not release an earlier active constraint. This is a bounded feasibility
heuristic, not a general convex-QP active-set method. As an illustrative mathematical
counterexample, minimizing `x^2+y^2` with `x>=1` and `0.1*(x+y)>=0.3` starts by locking
`x=1` under an unnormalized largest-violation rule; adding the second equality gives
`(1,2)`, while `(1.5,1.5)` satisfies both inequalities with lower objective. This is an
analysis of the rule, not a newly reproduced anatomical failure.

For fixed linear ordering constraints, a proper inequality QP is therefore a justified
comparison on **correctness**, in addition to speed. The existing PIQP integration can
solve that formulated class without permanently converting all encountered inequalities
to equalities. Compare objective, residuals, feasibility and final shapes against the
legacy heuristic; do not change an existing production fitter during this research.

### R9. Endpoint strips and anatomical bindings

Represent each attachment strip as an ordered parameterized region with support identities,
not an unconstrained collection of nearest vertices. Sample candidate Fiber endpoints along
that strip while preserving the association between across parameter and support. One strip
can contain multiple bone intervals. At an interval transition, refine or retain a boundary
row so a sparse layout cannot silently skip a small support region.

**Recommendation:** use current confirmed exterior capture in a batched preparation stage,
restricted to the chosen strip/support evidence. Feed the resulting qualified positions as
hard fit pins. If exterior qualification changes a proposed location, show it and check the
result against spatial tolerance; do not fit first and then snap endpoints arbitrarily.
Missing support blocks, while a Fiber passing through a bone still produces the agreed
advisory finding. Child branch roots use shared junctions; they do not acquire redundant
SCP bindings. Closed bands use their selected starting/binding cross-section.

This extends placement orchestration, not retained-binding deformation. After generation,
store ordinary binding records and verify current propagation/rebinding behavior. Reuse
common material stations across fitted rows so downstream surfaces and tissues do not
interpret different arc-length fractions as the same anatomical section.

### R10. True branches: fit through the existing seam operator

**New local evidence:** [native branch inputs](../native/src/surface_branch_inputs.cpp)
require at least two ordered distinct interior roots on an outer main curve. Branch rows
must start exactly at these shared points. Root intervals cannot overlap or share endpoints;
all paths must be open. [Native assembly](../native/src/surface_branches.cpp) merges seam
stations and applies a longitudinally fading correction to interpolated child rows before
welding. Therefore two independently good patch fits can produce a bad assembled branch.

**Recommended model:** a separate directed chart for the main and each child, with the
child's start boundary mapped to one explicit interval of the main's outer boundary.
Distribute child roots monotonically over that interval. Insert exact Bezier knots at root
locations using existing [de Casteljau subdivision](../native/src/curve_queries.cpp), assign
junction identities, and constrain each child start to its corresponding main position.
Never represent a whole shared edge between parallel patches as equivalent to this branch.

With topology and sampling stations fixed, the native correction
`(1-smoothstep(t))*(main_seam - interpolated_child_start)` is linear in evaluated positions.
It can be included in a fitting operator, or the existing native assembly can be evaluated
after each candidate and its residual fed back. The former is the more direct research
candidate; parity with the current assembly is mandatory. Station changes require rebuilding
that operator. Do not modify the native branch algorithm silently to make the fit pass.

Use exact C0 shared positions. Tangent-plane fairness may be a soft fit preference, but
forcing main and child **fiber directions** to match would defeat the painted branch flow.
Automatic quad meshing, such as Sketch Retopo, is useful background on patch layouts but
produces a different construction and cannot replace our junction model.
[Sketch Retopo](https://kenshi84.github.io/sketch-retopo/sketch-retopo-siggraph2013.pdf).
Check the final assembled footprint/angles, particularly near the correction zone.

### R11. Closed loops: geometry closure and material closure are different

Periodic B-splines provide smooth cyclic curves; cyclic piecewise Bezier permits intentional
corners. Simply duplicating an open curve's endpoint does not establish smooth periodicity
or common cross-row correspondence. Standard CAD APIs distinguish closed/periodic curves,
periodic origin and knot multiplicity.
[Periodic spline contract](https://dev.opencascade.org/doc/refman/html/class_geom___b_spline_curve.html).

**Recommendation:** use an annular material domain, cut computationally at the selected
binding cross-section. Represent the seam with paired coordinates and one period; do not
duplicate the authored endpoint or turn the seam into a physical edge. Fit smooth portions
with cyclic basis/continuity conditions, retaining intended corners within tolerance. Convert
to ordinary closed Bezier Fibers and preserve source direction and phase. A loop need not be
forced C2-smooth if that would erase an intentional closure feature.

**Actual integration gap:** [application correspondence](../src/anthroforge/application/surface_correspondence.py)
and [native correspondence](../native/src/surface_correspondence.cpp) explicitly reject
closed paths. [Closed alignment](../native/src/surface_alignment.cpp) saves starting phase
and reversal; [sampling](../native/src/surface_sampling.cpp) otherwise computes arc-length
stations. Thus existing closed loft support is not equivalent to retained periodic material
coordinates. Equal sample counts cannot remove this difference.

The preferred design candidate extends the shared correspondence contract to cyclic
monotone maps with an explicit period and retained seam identity, while leaving current
default arc-length consumers unchanged. It requires API, core, persistence and native
validation together. An alternative is fitting while constrained to the current arc-length
correspondence; compare it, but do not claim it preserves arbitrary painted cross-sections.
This proposed extension needs implementation design and tests, not a hidden paint-only map.
No schema decision or existing evaluator change is made by this research.

Closed bands also require consistent orientation. A twisted/nonorientable strip cannot be
given a consistent attachment normal merely by choosing a different starting point. Report
that incompatible construction rather than silently cutting it open or adding a half twist.

### R12. Independent quality checks, including direction

Use several distinct tests rather than one “fit score”:

1. Bidirectional distance between the frozen target sheet and the **evaluated** Membrane.
2. Boundary/coverage error, including narrow painted appendages and unwanted bridging.
3. Corresponding material-station error, so nearest-point proximity cannot hide swapped rows.
4. Axial tangent error in a common local frame, including interior loft locations.
5. Qualified attachment position/target and explicit junction/seam equality.
6. Degenerate chart/curve findings and advisory bone penetration.

Concrete counterexample: two different families of straight parallel Fibers can both loft
to the same planar square. Their geometric distance is zero although one family is rotated
90 degrees from the paint. Shape accuracy therefore cannot imply directional accuracy.
Transport and compare tangent vectors at corresponding material points; at a branch use
the relevant part's field. `acos(abs(dot(t_fit,t_paint)))` is the proposed axial angle;
near-zero tangents or field magnitude are failures to measure, not zero error.

An analytic route to a conservative tangent check is available for cubic Beziers: derivative
control vectors are `3*(P[i+1]-P[i])`, and the derivative lies in their convex hull. After
subdivision, test whether that hull stays away from zero and lies inside the accepted cone
around a reference tangent. Include variation of the target field/transport over the cell
in the angle allowance. If the hull test is inconclusive, subdivide; do not report the
endpoint/sample maximum as certified. This is a proposed bound construction derived from
the spline basis, not a measured implementation. Actual curve derivatives are also exposed
by standard spline APIs. [Eigen spline derivatives](https://eigen.tuxfamily.org/dox/unsupported/classEigen_1_1Spline.html).

CGAL bounded-error symmetric Hausdorff supplies a candidate numerical bound for triangle
meshes; its API documents that the bounded version currently runs sequentially regardless
of the concurrency tag. It has no cancellation argument in the public signature.
[Distance API](https://doc.cgal.org/6.1.1/Polygon_mesh_processing/group__PMP__distance__grp.html).
Use adaptive independent holdouts for fast feedback and investigate a cancellable bounded
validator for final qualification. The core already has AABB/query infrastructure. Do not
assume that adding a concurrency tag fixes responsiveness.

A concrete cancellable alternative is triangle branch-and-bound around existing native
point-to-mesh queries. For a triangle centroid `c`, let `r` be the maximum centroid-to-vertex
distance. Distance to a fixed mesh is 1-Lipschitz, so `distance(c,target)+r` is an upper
bound over that triangle; distances at sampled points are lower bounds on its maximum.
Maintain a priority queue of unresolved triangles, split the largest uncertain triangle,
and check cancellation between batches. Combine bounds over all triangles, then repeat in
the other direction. Accept only if the global upper bound including numerical allowance
is within tolerance; reject early if a lower bound exceeds it; otherwise refine or report
that the bounded work did not establish accuracy. This is a conservative derived variant
to compare with CGAL's implementation, not a claimed equally fast replacement. It avoids
turning a timed-out measurement into a false passing result.

Track the whole error budget: capture/target approximation + curve tessellation + measured
mesh distance + distance-estimation uncertainty. A passing distance estimate must include
its upper error allowance. Bezier control-hull subdivision and derivative bounds are
candidates for adaptive curve/tangent validation; sparse tangent samples alone do not
certify a maximum angle. Corners require one-sided tangents. No claim can bound unrecorded
human intent; the captured target and confidence are the comparison contract.
[Adaptive subdivision reference](https://orbit.dtu.dk/en/publications/adaptive-subdivision-and-the-length-and-energy-of-b%C3%A9zier-curves/).

### R13. Execution, dependencies, defaults and computational cost

Use fixed-basis sparse least squares as the first fit model; separate grouping/chart
updates from repeated coefficient solves. Cache only immutable prepared support queries,
chart operators and factorizations whose inputs actually match. Endpoint RHS changes may
reuse a factorization; topology, field weights, knot layout or constraints can invalidate it.
Gap depth gestures should reuse a prepared basis and change a scalar where possible.

All projection batches, fitting, candidate selection, field/chart calculations and repeated
geometry checks belong in C++. Python owns records, commands, dependency/read validation,
undo and publication. Reuse [authored jobs](../src/anthroforge/application/authored_jobs.py)
and the single coordinator; an interactive draft does not justify a competing solver pool.
Bound input samples, chart faces, fit degrees of freedom, validation subdivisions and
retained candidates independently. Release superseded work and retain only useful failure
evidence. Poll cancellation between native phases/iterations and account for uninterruptible
factorization/library calls explicitly.

Dependency assessment:

| Candidate | Disposition from research |
| --- | --- |
| Existing Eigen, native fit, PIQP and native queries | First implementation candidates; measure dense versus sparse/inequality cases. |
| Existing CGAL 6.1.1 | Investigate polygon sets, directed charts and bounded distance; per-package build/license and cancellation checks still required. |
| Existing minimum-twist frames and Bezier split/fit | Reuse first; do not replace curve behavior app-wide without evidence. |
| Directional | Useful constrained power-field/integration reference; primarily MPL2 with per-file exceptions. Pin and inspect numerical headers if needed; the site mixes version/dependency descriptions, so do not treat it as a verified minimal build. [Project/license](https://avaxman.github.io/Directional/) |
| StrokeStrip/Gurobi | Research comparator; no automatic adoption of separately licensed solver or discrete optimizer. |
| Geometry Central, Open CASCADE, PCL | Method/API references or comparators; no demonstrated need to introduce these full dependencies yet. |

Existing values are not new defaults: Draw's `FitSettings.error=0.002` and its 70-degree
corner angle govern curve fitting/corner detection, not Muscle Paint's angular accuracy.
Native surface caps (16,384 stations; 262,144 vertices; 524,288 triangles) constrain output,
not permissible fit-system memory. Do not copy any of these into unrelated controls.

Default spatial/angular tolerances and depth threshold require representative scale sweeps
and recorded visual acceptance. Research can determine the quantities and normalization,
but cannot honestly derive acceptable anatomy error or a millisecond budget without data.
This is remaining calibration/qualification, not an unresearched method question.

### R14. Temporary paint, one undo chronology and invalidation

**Observed integration gap:** [History](../src/anthroforge/application/history.py) creates
an entry only when the Document changes. Paint-only strokes deliberately do not create
document anatomy and must not dirty project content merely to get Undo. The existing
history cannot satisfy that requirement through a no-op document command alone.

**Recommended design direction:** let the current history mechanism carry an optional
owned transient edit-state delta/snapshot alongside the ordinary Document state. Paint-only
entries leave saved document state/checkpoints unchanged; Generate/Update entries own both
the document change and its association with the unchanged paint. Undo Generate restores
the prior document but preserves the draft; the next Undo can remove the preceding stroke.
Do not create hidden SCPs, serialized paint objects or a second competing Undo stack.
This is a specific extension to an observed responsibility, not a general event-sourcing rewrite.

Store stroke edits immutably with bounded shared data; regenerate derived coverage lazily
from the nearest valid transient snapshot when needed. A generated-object edit/deletion or
support change records paint discard in the same history entry, so Undo can restore it.
Document close releases it. Source revision signatures distinguish geometry changes from
presentation changes. Common rigid motion can be recognized from unchanged shape plus a
shared rigid transform; compare relative support frames rather than a blanket document
revision. A scale/shear is not a rigid motion. For a one-support painting, rigid movement
of that complete support/paint assembly remains coherent.

During Generate, capture the paint generation, support geometry/poses, allowed targets and
binding evidence at dispatch. Publication validates those reads, including membership that
changes eligible targets. Undo, discard or superseding edits invalidate pending work; no
completed worker may resurrect a discarded painting. Historical saves serialize only the
ordinary selected Document, never a pointer to transient paint or native previews.

### Combined candidate pipeline

Keep these stages separate enough to identify which one fails:

1. **Capture:** record stroke identity, physical width, camera, supported contacts, target
   identity/revision and gap spans. Perimeter edits change coverage without destroying flow.
2. **Group:** use support/layer continuity, world-space proximity and compatible axial
   tangents. Retain Keep Separate and ambiguous branch decisions. Replay order/camera changes
   to check stability; never infer anatomical bindings from coverage alone.
3. **Construct a target sheet:** preserve contact positions and gap course/depth. Compare a
   simple interpolated strip baseline with constrained displacement smoothing. Keep supported
   ends fixed and user gap handles explicit. Freeze this target before evaluating fit quality.
4. **Assign material coordinates and flow:** initially compare the addon's directed chart
   with stroke-guided correspondence. Carry explicit longitudinal stations through sampling;
   normalized arc length on each curve independently may skew cross-sections.
5. **Fit editable rows:** test the addon cubic-longitudinal/piecewise-linear-transverse model
   against that target. Lock qualified endpoints and explicit junctions. Adapt the fixed-row
   sparse-selection idea, then refit and independently verify the actual final loft.
6. **Assess and publish:** separate shape, footprint, direction and binding errors; report
   penetration as advisory. Publish only via existing atomic authored creation/undo semantics.

A useful test model is `S(u,v) = sum_i A_i(u) C_i(v)`, where `A_i` are piecewise-linear
across-Fiber weights and `C_i` are cubic longitudinal curves. This expresses the inspected
ruled-loft representation, rather than fitting an unrelated smooth surface. Fixed sample
coordinates make a least-squares/fairness subproblem linear in curve coefficients. Shared
curve identities and hard endpoint positions supply constraints. Direction penalties and
free correspondence require separate formulation; do not claim the whole problem is convex.

For angular reporting, a candidate axial metric is
`acos(clamp(abs(dot(normalized_fiber_tangent, normalized_paint_tangent)), 0, 1))`,
after both directions are expressed at corresponding points in a common tangent frame.
Zero tangents, ambiguous correspondence and singularities need explicit invalid-data findings,
not zero error. This metric is a proposal, not a selected acceptance implementation.

Auto count must distinguish **more Fibers across** from **more controls along** and more
evaluation samples. The existing shortest-path minimum applies only to fixed rows and band
tests. Joint refitting changes those band errors, so a refit/refine loop is heuristic and
must be rechecked; it cannot inherit the original minimality claim.

An approximately arbitrary painted footprint is not necessarily representable by one
ordered loft under current branch restrictions. Identify that mismatch explicitly. Do not
silently fill holes, invent nested branches or increase resolution indefinitely. Closed
paths require periodic correspondence with an explicit seam/binding region; an open disk
chart is not an acceptable substitute.

## 5. Experiments that would decide applicability

These are proposed research fixtures, not executed tests or new product constraints.

| Experiment | Compare | Discriminating evidence |
| --- | --- | --- |
| E1: flat, bowed and twisted single bands with known flow | Existing addon fit; simple sampled rows; native sparse selection + joint refit | Actual standalone loft, not only fitted samples: shape/flow errors, endpoint drift, Fiber/control counts, narrow-tip retention and material station stability. |
| E2: overdrawing and layers | Simple support-aware grouping; StrokeStrip-inspired station alignment; SurfaceBrush-inspired adjacency | Same/reverse strokes merge; 90-degree crossings and two nearby layers remain distinct. Test same strokes at different rates, ordering and camera angles. Record false merges separately from failed merges. |
| E3: two supports over a background bone | Existing drawing fallback; contact-interpolated strip; constrained gap displacement | Background rejected across full width, smooth curved support still followed, no jump on wheel input, zero-offset shape unchanged, supported ends fixed, reproducibility under zoom/event rate. |
| E4: Y branch and two nonoverlapping side branches | Existing explicit branch evaluator fed by fitted rows | Exact junction identities, welded seams, root interval validity and shape around roots. A shared whole-edge two-patch example alone cannot pass. Include deliberate ambiguous/nested/disconnected rejection cases. |
| E5: closed band and variable-width loop | Periodic fit/material stations versus open-fit-with-closure baseline | Seam continuity, closed curve evaluation, binding region preservation and actual closed loft. Include a sharp closing-course example to expose hidden oversmoothing. |
| E6: narrow protrusion and unsampled between-row bump | Fit-sample error; independent dense holdout; bounded-error mesh distance | Detect missing coverage and unwanted bulges. Keep direction failure separate even when surfaces coincide. Record tessellation uncertainty rather than calling sampling a proof. |
| E7: qualified anatomical paint examples | Best passing variants on SCM-like neck strip, broad pectoral fan and serratus-like branches | Multi-angle paint/loft overlays, endpoint targets, direction plots and penetration Issues. Use current schema-compatible assets or captured fixtures; old project names alone are not valid replay inputs. |
| E8: physical brush and depth replay | Identical geometric gestures sampled at different event rates, zoom levels and views | R1/R2: physical coverage stays consistent; no progressive threshold ratchet or newly painted backside. A conservative uncertain gap is distinct from an incorrect support attachment. |
| E9: known field/chart contradictions | Positive-weight chart; stroke-constrained field/integration; independent geometry-only fit | R7/R12: reverse directions agree, perpendicular directions do not, zero field/singularities are reported, flipped charts never count as successful parameterization. Include the coincident-square/90-degree flow counterexample. |
| E10: periodic material correspondence | Existing closed alignment + arc length; proposed cyclic material map | R11: distinguish geometric closure from stable cross-sections, including unequal row lengths, reversal, seam movement, deformation, save/reopen and ordinary consumer behavior. |
| E11: temporary-history sequence | Stroke A, stroke B, Generate, Undo, Undo, Redo; source edit/discard/Undo; asynchronous superseding work | R14: generated construction and stroke history unwind independently in one chronology; no false project dirtying, resurrection or serialized paint. |
| E12: cost/cancellation and solver choice | Dense addon baseline; fixed-correspondence sparse solve; PIQP where inequalities are actually needed | R8/R13: equal objectives/constraints and output evidence, preparation versus solve versus validation time, memory, cancelled work release, no uncontrolled nested worker pools. |

For E1/E4/E5, record native output before and after normal parent propagation as well as
generation. This checks that apparently good fitting has not hidden an incompatible
correspondence or binding. Expected deformation must come from existing semantics, not a
new optimizer. Include straight-line degenerate normals and width-near-zero cases as explicit
findings, without silently publishing empty regions.

Use the profiler for capture, target-sheet work, chart/field work, row selection, fit,
qualified binding, independent validation, publication, model updates and memory. Record
input sizes, peak retained bytes, cancellation latency and warm/cold repetitions. No
numerical budgets or interactive speed promise can yet be justified from this research.

Recommended experimental order: **E1 → E2/E3/E8/E9 → E4/E5/E10 → E6/E7**, with E11/E12
integrated as soon as their boundaries exist. Failure in E1 should send us
back to the actual loft representation before investing in more elaborate paint UI. Repeated
failure after 3–4 meaningful refinements calls for a materially different approach, with
the failed attempts retained as evidence. Product-policy changes still require discussion.

## 6. Research conclusions versus remaining qualification

**Coverage:** R1–R14 each has a concrete method direction, alternatives/limitations and
local integration consequences. The four initially highlighted gaps have specific answers:
contact-constrained gap interpolation/displacement; partial-boundary branch fitting through
the existing seam operator; cyclic curves with periodic material correspondence; and
independent geometric/material/tangent validation. They are no longer deferred as generic
“needs research” labels.

**Recommended combined approach:** retain a contact-aware painted target sheet and separate
coverage/axial-flow data; make a checked chart per main/branch part; fit ordinary editable
Bezier Fibers using a native constrained ruled-loft model; refine rows/knots based on the
actual remaining error; validate the assembled native result; and create ordinary bindings
and Membrane records atomically. Use existing native queries, frames and numerical libraries
first. A general mesh reconstruction, learned grouping system, automatic quad remesher or
ROUTED solve is not the preferred default on current evidence.

**Concrete shared-boundary work discovered:** periodic surface correspondence, branch-aware
fit assembly, physical brush coverage and transient participation in history. None should
be hidden as a local paint-tool exception. The recommendations do not change confirmed
product behavior or authorize an unannounced app-wide algorithm replacement.

**Still requiring experiments rather than more generic literature:** actual anatomy fit
quality, tolerance/default calibration, the simplest adequate gap/field variant, numerical
degeneracy handling, solver crossover sizes, cancellability and peak memory. The tests above
discriminate those questions. Research cannot honestly certify speed, universal convergence
or arbitrary painted-surface representability without implementation and representative data.
No production algorithm, dependency, schema or final API is selected or changed here.

## 7. Local source evidence

Addon root:
`C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
Local documents may change independently of HEAD; these SHA-256 values identify the
reviewed key files without claiming all local edits were committed:

| Addon path | SHA-256 |
| --- | --- |
| `docs/smooth_native_base.md` | `7bbea1003630542fe7253281635fdc02e57260d2da3d3d9617705f2551336117` |
| `core/authoring/fiber_layout.py` | `b7e0bdbaae534496d2aba01001b53c78fcb7300525ca1482d1ff30ac166fd379` |
| `core/authoring/layout_reduction.py` | `867404e598fc000bf32ca5b4cd3ffb0282d4d3ff72ad0bfe048f839f0496f5d8` |
| `native/fiber_ccd/af_base_spline.hpp` | `31f92be9ccd0d3df1ebb4cb99bead05770c724f354a3c650bedee02b75f71a6f` |
| `native/fiber_ccd/af_base_order.hpp` | `279f6e54aa95af0ae3f23d5af21a9633f4038f20e830505572cf98a050c07128` |
| `native/fiber_ccd/af_base_partition.hpp` | `4575c3a30d2a57e76ca2c37b58262ca4eb3d838e0a8915a825b594ced5ae83d4` |

The maintained [task record](tasks/muscle-paint-050-research.md) records documentation
verification and delivery. No source assets were modified or research implementations
downloaded/built for this initial pass.
