# Third-party native sources

- Eigen and libigl: copied unchanged from the addon's native/deformation/vendor
  on 2026-10-16; original MPL notices are retained. Only used headers compile.
- happly.h: nmwsharp/happly upstream source, retrieved 2026-10-16, MIT.
  SHA-256: 05A2BC71E9F3A48B2B996D06C5516254132D0F26F52B3FD845AFF2492BF51F82.
- mapbox/earcut.hpp: v2.2.4, ISC.
  SHA-256: 3B838BC3F643D34CED850B6D53B19E2D9ABDF6C2C067425B02868D131379B3CC.

These vendored snapshots need no network access during application builds.
Project function-length rules apply to authored adapters, not unchanged upstream sources.
