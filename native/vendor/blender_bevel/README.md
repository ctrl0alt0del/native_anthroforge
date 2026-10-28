# Blender 5.0.1 Fiber bevel subset

`frames.inc` retains four upstream `curve.cc` functions without body changes. The manifest
records the source URL, full source hash, exact byte ranges, individual hashes and retained
file hash. Recreate it with `tools/restore_blender_skin_bevel.py <pinned-curve.cc>`.

`native/src/skin_bevel_frames.cpp` supplies an owned geometry-only point/list adapter.
`skin_bevel_points.cpp` preserves POLY duplicate removal and endpoint directions;
`skin_fiber.cpp` adapts the full-circle ring from `curve_bevel.cc` and placement/topology
from `displist.cc`. The shared BLI math implementation lives in the pinned `blender_bmesh`
subset and has its own reconstruction manifest. No Blender runtime is required.

Source: https://github.com/blender/blender/tree/v5.0.1/source/blender/blenkernel/intern
License: GPL-2.0-or-later, NaN Holding BV and Blender Authors, as retained in source headers.
Distributed as part of GPL-3.0-or-later AnthroForge; license texts accompany the source.

The addon sets a 3D POLY curve's bevel depth. Blender's defaults are resolution 4 (12
vertices/ring), minimum twist and no fill caps. The skin adapter applies these to accepted
world-space paths at the authored skin radius. Workspace presentation is not an input.
Six background Blender captures in `tests/fixtures/skin/fiber_bevel.json` qualify this
subset; `tools/capture_skin_fibers.py` records the actual addon writer and Blender build.
