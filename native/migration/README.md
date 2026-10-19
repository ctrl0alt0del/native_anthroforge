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

## Production routing kernel closure

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
separate evidence. Warm continuation remapping ports `core/vcp/v3/warm.py`: each previous
authored span is arc-length resampled to the newly allocated pin interval, then pins are
restored exactly. Authored point identities, closure and binding parents gate compatibility.
Six donor-generated cases cover open/closed curves and 24/32/48 samples after anchor motion;
both remapping and resulting solves agree to absolute 1e-10.

`tests/fixtures/routing/addon.json` contains compact actual addon outputs and loaded-source
hashes. The four current cases cover clear open/closed paths and a cube detour/bound route.
They match the standalone numerical output to absolute 1e-10. Capture through
`tools/capture_routing_reference.py ADDON_PATH OUTPUT_PATH` without Blender/desktop input.

`tests/fixtures/routing/skull.json` additionally pins four evaluated SCP meshes from the
original `skull_muscles.blend` (9,158 vertices), explicit endpoint choices from four saved
fiber paths, nearest-parent choices and actual addon cold/warm solve outputs. Blender/file
and loaded-addon source hashes are included. Saved BAKE paths supply endpoints, not expected
solver output. These four cold/warm pairs match to absolute 1e-10. Extraction uses background
factory-startup Blender and does not save or modify the source. Reproduce with
`capture_skull_routing.py`, `skull_routing_qualification.py`, then
`capture_skull_routing_reference.py`. These fixtures establish those cases, not unrestricted
anatomical route correctness or complete release acceptance.

## Standalone routing contact and continuation corrections

The `solver_test.anthroforge` regression is captured compactly in
`tests/fixtures/routing/surface_pins.json`, including its source hash and accepted warm
path. Unbound ordinary curve knots may touch explicitly selected surfaces. Native nearest
queries classify only contacts within the captured world's numerical floor, independently
of anatomical bindings; explicit owners remain authoritative. This extends the addon
adapter to the first-class curve contract without modifying its pinned numerical kernels.

Warm seeds crossing solid interiors are replanned. This check permits recoverable clearance
deficits and retains localized contact exemptions; the solver still enforces its clearance
policy. A warm solve reported infeasible receives one cold planning attempt. Existing addon
cold/warm fixtures remain unchanged and pass. The new user case additionally checks actual
intersections; numerical parity alone does not establish collision clearance.

## Accepted authored-fiber collision checks

`path_collisions.cpp` uses the pinned routing collision-world, segment-triangle distance and
closed-mesh containment kernels for read-only advisory checks. `routing_world.cpp` separates
collision capture from planner snapshot construction so advisory work does not allocate a
routing graph. Batches own transformed path samples and reuse one captured collision world;
cancellation is checked between samples, segments and surfaces. The numerical contact
tolerance is `max(1e-9, 1e-9 * world diagonal)` metres, with an eight-tolerance arclength
neighborhood at explicitly bound knots. This is not a clearance-radius calculation.
`tests/test_path_collisions.py` covers crossings between samples, containment, closing edges,
attachment contact, transforms and cancellation. Original pinned kernel provenance remains
in `routing/sources.json`.

