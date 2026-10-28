"""Capture the addon's ordinary Fiber proxy bevel without altering source projects."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import bpy
from mathutils import Vector


def cases():
    return [
        dict(name="vertical", points=[[0, 0, 0], [0, 0, 1]]),
        dict(name="horizontal", points=[[0, 0, 0], [1, 0, 0]]),
        dict(name="bent", points=[[0, 0, 0], [0.2, 0.1, 0.4], [0.1, 0.3, 0.8], [0.4, 0.2, 1]]),
        dict(
            name="loop",
            points=[[0, 0, 0], [0.3, 0, 0.1], [0.4, 0.3, 0], [0, 0.4, 0.2]],
            closed=True,
        ),
        dict(name="duplicate", points=[[0, 0, 0], [0, 0, 0], [0, 0.2, 0.4], [0.1, 0.1, 0.9]]),
        dict(name="reverse", points=[[0, 0, 0], [0, 0, 1], [0, 0, 0.2]]),
    ]


def mesh_arrays(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        return dict(
            vertices=[list(v.co) for v in mesh.vertices],
            faces=[list(p.vertices) for p in mesh.polygons],
            triangles=[list(t.vertices) for t in mesh.loop_triangles],
        )
    finally:
        evaluated.to_mesh_clear()


def create_proxy(row):
    from anthroforge.core.visualization.fiber_sync_helpers import (
        _write_curve_payload,
        create_fiber_proxy,
    )

    obj = create_fiber_proxy(
        bpy.context.scene.collection, SimpleNamespace(name="Fixture"), row["name"], (1, 0, 0, 1)
    )
    _write_curve_payload(
        obj, [Vector(p) for p in row["points"]], 0.001, False, row.get("closed", False), "fixture"
    )
    return obj


def capture(row):
    obj = create_proxy(row)
    settings = dict(
        bevel_resolution=obj.data.bevel_resolution,
        twist=obj.data.twist_mode,
        caps=obj.data.use_fill_caps,
        resolution=obj.data.resolution_u,
    )
    bpy.context.view_layer.update()
    result = row | dict(radius=0.001, settings=settings, output=mesh_arrays(obj))
    bpy.data.objects.remove(obj, do_unlink=True)
    return result


def main():
    addon, output = map(Path, sys.argv[sys.argv.index("--") + 1 :])
    sys.path.insert(0, str(addon.parent))
    payload = dict(
        blender=bpy.app.version_string,
        build=bpy.app.build_hash.decode(),
        cases=[capture(row) for row in cases()],
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(
        [(row["name"], row["settings"], len(row["output"]["vertices"])) for row in payload["cases"]]
    )


if __name__ == "__main__":
    main()
