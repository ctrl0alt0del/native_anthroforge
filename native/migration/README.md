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
