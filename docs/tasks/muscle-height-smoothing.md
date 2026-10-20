# Repair the saved muscle workflow

- Task branch: `codex/muscle-height-smoothing`
- Integration branch: `main`
- Starting revision: `dda3af44d2899bd27da95eb20c75ca15d743260e`
- Status: native correction implemented; focused checks pass; release qualification pending
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: local desktop chat, direct work

## Outcome and acceptance

Make the tissue workflow in the user's `muscle_test.anthroforge` work. Reproduce
and fix the owning cause, inspect actual geometry, exercise edits and persistence,
and qualify the canonical portable application. Preserve the original project.
All GUI validation stays offscreen; no desktop input or visible windows.

## Observed evidence

The saved tissue's Rest result fails with
`Height smoothing: Smoothing would collapse or reverse an existing face`.
Intrinsic/stacking and two ordinary routed curves subsequently fail on that
prerequisite. Two Fibers and their Membrane have accepted ready results.
The tissue uses Distributed inflation, amount 1 m, with Height smoothing
radius 0.2, strength 0.8, maximum change 0.05.

The rejection originates in `native/migration/smoothing/src/height.cpp`.
The user requires diagnosis before choosing a fix, strict preservation of settings,
and explanation of genuine limitations. Do not silently reduce inflation/smoothing,
change authored geometry, or introduce an adaptive fallback.

## Established diagnosis

An isolated C++ diagnostic reproduces the same QP candidate before the existing
normal-dot rejection. It does not change the application or original project.

| Saved refined base, Distributed amount | Inflation crossings (application checker) | Smoothing outcome |
| --- | --- | --- |
| 0.02 m, diagnostic comparison only | 0 | QP hits 250-iteration limit; no candidate published |
| 0.1 m, diagnostic comparison only | 10 | Production accepts despite 36 newly introduced crossing pairs |
| 1 m, actual saved setting | 1,453 | Candidate introduces 281 new crossing pairs; existing normal-dot test rejects |

The base itself has no crossings. At 1 m the candidate has zero newly collapsed
faces and ten faces whose normals rotate past 90 degrees. Thus the wording about
collapse/reversal is not an adequate geometric diagnosis, although accepting this
particular candidate would indeed expose invalid geometry.

Independent `libigl 2.6.3` exact-predicate intersection tests confirm proper,
nonadjacent, noncoplanar intersections: 1,456 inflated pairs, 875 candidate pairs,
281 newly introduced candidate pairs. Differences from the application baseline
count are attributable to the different intersection classifiers, not disappearance
of the defect. The longest confirmed inflation crossing segment is about 0.0734 m.
Original face pair 8894/12521 is disjoint in the base and intersects after inflation.

Inflation already fails before smoothing and before refinement: the accepted
56x86 Membrane inflated directly at 1 m has 356 crossing pairs. Standalone refinement
to 78x108 increases this to 1,453; at 0.1 m it changes zero crossings to ten.
The migrated Distributed kernel is byte-identical to the original addon's
`native/fiber_ccd/af_muscle_numeric.hpp` source range and recorded source hash.
Its locally derived normal displacements and local stability heuristic do not
guarantee an embedded surface. The current refinement/evaluation composition
amplifies the defect. No alternative algorithm has yet been qualified.

Strict retention of the exact existing displacement field cannot also remove its
intersections. This is not evidence that the user's numeric settings or intended
shape are intrinsically impossible. A correction must distinguish preserving those
settings/attachments from preserving the legacy per-vertex displacement formula.

There is also an independent numerical issue on the valid 0.02 m comparison:
PIQP reaches its iteration limit (primal residual 1.30e-17, dual 2.37e-6).
Turning on the existing `robust_linear_solve` option was tested only in the isolated
probe and worsened convergence; it is not an accepted fix. Do not recommend reducing
inflation as a complete workaround.

## Verification and next actions

1. The user approved changing generated directions/shape while preserving authored
   settings and attachment constraints, and requested addon reproduction.
2. Qualify the chosen numerical correction against this actual fixture, including
   refinement sensitivity and QP stability. Merely changing failure messages is insufficient.
3. Add representative regression coverage; validate GUI, persistence and packaging.
4. Run the development gate, checkpoint/push, then validated merge/push.

Production changes now exist on the task branch; no release package or original
project has changed. Full development and package gates remain pending.
The original SHA256 was checked again after the experiments and is unchanged.

## Recovery inputs

- Original: `E:/development/WIP_models/muscle_test.anthroforge`
- SHA256: `adff36f1c75943ae808369edb26f989d0423d392a70399d0ac2267c590b6a3f7`
- Untouched local copy/evidence: `build/muscle-height-smoothing/`
- Local scripts: `probe_case.py`, `inspect_shapes.py`, `intersection_view.py`;
  isolated C++ probe under `probe/`. The probe currently uses the independently
  certified iteration-limit adapter; `scaled.hpp`, `reduced.hpp` and `factor.hpp`
  retain rejected diagnostic experiments. `candidate.npz` still retains the actual
  original default-solver candidate before the normal-dot rejection.
- Local evidence: `diagnosis.json`, `exact_intersections.json`,
  `intersection_lengths.json`, `sections.png`, `confirmed-crossing.png`.
  The intersection image is a diagnostic geometry plot, not a desktop acceptance capture.
- Independent checker installed only under ignored `independent-check/`; it is not
  an application dependency and did not change the project's lockfile/environment.
- Existing untracked root `__init__.py` is unrelated and must remain untouched.

The containing Git commit identifies this checkpoint; inspect remote reachability
before treating work as recoverable from another machine.

## Addon reproduction and current experiments

Blender 5.0.1 was run in background against the current addon. Exact source (4,816
vertices) and refined (8,424 vertices) grids produce **bit-identical unsmoothed
positions** to standalone. Both fail Height smoothing with the same collapse/reverse
message. A normal addon scene built from the saved cube and two boundary Fiber
paths also fails: smoothing Off publishes 4,644 vertices; Height marks both proxies
INVALID and empties them. The different count in that scene comes from normal
addon loft preparation; it is not the exact-grid comparison.

`addon-off.blend` and `addon-height.blend` were saved with `StaticScene.save_debug_copy`,
reopened, and rendered in background. Both Fibers remain visible in ordinary Curve
display; the cube retains its native SCP color. The Off render visibly shows the
distorted envelope, while Height has no displayed muscle. Temporary rendering
changes were not saved. No addon source files were edited.

Evidence is local under the task build directory: `addon_reproduction.json`,
`addon-reopened.json`, both `.blend` files and `addon-*-render.png`. The initially
nonfinite source comparison was a diagnostic borrowed-array lifetime mistake;
owned array copies corrected it and both exact comparisons are now zero.

An isolated C++ experiment filters area-weighted displacement directions with
the mesh mass matrix and cotangent diffusion operator, leaving lengths unchanged.
For the actual refined 1 m case, tested radii 0.02, 0.1, 0.3 and 1 m remove detected
crossings. The unconstrained diagnostic view of each height-QP candidate also has
zero detected crossings/collapses, despite normal rotations that the old validator
rejects. This is **not yet a production correction**: direction scale, shape quality,
refinement sensitivity, independent intersection checks and regression qualification
remain unresolved. The old local stability heuristic also introduces sharp height
changes around the bend; its effect is being isolated rather than silently retained.

## Implemented candidate (not released)

- Distributed inflation now computes area-weighted normals and solves screened
  diffusion with physical distance equal to the authored inflation amount. It
  normalizes directions and applies the unchanged amount/edge/taper controls.
  The old local stability height reduction is removed. Donor files remain unchanged.
- Refinement subdivides existing intervals only when required by the requested
  material density. In the reported case it preserves the 56x86 source instead
  of introducing the ill-conditioned 78x108 overlay.
- Height smoothing reuses pinned field/QP preparation and diagnostics, then applies
  shared complete-mesh validation. Normal rotation alone no longer rejects a result.
- Inflation uses the same geometry validation before publication.
- Refinement exposed a false crossing in an existing Static PBD shell fixture.
  Native pair 24/1127 touches at one fixed point; independent libigl reports zero
  intersection length. A strict plane-side test now removes these false transverse
  classifications. The PBD kernel and numerical settings were not changed.

67 focused tests pass, including the saved bend at 0.02, 0.1 and 1 m, smoothing
bounds/pins, source retention, denser refinement, rigid/scale equivariance, planar
height, real-crossing rejection, coincident contact, relaxation, and corrected
envelope snapshots. Original donor fixtures are preserved; revised Distributed
snapshots are clearly identified as standalone regression evidence, not donor parity.

The actual project reevaluates through the shared Session API with Base, Rest,
Intrinsic and Final ready, no detected crossings/collapses. A texture-only GPU
capture was inspected at `candidate-gpu.png`; the sharp inherited height depression
is removed. The retained 1 m inflation and 0.1 boundary-band setting still produce
a tall, steep-sided envelope; no parameters were altered to make it look smaller.
Full gate, independent final intersection check, edit/save/undo inspection, and
portable qualification remain outstanding. Do not merge or call this released yet.

## Saved-base and solver qualification

The first complete development gate passed (1,324 tests, native contract/style,
script style, typing, numerical audit and doctor). Background editor acceptance,
GPU scene/picking acceptance and the actual project GPU capture also passed.
The saved project supports superseding edits, undo/redo and exact geometry after
save/reopen. Independent libigl exact-predicate inspection of its final 4,816-vertex
mesh found zero nonadjacent noncoplanar crossings.

An additional necessary case was found before packaging: a settings-only edit
can legitimately reuse the old saved 78x108 base. At 0.02 m its QP reaches the
250-iteration budget. Rescaling variables and eliminating fixed variables did not
resolve that stop; augmented curvature-variable experiments were not qualified
over the full amount range and are not production code.

Direct independent KKT checking established that the original iterate already
meets the existing application tolerance: relative stationarity about `5.07e-9`,
primal residual about `1.12e-26`, relative complementarity about `8.17e-14`.
The migrated Session rejected it before running that check. The standalone height
adapter now certifies **only maximum-iteration** candidates before allowing the
ordinary exact-pin/second-certification/geometry path. It preserves the solver's
terminal status in a diagnostic-aware ABI, keeps the old 12-value ABI compatible,
and publishes an accurate `ITERATION_LIMIT` warning with residual evidence.
No tolerance, authored setting, iteration budget or objective was relaxed.

32 focused tests pass after this change, including a compact reconstruction of
the saved old grid. New full gate and portable qualification remain pending.
The offscreen/headless evidence does not establish interactive desktop latency.
