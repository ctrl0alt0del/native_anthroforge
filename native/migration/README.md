# SCP attachment kernel provenance

attachment_wave_reference.hpp is an unchanged copy of the addon's
native/fiber_ccd/af_attachment_wave.hpp, captured 2026-10-16.
SHA-256: 5BAF4DD3681EE327BF184639EAA2A8386DA43228004BE55345988E6F17097750.

The standalone adapter reuses its surface frame and propagation mathematics.
Its process-global worker setting is fixed at one: the document scheduler owns
concurrency, avoiding competing OpenMP pools. Native cancellation occurs between
SCP operations. Blender capture is replaced with owned native mesh queries.

The original addon remains the parity reference and is not a runtime dependency.

## Bind-time owner transitions

`src/attachment_weights.cpp` ports the numerical work from the addon's
`core/vcp/fiber_node_attachment_weights.py`, captured 2026-10-18.
Source SHA-256: `fbc0a79439ace1f82b6b5ac7bbe9a280e682843a25bfe173bdc4a70f8e37b712`.
It preserves hard-pin span partitioning, arc-length owner runs, quintic transitions,
cyclic spans, duplicate-position handling and the one/two-influence thresholds.
Python only packs inputs and returned records. Eleven compact reference cases are in
`tests/fixtures/attachments/owner_weights.json`, reproducible with
`tools/capture_attachment_weights.py ADDON_PATH OUTPUT_PATH`.

Generic point capture/resolution now shares `attachment.cpp`'s existing surface capture
and the unchanged migration kernel's `af_surface_frame`. Batched input avoids synthetic
SCPs and per-point Python numerical queries. Bindings retain canonical triangle vertices,
barycentric coordinates and frame offsets; ordinary resolution never selects a new parent.

## Production routing kernel closure (integration in progress)

`routing/sources.json` pins the production addon's numerical headers and the collision
portion of `af_fiber_ccd.cpp` by source hashes and exact line ranges. Reproduce with
`tools/capture_routing_kernels.py ADDON_PATH`. These unchanged reference files retain
the upstream formatting. Owned adapters in `src/routing*.cpp` follow the function limit.
Only this numerical closure is compiled: no addon Python, Blender objects or dependency
graph, muscle/skin code, public legacy ABI, or competing OpenMP pool. Kernel entry points
are private to the adapter. The application's existing coordinator owns work concurrency.

Native adapters own surface snapshots, transforms, direct-reference allocation, open
hard-pin spans/global closed paths, production SQP settings, cancellation between trials,
path correspondence and output preparation. Planner preparation ports
`core/vcp/v2/planner.py` and its production session helpers, including sparse/dense/expanded,
pin-exit and warm recovery plus the separate handoff clearance check. A pinned 1050-node
pin-tree fixture checks its graph and thirteen paths; compact end-to-end cases remain
separate evidence. Broader anatomical and warm-path qualification is still required.

`tests/fixtures/routing/addon.json` contains compact actual addon outputs and loaded-source
hashes. The four current cases cover clear open/closed paths and a cube detour/bound route.
They match the standalone numerical output to absolute 1e-10. This does not establish
production anatomical, full planner, GUI or release acceptance. Capture through
`tools/capture_routing_reference.py ADDON_PATH OUTPUT_PATH` without Blender/desktop input.
