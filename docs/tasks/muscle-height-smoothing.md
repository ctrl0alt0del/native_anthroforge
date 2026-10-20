# Repair the saved muscle workflow

- Task branch: `codex/muscle-height-smoothing`
- Integration branch: `main`
- Starting revision: `dda3af44d2899bd27da95eb20c75ca15d743260e`
- Status: diagnosis established; geometric behavior decision pending; no production fix
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

1. Clarify whether correction may change generated inflation directions/shape while
   retaining authored settings and attachment constraints. The user asked to choose
   the repair path once the cause is known.
2. Qualify the chosen numerical correction against this actual fixture, including
   refinement sensitivity and QP stability. Merely changing failure messages is insufficient.
3. Add representative regression coverage; validate GUI, persistence and packaging.
4. Run the development gate, checkpoint/push, then validated merge/push.

No production code, release package, or original project has changed. Full development
and package gates are not run: this is a diagnostic checkpoint, not a delivered fix.
The original SHA256 was checked again after the experiments and is unchanged.

## Recovery inputs

- Original: `E:/development/WIP_models/muscle_test.anthroforge`
- SHA256: `adff36f1c75943ae808369edb26f989d0423d392a70399d0ac2267c590b6a3f7`
- Untouched local copy/evidence: `build/muscle-height-smoothing/`
- Local scripts: `probe_case.py`, `inspect_shapes.py`, `intersection_view.py`;
  isolated C++ probe under `probe/`. The probe currently has the unsuccessful robust
  solve experiment enabled; restore default `afs::Options{}` to reproduce the
  original candidate. `candidate.npz` retains the actual default-solver candidate.
- Local evidence: `diagnosis.json`, `exact_intersections.json`,
  `intersection_lengths.json`, `sections.png`, `confirmed-crossing.png`.
  The intersection image is a diagnostic geometry plot, not a desktop acceptance capture.
- Independent checker installed only under ignored `independent-check/`; it is not
  an application dependency and did not change the project's lockfile/environment.
- Existing untracked root `__init__.py` is unrelated and must remain untouched.

The containing Git commit identifies this checkpoint; inspect remote reachability
before treating work as recoverable from another machine.
