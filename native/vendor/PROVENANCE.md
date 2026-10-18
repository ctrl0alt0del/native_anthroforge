# Third-party native sources

- Eigen and libigl: copied unchanged from the addon's native/deformation/vendor
  on 2026-10-16; original MPL notices are retained. Only used headers compile.
- happly.h: nmwsharp/happly upstream source, retrieved 2026-10-16, MIT.
  SHA-256: 05A2BC71E9F3A48B2B996D06C5516254132D0F26F52B3FD845AFF2492BF51F82.
- mapbox/earcut.hpp: v2.2.4, ISC.
  SHA-256: 3B838BC3F643D34CED850B6D53B19E2D9ABDF6C2C067425B02868D131379B3CC.

These vendored snapshots need no network access during application builds.
Project function-length rules apply to authored adapters, not unchanged upstream sources.

## Curve fitting

`curve_fit_nd/` is unchanged from Blender tag `v5.0.1`, retrieved 2026-10-18:
https://github.com/blender/blender/tree/v5.0.1/extern/curve_fit_nd.
BSD-3-Clause, Copyright 2016 DWANGO Co., Ltd.; complete notices remain in every source.
Compiled as C separately from the authored C++ adapter. No Blender runtime or object system.
File SHA-256 values are recorded in `curve_fit_nd/SHA256SUMS`.

The adapter's deduplication, fit flags, split corner detection radii and handle-mode policy
follow Blender `source/blender/editors/curve/editcurve_paint.cc` at the same tag, GPL-2.0-or-later.
The application retains its GPL-3.0-or-later distribution license. Fitting is an atomic upstream
call with cooperative cancellation checks immediately before/after it; no mid-fit cancellation
or exact display-latency guarantee is claimed.

The stroke adapter also follows that source's one-pixel motion threshold, depth-only
substep count, screen-to-world tolerance ratio and eight-pixel closure test. Qt logical
pixels supply the UI scale. Automatic closure is disabled when a stroke changes view;
world-space tolerance remains available. Exact cached mesh rays replace Blender's raster
depth buffer, so silhouette/normal differences from raster depth are intentional.
