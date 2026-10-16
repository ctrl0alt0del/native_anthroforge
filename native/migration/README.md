# SCP attachment kernel provenance

attachment_wave_reference.hpp is an unchanged copy of the addon's
native/fiber_ccd/af_attachment_wave.hpp, captured 2026-10-16.
SHA-256: 5BAF4DD3681EE327BF184639EAA2A8386DA43228004BE55345988E6F17097750.

The standalone adapter reuses its surface frame and propagation mathematics.
Its process-global worker setting is fixed at one: the document scheduler owns
concurrency, avoiding competing OpenMP pools. Native cancellation occurs between
SCP operations. Blender capture is replaced with owned native mesh queries.

The original addon remains the parity reference and is not a runtime dependency.
