"""Blender 5.0.1 background operator fixtures; no viewport or user input."""

import json
import math
import sys
from pathlib import Path

import bpy


def samples(closed, corner):
    if corner:
        return [[i / 20, 0, 0] for i in range(21)] + [[1, i / 20, 0] for i in range(1, 21)]
    count = 80 if closed else 81
    return [
        [
            math.cos(i * math.pi * (2 if closed else 1) / 80),
            math.sin(i * math.pi * (2 if closed else 1) / 80),
            0,
        ]
        for i in range(count)
    ]


def curve(name):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    return obj


def record(point):
    return dict(
        position=list(point.co),
        left=list(point.handle_left),
        right=list(point.handle_right),
        left_mode=point.handle_left_type,
        right_mode=point.handle_right_type,
        radius=point.radius,
        tilt=point.tilt,
    )


def stroke_point(index, position):
    return dict(
        name=str(index),
        location=position,
        mouse=(index * 3, 0),
        mouse_event=(index * 3, 0),
        x_tilt=0,
        y_tilt=0,
        pressure=1,
        time=index / 60,
        is_start=index == 0,
        size=1,
    )


def draw(method, closed, source):
    settings = dict(
        fit_method=method,
        error_threshold=0.005,
        corner_angle=math.radians(70),
        use_cyclic=closed,
        stroke=[stroke_point(i, p) for i, p in enumerate(source)],
        wait_for_input=False,
    )
    assert bpy.ops.curve.draw("EXEC_DEFAULT", **settings) == {"FINISHED"}


def capture(method, closed, corner):
    source = samples(closed, corner)
    obj = curve(f"{method}_{closed}_{corner}")
    draw(method, closed, source)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)
    spline = obj.data.splines[-1]
    return dict(
        method=method,
        closed=closed,
        corner=corner,
        samples=source,
        expected=[record(p) for p in spline.bezier_points],
    )


def main():
    if bpy.app.version[:3] != (5, 0, 1):
        raise RuntimeError("Pinned Blender 5.0.1 required.")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    cases = [
        capture(method, closed, corner)
        for method in ("REFIT", "SPLIT")
        for closed, corner in ((False, False), (False, True), (True, False))
    ]
    save(cases)


def save(cases):
    output = Path(sys.argv[sys.argv.index("--") + 1])
    blend = Path(sys.argv[sys.argv.index("--") + 2])
    blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()), check_existing=False)
    data = dict(blender=bpy.app.version_string, build=bpy.app.build_hash.decode(), cases=cases)
    output.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Captured {len(cases)} drawing operator fixtures")


if __name__ == "__main__":
    main()
