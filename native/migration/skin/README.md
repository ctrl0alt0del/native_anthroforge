# Skin source kernels

These headers are pinned copies of the maintained addon gap/tile/binding/quality
kernels at the source revision and hashes in `sources.json`. They remain GPL-3.0-or-later.
`native/src/skin_kernel.hpp` includes them privately alongside the already-pinned triangle
query infrastructure, in a skin-only namespace. The dedicated `af_skin_kernels` object
target enables the source OpenMP loops with their existing maximum of four threads.
The coordinator reserves four CPUs for envelope jobs; combined construction already
reserves all CPUs. Routing keeps its separate serial compilation boundary. No Blender
runtime, exported legacy ABI or independent task queue is introduced. Authored adapters
retain the application's owned handles and cancellation. Missing OpenMP is a compilation
error rather than a silent serial fallback.
One integration-only adaptation in `af_skin_gap.hpp` replaces the scene cancellation
atomic with `KernelCancellation`. It reads the existing job cancellation flag during
native loops, without a polling thread. A serialized RAII access scope borrows the flag
only for the call and clears it on all exits. Source hashes describe the original input;
this adapter does not alter contact, gap, field, smoothing or binding calculations.

After supported-component filtering, the unfiltered temporary mesh is released. After
the same eight smoothing iterations, `af_skin_tiles_release_field` frees varying voxel
blocks, flags and copied coarse fields before diagnostics, matching addon `finish()`.
Source geometry, separators and corridor checks remain alive for validation. Borrowed
input Fields stay intact for inspection/retry. No memory budget or precision is changed.
October 28 execution/lifetime changes await build, parity and performance qualification:
the user has paused all testing while playing. Earlier evidence does not qualify them.

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
