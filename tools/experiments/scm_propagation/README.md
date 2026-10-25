# SCM propagation experiment — not application code

Case: Sternocleidomastoid.L continuous belly, Ribs Top Radius `.983 -> 3`.
The native trial is a separate DLL. Nothing here is imported/linked/registered by the
application. Do not promote this into production without a separate reviewed design.

## Reproduce on the existing Windows development environment

Run from the repository root. The archived 96-muscle project must exist locally;
no production anatomy payloads or generated binaries are committed. `capture.py`
reads that source without a write lock and saves only under build. It refuses an
input whose driver is already edited. Existing work/results under this experiment's
build folder are replaced when the commands are rerun.

```powershell
. ./tools/common.ps1
Import-NativeEnvironment
cmake -S tools/experiments/scm_propagation -B build/scm-ribs-distortion/native -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=clang-cl -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build/scm-ribs-distortion/native --parallel 2
.venv/Scripts/python.exe tools/experiments/scm_propagation/capture.py
.venv/Scripts/python.exe tools/experiments/scm_propagation/run.py
.venv/Scripts/python.exe tools/experiments/scm_propagation/timing.py
.venv/Scripts/python.exe tools/experiments/scm_propagation/packed_timing.py
.venv/Scripts/python.exe tools/experiments/scm_propagation/audit.py
.venv/Scripts/python.exe tools/experiments/scm_propagation/quality.py
.venv/Scripts/python.exe tools/experiments/scm_propagation/profile_case.py
.venv/Scripts/python.exe tools/experiments/scm_propagation/render.py
.venv/Scripts/python.exe tools/experiments/scm_propagation/report.py
```

The last two commands use the locally available Matplotlib installation; it is not
added as a production dependency. The review is a self-contained local HTML file:
`build/scm-ribs-distortion/comparison/review.html`.

## Contracts and limits

- The fixture is specifically the three unparented SCM POLYLINE Fibers, each with one
  path sample per authored control. Parent vertex counts and triangle connectivity
  must match between baseline and edited snapshots. This is not a generic engine API.
- Eight cached affine regions per support, 64 fixed source vertices per region,
  small 3x3 fits, cubic B-spline interpolation, arc-length influence kernels and exact
  hard-pin corrections. No iterative path/global deformation solve or Python optimizer.
- The current algorithm and all consumer stages are unchanged. The isolated current
  pipeline is verified against saved production geometry at all four tissue stages.
- Direct ROUTED preserves all 73 constraints and fails on an intersecting structural
  point. The successful endpoint-only reference is deliberately different: two retained
  anatomical bindings, original rest path warm start, 73 requested samples, CUSTOM,
  153 automatic eligible surfaces. Explicit material-station mapping permits consumer
  inspection; it is not an equivalent normal engine conversion or anatomical truth.
- `run.py` records profiled timing, useful for attribution only. `timing.py` runs 12
  unrecorded counterbalanced trials from prepared parent data; `packed_timing.py` runs
  all six order permutations including dynamic input packing. All times are SCM-only,
  after parent geometry is available, excluding other anatomy, scheduling and viewport.
- Exact hard pins, neutral shape and a global rigid motion are checked. This does not
  qualify arbitrary scaling, topology changes, loops, other tissues or collision-free
  deformation. The remaining bulge/crossings are visible, not silently repaired.
- `quality.py` uses existing advisory transverse crossing checks; it excludes touching,
  coplanar contact and containment. Existing Spine endpoint contact is documented.

Research/diagnosis and results: `docs/tasks/scm-ribs-distortion.md`.
No project or package version changes; no canonical dist rebuild.

## Low-step routing follow-up

`hybrid_probe.py` records each direct conversion separately, then tests 1/4 accepted
steps with endpoint bindings and current/improved paths as warm-start candidates.
`pin_probe.py` localizes control contacts with batched native tiny-segment checks and
reproduces the first-interior-point rejection with a reduced constraint set and Spine
alone. These are trace-enabled diagnostic runs, not controlled timing trials. See the
task record for rejected warm starts, planning costs, and preserved endpoint checks.

## Direct SQP experiment — no planner

The user clarified that the current propagated curve itself must seed a small local solve.
Normal ROUTED's planner fallback is therefore excluded. `solver_only.cpp` builds a second
isolated DLL, `af_scm_solver_only.dll`, reusing the production `routing_solve.cpp` stage and
pinned kernels with owned surface inputs. It calls no planner or warm-start remapping.
Only two anatomical endpoint pins are fixed. Native failures are reported; the output
can be visualized as a rejected candidate but is never published into the application.

After building the experiment CMake project, run:

```powershell
.venv/Scripts/python.exe tools/experiments/scm_propagation/solver_qualification.py
.venv/Scripts/python.exe tools/experiments/scm_propagation/hybrid_retest.py
.venv/Scripts/python.exe tools/experiments/scm_propagation/solver_quality.py
.venv/Scripts/python.exe tools/experiments/scm_propagation/solver_review.py
```

Results are under `build/scm-solver-only/`. The application endpoint conversion command
prepares each input, with numerical resolution dispatched directly by the experiment.
All document objects are Manual inside this isolated setup to prevent unrelated queued
application calculations. The before variant routes in the baseline pose, captures a new
propagation field, and then deforms it. New baseline material captures are explicitly
retained in the edited resource set. This changes support influences and is not identical
to the original field. Scene capture and baseline recapture costs are reported separately
from warm execution. All calculations, including SQP iteration and repeated geometry
queries, remain C++; Python packs inputs, orchestrates calls, exports and renders evidence.

## Propagation-only smoothing experiment

`fairing.cpp` adds a third independent DLL. It combines the existing C2 prototype with
a cached, exact-pin differential-coordinate reconstruction. No routing or collision
scene is involved in evaluation. The adapter is limited to the current SCM's open
73-sample Polylines; it preserves dormant handle offsets rather than collapsing them.
The .05/.10/.20 reconstruction scales and .20/.35 support widths are experiments,
not application settings or qualified defaults. See the task record for the objective.

After building `af_scm_fairing` and `af_scm_solver_only`:

```powershell
.venv/Scripts/python.exe tools/experiments/scm_propagation/fairing_run.py
.venv/Scripts/python.exe tools/experiments/scm_propagation/fairing_quality.py
.venv/Scripts/python.exe tools/experiments/scm_propagation/fairing_contacts.py
.venv/Scripts/python.exe tools/experiments/scm_propagation/fairing_support.py
.venv/Scripts/python.exe tools/experiments/scm_propagation/fairing_review.py
```

Results: `build/scm-smoothing/review.html`. The all-segment contact diagnostic reuses
the earlier solver DLL's surface-capture adapter but calls only native validation,
never SQP or a planner. Contact checks have zero clearance and no endpoint exemptions;
do not confuse them with ROUTED's acceptance contract. Diagnostic calls are excluded
from the 14 balanced-order timing trials. Source and production files stay untouched.

## Production policy qualification

The historical experiments above remain independent. The approved .20 reconstruction
is now integrated as **Smooth Shape Preservation**, with **Local Surface Following**
retained in Preferences. See CH-078 in `docs/computation_history.md` for contracts,
compatibility, evidence and limits.

With the before/after fixture and the reviewed `build/scm-smoothing/fair20-*.npz` outputs
available, run:

```powershell
.venv/Scripts/python.exe tools/experiments/scm_propagation/production_qualification.py
```

It invokes the actual application evaluator for both policies, compares the new paths
to the reviewed prototype, rebuilds the same surface/tissue stages, checks geometric
findings, records counterbalanced timing and writes a profile under
`build/fiber-propagation/scm/`. The application does not load any experimental DLL.
