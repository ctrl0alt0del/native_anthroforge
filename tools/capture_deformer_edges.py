"""Additional Blender CurveMapping, cage-weight and resize reference cases."""

import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture_primitive_parity import (
    dispose,
    evaluated,
    flat,
    hook_settings,
    hook_setup,
    lattice_control,
    matrix,
    mesh_object,
)  # noqa: E402


def custom_settings(modifier, mode, extrapolate):
    mapping = modifier.falloff_curve
    mapping.initialize()
    points = mapping.curves[0].points
    points.new(0.2, 0.7)
    points.new(0.65, 0.4)
    for point in points:
        point.handle_type = mode
    mapping.extend = "EXTRAPOLATED" if extrapolate else "HORIZONTAL"
    mapping.update()
    return dict(
        custom=[v for p in points for v in p.location],
        custom_handles=[p.handle_type for p in points],
        custom_extrapolate=extrapolate,
    )


def custom_case(mode, extrapolate):
    owner, target, modifier = hook_setup()
    options = hook_settings(owner, modifier, "CURVE", True, False)
    options.update(custom_settings(modifier, mode, extrapolate))
    target.matrix_world = matrix([0.7, -0.2, 0.6, -0.2, -0.4, 0.6, 1.2, 0.7, 1.3])
    result = dict(
        kind="HOOK",
        owner=flat(owner.matrix_world),
        target=flat(target.matrix_world),
        options=options,
        expected=evaluated(owner),
    )
    dispose(owner, target)
    return result


def weighted_cage(cage):
    group = cage.vertex_groups.new(name="Cage weights")
    weights = [i % 7 / 6 for i in range(len(cage.data.points))]
    for index, weight in enumerate(weights):
        group.add([index], weight, "REPLACE")
    cage.data.vertex_group = group.name
    return weights


def resize_case(axis, count, outside):
    cage = lattice_control("KEY_BSPLINE", outside)
    weights = weighted_cage(cage)
    before = [list(p.co_deform) for p in cage.data.points]
    setattr(cage.data, "points_" + axis, count)
    result = dict(
        resize_output(cage),
        points=before,
        weights=weights,
        axis=axis,
        count=count,
        outside=outside,
    )
    dispose(cage)
    return result


def resize_output(cage):
    return dict(
        resolution=[3, 4, 3],
        expected=[list(p.co_deform) for p in cage.data.points],
        output_resolution=[cage.data.points_u, cage.data.points_v, cage.data.points_w],
    )


def cage_weight_case(outside):
    owner, cage = mesh_object(), lattice_control("KEY_CATMULL_ROM", outside)
    weights = weighted_cage(cage)
    modifier = owner.modifiers.new("Lattice", "LATTICE")
    modifier.object, modifier.strength = cage, 0.6
    result = dict(
        cage_metadata(cage, outside),
        owner=flat(owner.matrix_world),
        cage_weights=weights,
        expected=evaluated(owner),
    )
    dispose(owner, cage)
    return result


def cage_metadata(cage, outside):
    return dict(
        kind="LATTICE",
        target=flat(cage.matrix_world),
        points=[list(p.co_deform) for p in cage.data.points],
        resolution=[3, 4, 3],
        interpolation="CATMULL_ROM",
        outside=outside,
        weights=[1] * 6,
        strength=0.6,
        invert=False,
    )


def cases():
    hooks = [
        custom_case(mode, extrapolate)
        for mode in ("AUTO", "VECTOR", "AUTO_CLAMPED")
        for extrapolate in (True, False)
    ]
    resizes = [
        resize_case(axis, count, outside)
        for axis, count in (("u", 5), ("v", 1), ("w", 2))
        for outside in (False, True)
    ]
    return hooks + [cage_weight_case(outside) for outside in (False, True)], resizes


def main():
    modifiers, resizes = cases()
    data = dict(
        blender=bpy.app.version_string,
        build=bpy.app.build_hash.decode(),
        cases=modifiers,
        resizes=resizes,
    )
    Path(sys.argv[sys.argv.index("--") + 1]).write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )
    print("Captured CurveMapping, cage weights and resize fixtures")


if __name__ == "__main__":
    main()
