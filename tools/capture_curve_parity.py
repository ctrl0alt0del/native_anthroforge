"""Capture Blender curve-modifier output from small deterministic constructions."""

import json
import sys
from pathlib import Path

import bpy

POSITIONS = ((0, 0, 0), (0.4, 0.2, 0.3), (0.8, -0.3, 0.6), (1.3, 0.2, 0.8))


def curve_object(mode, closed, tilted):
    data = bpy.data.curves.new("Curve parity", "CURVE")
    data.dimensions, data.resolution_u, data.twist_mode = "3D", 24, "MINIMUM"
    spline = data.splines.new("BEZIER")
    spline.bezier_points.add(len(POSITIONS) - 1)
    for index, (point, position) in enumerate(zip(spline.bezier_points, POSITIONS, strict=True)):
        point.co = position
        point.handle_left_type = point.handle_right_type = mode
        point.tilt, point.radius = (index * 0.4 if tilted else 0), 1 + index * 0.3
    spline.use_cyclic_u = closed
    obj = bpy.data.objects.new("Curve parity", data)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def body_object():
    data = bpy.data.meshes.new("Body parity")
    points, faces = body_data()
    data.from_pydata(points, [], faces)
    obj = bpy.data.objects.new("Body parity", data)
    bpy.context.scene.collection.objects.link(obj)
    return obj, points, faces


def body_data():
    points = [
        (i / 8, y, z)
        for i in range(9)
        for y, z in ((-0.1, -0.2), (0.1, -0.2), (0.1, 0.2), (-0.1, 0.2))
    ]
    faces = [
        (i * 4 + j, i * 4 + (j + 1) % 4, (i + 1) * 4 + (j + 1) % 4, (i + 1) * 4 + j)
        for i in range(8)
        for j in range(4)
    ]
    return points, faces


def point_record(point):
    return dict(
        position=list(point.co),
        left=list(point.handle_left),
        right=list(point.handle_right),
        left_mode=point.handle_left_type,
        right_mode=point.handle_right_type,
        radius=point.radius,
        tilt=point.tilt,
    )


def curve_record(obj):
    spline = obj.data.splines[0]
    return dict(
        points=[point_record(p) for p in spline.bezier_points],
        closed=spline.use_cyclic_u,
        resolution=spline.resolution_u,
        radius_interpolation=spline.radius_interpolation,
        tilt_interpolation=spline.tilt_interpolation,
    )


def evaluated(obj):
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    points = [list(v.co) for v in mesh.vertices]
    evaluated.to_mesh_clear()
    return points


def case(mode, closed, tilted, fit):
    curve = curve_object(mode, closed, tilted)
    curve.data.use_stretch, curve.data.use_deform_bounds = fit, True
    body, vertices, faces = body_object()
    modifier = body.modifiers.new("Curve", "CURVE")
    modifier.object, modifier.deform_axis = curve, "POS_X"
    expected = evaluated(body)
    result = dict(
        curve=curve_record(curve), fit=fit, vertices=vertices, faces=faces, expected=expected
    )
    bpy.data.objects.remove(body, do_unlink=True)
    bpy.data.objects.remove(curve, do_unlink=True)
    return result


def main():
    cases = [
        case(mode, closed, tilted, fit)
        for mode in ("AUTO", "VECTOR")
        for closed in (False, True)
        for tilted in (False, True)
        for fit in (False, True)
    ]
    data = dict(blender=bpy.app.version_string, build=bpy.app.build_hash.decode(), cases=cases)
    Path(sys.argv[sys.argv.index("--") + 1]).write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )
    print(f"Captured {len(cases)} curve reference cases")


if __name__ == "__main__":
    main()
