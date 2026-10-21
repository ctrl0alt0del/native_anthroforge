# Blender 5.0.1 primitive/deformer provenance

AnthroForge 0.1.2 adapts the following Blender algorithms to owned arrays, immutable
construction records, and the existing C ABI. Blender objects, dependency graph,
operators, RNA and Python runtime are not compiled into or required by the application.
The adaptations are included in the corresponding AnthroForge source distribution.

Upstream revision: **v5.0.1**, reference executable build **a3db93c5b259**.
Original sources carry **GPL-2.0-or-later** notices; AnthroForge's adaptations are
distributed under **GPL-3.0-or-later**. Original attribution is retained in adapted
files. See the repository LICENSE and licenses/GPL-2.0.txt.

| AnthroForge implementation | Blender source / behavior |
| --- | --- |
| native/src/curves.cpp | [curve.cc](https://github.com/blender/blender/blob/v5.0.1/source/blender/blenkernel/intern/curve.cc): Bézier handles, vector/automatic handling and evaluation; aligned handles change only during explicit handle editing |
| native/src/curve_frames.cpp | curve.cc, [math_rotation_c.cc](https://github.com/blender/blender/blob/v5.0.1/source/blender/blenlib/intern/math_rotation_c.cc), displist.cc: minimum-twist frames, tilt and radius |
| native/src/curve_deform.cpp | [curve_deform.cc](https://github.com/blender/blender/blob/v5.0.1/source/blender/blenkernel/intern/curve_deform.cc), anim_path.cc: path interpolation and deformation |
| native/src/hooks.cpp | [MOD_hook.cc](https://github.com/blender/blender/blob/v5.0.1/source/blender/modifiers/intern/MOD_hook.cc), object_hook.cc: binding transforms, membership, weights, falloff, reset/recenter |
| native/src/curve_mapping.cpp | [colortools.cc](https://github.com/blender/blender/blob/v5.0.1/source/blender/blenkernel/intern/colortools.cc), DNA_color_types.h: custom falloff handles, interpolation tables and extrapolation |
| native/src/lattices.cpp and application/control_operations.py | [lattice_deform.cc](https://github.com/blender/blender/blob/v5.0.1/source/blender/blenkernel/intern/lattice_deform.cc), lattice.cc, key.cc, rna_lattice.cc, MOD_lattice.cc: interpolation, coordinates, Outside, weights, limits and resizing |
| native/src/solidify.cpp | [MOD_solidify_extrude.cc](https://github.com/blender/blender/blob/v5.0.1/source/blender/modifiers/intern/MOD_solidify_extrude.cc), math_vector.cc: Simple Solidify offsets, rims, normal correction, signed angles and clamping |

The adjacent `blender_501_sources.json` pins the SHA-256 and original attribution of
the inspected upstream files. These are algorithm sources, not runtime dependencies.
Body base construction and connected loft topology are AnthroForge implementations.
Connected adjacent loft seams deliberately differ from the reference Geometry Nodes
graph, which emitted disconnected strips. Complex Solidify, Blender animation and
shape-key systems are outside this release.

Compact reference data live in tests/fixtures/primitives. Their generators under tools
create in-memory reference scenes or read the two original anatomical .blend files
with automatic script execution disabled. They never save those .blend files.
The scene fixtures embed source paths and SHA-256 identifiers. Synthetic fixtures
record their Blender version/build. Comparison tolerances and exercised options are
explicit in test_primitive_parity.py, test_curve_parity.py and test_anatomy_primitives.py.
Passing those cases qualifies the stated coverage, not every possible Blender scene.

Nearest-surface Shrinkwrap uses Blender 5.0.1
`source/blender/blenkernel/intern/shrinkwrap.cc` (`shrinkwrap_snap_with_side` and
nearest-surface coordinate/weight semantics), adapted to owned libigl mesh trees.
Source: https://raw.githubusercontent.com/blender/blender/v5.0.1/source/blender/blenkernel/intern/shrinkwrap.cc
Blender Authors, GPL-2.0-or-later; adaptation GPL-3.0-or-later.
`tools/capture_shrinkwrap.py` and `blender501_shrinkwrap.json` pin 24 weighted,
nonuniform-transform and signed-offset cases across four nearest-surface snap modes.
Ray projection, target-normal projection and smooth-normal Above Surface are not
claimed by this nearest-surface adapter.
