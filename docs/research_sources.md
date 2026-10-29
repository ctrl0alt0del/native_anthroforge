# Research sources and candidate methods

This is a reading list, not a record of qualified production algorithms. Implemented
calculations and changes belong in [computation history](computation_history.md).
Muscle Paint references checked: 2026-10-29. Tissue reading-list review: 2026-10-21.

## Muscle Paint: strokes to editable Fibers and Membranes

See the [0.5.0 product contract](specification_050.md) and
[method/capability review](muscle_paint_050_research.md). The review inventories the addon's
sparse layout and native smooth-base fitter, compares SurfaceBrush, StrokeStrip, SecondSkin,
line fields, constrained fitting and bounded-error geometry checks. Its R1–R14 review
includes concrete methods for gaps, branching seams, periodic correspondence, physical
brush/depth policies, adaptive fitting, independent direction accuracy and transient history.
It identifies current integration gaps and proposes discriminating experiments for each.
These are research candidates, not implemented or qualified algorithms. The first comparison
should fit the actual native loft; no new reconstruction dependency is selected.

## Pixar research library

**Bookmark: [Pixar Research](https://research.pixar.com/).** Browse this library when
investigating geometry, deformation, simulation, rendering and production workflows.
The old `graphics.pixar.com/library/` address now redirects to Pixar's technology page,
which links this current library. Papers do not imply available implementation code.

## Tissue self-intersection reading list

| Source | Evidence and reading status |
| --- | --- |
| Baraff, Witkin and Kass, [Untangling Cloth](https://research.pixar.com/docs/2003.SiggraphPapers.BWK.pdf), SIGGRAPH 2003 | Full paper inspected, particularly sections 3 and 5–7. GIA traces intersection contours, flood-fills smaller regions, then selects attraction, repulsion or neither for cloth dynamics. Some folded regions rely on surrounding forces. This is not a globally convergent optimization method; boundary intersections remain unsupported by its active repair. |
| Wicke, Lanker and Gross, [Untangling Cloth with Boundaries](https://graphics.stanford.edu/~wicke/publications/untangling/wlg-ucwb-06.pdf), VMV 2006 | Relevant sections inspected. Extends path classification and uses RBF correspondence. Direct separation can oscillate; penalty relaxation performed better in their experiments. The authors still give no universal unfolding guarantee. |
| Wong, Eberle and Kim, [Clean Cloth Inputs](https://research.pixar.com/docs/2018.SiggraphTalks.WEK.pdf), SIGGRAPH Talks 2018 | Full two-page talk inspected. Uses tetrahedral ARAP simulation with constraints, rest-state retargeting and collision processing, including GIA. Evidence of a broader production application; not evidence that a surface-only tissue adapter is sufficient. |
| Cha and Ko, [Tanglement Resolution in Clothing Simulation with Explicit Convergence](https://snu.elsevierpure.com/en/publications/tanglement-resolution-in-clothing-simulation-with-explicit-conver/), TVCG 2022, DOI 10.1109/TVCG.2020.3039566 | Author-institution abstract inspected only. Reports finite-step resolution under conditions using triangle shrinkage and vertex pull. Read the full conditions and geometry effects before claiming relevance to retained tissue bindings. |

## AnthroForge assessment, not an implementation decision

The current height smoother solves a convex, bound-constrained biharmonic QP on a
fixed base domain. It rescales existing displacement directions; it does not impose
triangle-separation constraints. Competing local minima are therefore not the reason
this particular objective fails to repair all intersections. See
[QP assembly](../native/migration/smoothing/src/assembly.cpp) and
[height reconstruction](../native/src/smoothing_core.cpp).

The 2003 GIA method is worth studying for intersection classification, but is not yet
qualified as a static tissue repair. Its repeated analysis and simulation steps offer
no fixed repair-iteration bound. Its historical cost measurement is not an interactive
AnthroForge performance estimate. In particular, our fixed backing and anatomical
constraints need not supply the motion that helps cloth untangle.

Any experiment must stay within one TissueVCP; separate tissues remain separate.
The user's objective is usable downstream geometry and a smooth exterior, not a
requirement to delete hidden faces, remesh, or simulate cloth. Separating intersecting
sheets alone does not establish the desired exterior shape.

Before selecting a method, classify the intersections in the historical
`muscle_test.anthroforge` failure snapshots under `build/muscle-height-smoothing/`.
Those local-only snapshots predate the Distributed direction-field correction; do not
describe them as a current unfixed inflation result. Test representative current
failures as they arise, rather than relying on easy cloth examples.

A useful comparison must record actual shape, remaining/new crossings, attachment
and backing errors, downstream material correspondence, runtime by stage, and iteration
progress/stalls. Compare against the current smoother and the original shape. A lower
crossing count or a successful linear solve alone is insufficient. No untangling
implementation, benchmark, or downstream acceptance qualification was performed for
this reading-list update.
