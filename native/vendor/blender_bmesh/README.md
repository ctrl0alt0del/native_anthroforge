# Blender 5.0.1 geometry-only BMesh subset

Source: https://github.com/blender/blender/tree/v5.0.1 (build a3db93c5b259).
Original SPDX notices remain in each file; GPL-2.0-or-later. See
`../../../licenses/GPL-2.0.txt` and `sources.json` for per-file provenance.

This subset retains Blender's actual collapse, connectivity mutation, bisect,
triangulation, heap, quadrics, mempool and numerical helper implementations.
Unreachable functions are omitted as complete definitions, leaving their source
line positions intact. Retained numerical function bodies are unchanged.
`sources.json` records original/retained SHA-256 hashes and omitted byte ranges.
`tools/restore_blender_bmesh.py` reproduces these files from the pinned source tree.
The parser used to discover the closure is not an application/build dependency.

Authored adapters live outside this directory. They accept geometry-only meshes,
keep canonical edge order between preparation stages, and reject attribute access
outside that subset. There is no Blender object system, Python runtime, UV or
multires support. CustomData origin-index layers are unnecessary for these owned
temporary inputs and are not exposed. Independent normal callbacks run on the
coordinator's worker; no Blender task scheduler is initialized. The Windows
allocator mutex adapter uses `std::mutex`.

Cancellation occurs during owned input preparation and at the boundaries of the
upstream collapse/bisect/triangulation calls. No mid-collapse cancellation or
latency guarantee is claimed. On cancellation, completed temporary BMeshes are
freed and cannot publish. Upstream functions retain their original style; the
15-line limit applies to the authored adapters.

Qualification remains in progress. Initial isolated checks match captured sphere,
ellipsoid and patch vertices when source edge order is retained. Half cutting
retains exact-on-plane degeneracies instead of deleting them. These checks alone
do not establish complete anatomical skin workflow acceptance.
