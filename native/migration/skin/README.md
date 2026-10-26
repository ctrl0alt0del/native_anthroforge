# Skin source kernels

These headers are unchanged copies of the maintained addon gap/tile/binding/quality
kernels at the source revision and hashes in `sources.json`. They remain GPL-3.0-or-later.
`native/src/skin_kernel.hpp` includes them privately alongside the already-pinned triangle
query infrastructure. No Blender runtime, exported legacy ABI or OpenMP worker pool is
introduced. Authored adapters retain the application's owned handles and cancellation.

Current integration: source-aware gap sampling only. Compilation of the full header set
does not establish tile reconstruction, binding, quality or final-skin qualification.
Source capture and coarse scalar fields are separate from these source-aware predicates.
The first source-port tests preserve gap width, stricter two-sided policy selection,
winding independence and disjoint patches of a single source.
