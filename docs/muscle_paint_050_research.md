# Muscle Paint 0.5.0 — methods and initial research

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

The missing work is substantial: capture a coherent painted sheet over multiple supports
and gaps; combine coverage with axial direction; infer only permitted branch relationships;
choose a compact Fiber layout; preserve attachment strips; and verify the actual final
loft. Closed paths and partial branch roots need dedicated qualification. None can be
inferred from an ordinary open-patch fitting result.

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
| `core/authoring/smooth_native.py`; `native/fiber_ccd/af_base_spline.hpp`, `af_base_order.hpp` | Native scale-normalized spline fit combines sample fidelity and fairness, hard endpoints, shared-boundary equality and soft tangent regularization. Sampled ordering constraints can fail explicitly; there is no global topology guarantee. |
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

## 4. Proposed experimental decomposition, not an approved algorithm

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

For E1/E4/E5, record native output before and after normal parent propagation as well as
generation. This checks that apparently good fitting has not hidden an incompatible
correspondence or binding. Expected deformation must come from existing semantics, not a
new optimizer. Include straight-line degenerate normals and width-near-zero cases as explicit
findings, without silently publishing empty regions.

Use the profiler for capture, target-sheet work, chart/field work, row selection, fit,
qualified binding, independent validation, publication, model updates and memory. Record
input sizes, peak retained bytes, cancellation latency and warm/cold repetitions. No
numerical budgets or interactive speed promise can yet be justified from this research.

Recommended experimental order: **E1 → E2/E3 → E4/E5 → E6/E7**. Failure in E1 should send us
back to the actual loft representation before investing in more elaborate paint UI. Repeated
failure after 3–4 meaningful refinements calls for a materially different approach, with
the failed attempts retained as evidence. Product-policy changes still require discussion.

## 6. What is decided and what is not

- **Confirmed:** the product contract, native numerical ownership, reuse of existing
  branches/attachments/lifecycle, and no implicit routing or tissue creation.
- **Observed:** reusable native fit and sparse-layout ideas exist; important surrounding
  tools remain Python/Blender-specific; standalone already owns drawing, queries and lofts.
- **Recommended first experiment:** fit the final native loft directly using the addon
  formulation, then test sparse row selection and independent accuracy measurement.
- **Not decided:** target-sheet representation, exact grouping/field solver, gap interpolation,
  error-bound scheme, default tolerances/count limits, periodic/branch fitting details,
  dependency additions or final public APIs. No production algorithm has changed.

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
