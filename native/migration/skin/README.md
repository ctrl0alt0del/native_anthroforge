# Skin source kernels

These headers are pinned copies of the maintained addon gap/tile/binding/quality
kernels at the source revision and hashes in `sources.json`. They remain GPL-3.0-or-later.
`native/src/skin_kernel.hpp` includes them privately alongside the already-pinned triangle
query infrastructure. No Blender runtime, exported legacy ABI or OpenMP worker pool is
introduced. Authored adapters retain the application's owned handles and cancellation.
One integration-only adaptation in `af_skin_gap.hpp` replaces the scene cancellation
atomic with `KernelCancellation`. It reads the existing job cancellation flag during
native loops, without a polling thread. A serialized RAII access scope borrows the flag
only for the call and clears it on all exits. Source hashes describe the original input;
this adapter does not alter contact, gap, field, smoothing or binding calculations.

Current integration: source-aware gap sampling, protected lattice preparation, tiled
extraction, stitching, supported-component filtering and constrained smoothing.
Compilation of the full header set does not establish binding, quality or final-skin qualification.
Source capture and coarse scalar fields are separate from these source-aware predicates.
The first source-port tests preserve gap width, stricter two-sided policy selection,
winding independence and disjoint patches of a single source.

## Standalone centerline adaptation

The confirmed 0.4.0 policy uses bare-Fiber centerlines, not Blender bevel meshes.
`af_skin_gap.hpp` now consults an owned segment AABB for nearest-distance/support
queries; zero-width lines do not claim opposing surface normals. Empty triangle ray
queries are safe. `af_skin_bind.hpp` preserves the existing triangle-only weighting
and supports explicit segment identities and linear coordinates. The standalone ABI
adds element-kind buffers (0 triangle, 1 segment, -1 unbound). Source hashes in
`sources.json` continue to identify the original addon inputs, not modified copies.
