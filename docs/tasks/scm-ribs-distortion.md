# Sternocleidomastoid distortion after Ribs Top Radius

- Task branch: `codex/scm-ribs-distortion`
- Integration branch: `main`
- Starting revision: `4ff1ef8`
- Status: diagnosis complete; no production behavior changed
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
