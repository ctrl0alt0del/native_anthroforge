# Routed surface sampling comparison

This is an isolated numerical experiment, **not a production attachment repair**.
It leaves the native application library and canonical distribution unchanged.

The real API creates two routed Fibers with preferred density 3 between two cube
supports. A third cube enters/leaves their route. Both paths grow 3 → 4 → 3.
The same accepted path buffers feed both comparison variants:

- **Exact prototype:** retain all path stations, merge numerically coincident stations
  within `1e-12` normalized length, and transport a probe at normalized longitudinal
  coordinate 0.33 and across coordinate 0.5. This exercises the proposed correspondence
  at the geometric level. It does not implement persisted attachment frames, tissue
  Final correspondence, constraints or fields for changing exact topology.
- **Fixed sampling:** 32 stations, the current surface consumer default, plus an
  8-station sensitivity check. The 32-station experiment geometry is compared against
  the actual application surface to `1e-12` m. Real Base/Final Anchors on its tissue
  retain their bindings through obstacle movement, undo/redo and reopening.

`sampling.cpp` performs station allocation, interpolation and corner-to-polyline
distance in C++; Python orchestrates, copies outputs and plots. Native application
collision checks test complete boundary segments, not only sample positions.
Corner deviation is not penetration depth. Boundary checks alone do not prove every
surface triangle is collision-free. This fixture does not establish arbitrary closed,
branched or cropped material-domain behavior.

The exact prototype uses normalized arc-length material coordinates; it demonstrates
sampling-independent locations, not a universal definition of tissue material motion.
Production work still needs a stable part/correspondence contract, role-aware transport,
resource persistence, and full deformation/attachment qualification.

## Run on Windows

From the repository root, use the existing native toolchain:

```powershell
. tools/common.ps1
Import-NativeEnvironment
New-Item -ItemType Directory -Path build/routed-fiber-surface-stability -Force
clang-cl /nologo /LD /EHsc /std:c++17 /O2 tools/experiments/routed_sampling/sampling.cpp /Fobuild/routed-fiber-surface-stability/sampling.obj /link /OUT:build/routed-fiber-surface-stability/sampling.dll /IMPLIB:build/routed-fiber-surface-stability/sampling.lib
.venv/Scripts/python.exe tools/experiments/routed_sampling/collect.py build/routed-fiber-surface-stability/sampling.dll build/routed-fiber-surface-stability/compare
.venv/Scripts/python.exe tools/experiments/routed_sampling/exact_limit.py
.venv/Scripts/python.exe tools/experiments/routed_sampling/plots.py build/routed-fiber-surface-stability/compare
```

Plotting requires Matplotlib in the development environment; it adds no application
dependency. The `.npz` files contain actual evaluated paths and experiment surfaces.
JSON reports include collisions, sample counts, corner error and transport probe
positions. PNG figures use matched cameras/scales and are not application screenshots.

`exact_limit.py` independently demonstrates the current production failure:
exact surface connectivity changes and a retained Base attachment correctly refuses
to reuse old indices. Near-coincident exact stations also produce degenerate tissue
frames. These remain unresolved until the production repair is selected and integrated.

The prior [OMPL interpolation reference](https://ompl.kavrakilab.org/classompl_1_1geometric_1_1PathGeometric.html)
informed the route-corner contract; the experiment's actual native outputs determine
the comparison, not the external reference.
