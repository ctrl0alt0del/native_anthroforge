"""Run with Blender 5.0.1 --background --factory-startup --disable-autoexec.

Captures native modifier reference data without saving any Blender document.
"""

import json
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector

VERTICES = [(-1, -1, 0), (0, -1, 0), (1, -1, 0), (-1, 1, 0), (0, 1, 0.4), (1, 1, 0.4)]
FACES = [(0, 1, 4, 3), (1, 2, 5, 4)]
FALLOFFS = ("NONE", "SMOOTH", "SPHERE", "ROOT", "SHARP", "LINEAR", "CONSTANT", "INVERSE_SQUARE")
INTERPOLATIONS = ("KEY_LINEAR", "KEY_CARDINAL", "KEY_CATMULL_ROM", "KEY_BSPLINE")
SHELL_CASES = (
    (-1, False, False, False, 0, False),
    (0, True, False, False, 0, False),
    (1, True, True, False, 0, False),
    (-0.3, False, False, True, 0, False),
    (-1, True, True, False, 1, False),
    (0.5, True, False, False, 1, True),
)
SHELL_NAMES = dict(
    even="use_even_offset",
    high_quality_normals="use_quality_normals",
    rim="use_rim",
    rim_only="use_rim_only",
    flip="use_flip_normals",
    clamp="thickness_clamp",
    angle_clamp="use_thickness_angle_clamp",
    invert="invert_vertex_group",
    minimum="thickness_vertex_group",
)


def matrix(values):
    translation = Matrix.Translation(Vector(values[:3]))
    rotation = Euler(values[3:6]).to_matrix().to_4x4()
    return translation @ rotation @ Matrix.Diagonal((*values[6:], 1))


def flat(value):
    return [component for row in value for component in row]


def mesh_object():
    mesh = bpy.data.meshes.new("Reference")
    mesh.from_pydata(VERTICES, [], FACES)
    owner = bpy.data.objects.new("Reference", mesh)
    bpy.context.scene.collection.objects.link(owner)
    return owner


def evaluated(owner):
    bpy.context.view_layer.update()
    evaluated = owner.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    result = [list(vertex.co) for vertex in mesh.vertices]
    evaluated.to_mesh_clear()
    return result


def weighted(owner):
    group = owner.vertex_groups.new(name="Influence")
    weights = [1, 0.25, 0.5, 0.75, 0, 1]
    for index, weight in enumerate(weights):
        group.add([index], weight, "REPLACE")
    return weights


def hook_case(falloff, uniform, invert):
    owner, target, modifier = hook_setup()
    options = hook_settings(owner, modifier, falloff, uniform, invert)
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


def dispose(*objects):
    for obj in objects:
        bpy.data.objects.remove(obj, do_unlink=True)


def hook_setup():
    owner = mesh_object()
    owner.matrix_world = matrix([1, 2, 0, 0.2, 0.3, -0.1, 1.2, 0.8, 1.5])
    target = bpy.data.objects.new("Hook", None)
    bpy.context.scene.collection.objects.link(target)
    target.matrix_world = matrix([0.2, -0.3, 0.4, 0.1, -0.4, 0.3, 1, 1.5, 0.7])
    bpy.context.view_layer.update()
    modifier = owner.modifiers.new("Hook", "HOOK")
    modifier.object = target
    modifier.matrix_inverse = target.matrix_world.inverted() @ owner.matrix_world
    return owner, target, modifier


def hook_settings(owner, modifier, falloff, uniform, invert):
    modifier.strength, modifier.falloff_radius, modifier.center = 0.7, 2, (0.1, 0.2, 0.1)
    modifier.falloff_type, modifier.use_falloff_uniform = falloff, uniform
    modifier.vertex_indices_set([0, 1, 3, 4, 5])
    weights = weighted(owner)
    modifier.vertex_group, modifier.invert_vertex_group = "Influence", invert
    return dict(
        hook_options(modifier), weights=weights, invert=invert, uniform=uniform, falloff=falloff
    )


def hook_options(modifier):
    return dict(
        strength=0.7,
        radius=2,
        center=[0.1, 0.2, 0.1],
        indices=[0, 1, 3, 4, 5],
        bind=flat(modifier.matrix_inverse),
    )


def lattice_control(interpolation, outside):
    data = bpy.data.lattices.new("Cage")
    cage = bpy.data.objects.new("Cage", data)
    bpy.context.scene.collection.objects.link(cage)
    data.points_u, data.points_v, data.points_w = 3, 4, 3
    data.interpolation_type_u = data.interpolation_type_v = data.interpolation_type_w = (
        interpolation
    )
    for index, point in enumerate(data.points):
        point.co_deform += Vector((0.03 * (index % 3), -0.02 * (index % 5), 0.04 * (index % 7)))
    data.use_outside = outside
    cage.matrix_world = matrix([0.1, 0.2, -0.1, 0.2, -0.3, 0.1, 2, 3, 1.5])
    return cage


def lattice_case(interpolation, outside, invert):
    owner, cage = mesh_object(), lattice_control(interpolation, outside)
    modifier = owner.modifiers.new("Lattice", "LATTICE")
    modifier.object, modifier.strength = cage, 0.6
    weights = weighted(owner)
    modifier.vertex_group, modifier.invert_vertex_group = "Influence", invert
    result = dict(
        lattice_options(cage, interpolation, outside),
        weights=weights,
        invert=invert,
        owner=flat(owner.matrix_world),
        expected=evaluated(owner),
    )
    dispose(owner, cage)
    return result


def lattice_options(cage, interpolation, outside):
    return dict(
        kind="LATTICE",
        target=flat(cage.matrix_world),
        points=[list(p.co_deform) for p in cage.data.points],
        resolution=[3, 4, 3],
        interpolation=interpolation.removeprefix("KEY_"),
        outside=outside,
        strength=0.6,
    )


def solidify_case(options):
    owner = mesh_object()
    modifier = owner.modifiers.new("Thickness", "SOLIDIFY")
    modifier.solidify_mode = "EXTRUDE"
    for key, value in options.items():
        setattr(modifier, SHELL_NAMES.get(key, key), value)
    weights = weighted(owner)
    modifier.vertex_group = "Influence"
    result = dict(
        kind="THICKNESS", options=dict(options, weights=weights), **evaluated_surface(owner)
    )
    dispose(owner)
    return result


def evaluated_surface(owner):
    bpy.context.view_layer.update()
    obj = owner.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = obj.to_mesh()
    result = dict(
        expected=[list(vertex.co) for vertex in mesh.vertices],
        faces=[list(p.vertices) for p in mesh.polygons],
    )
    obj.to_mesh_clear()
    return result


def cases():
    hooks = [
        hook_case(mode, uniform, invert)
        for mode in FALLOFFS
        for uniform, invert in ((False, False), (True, True))
    ]
    lattices = [
        lattice_case(mode, outside, invert)
        for mode in INTERPOLATIONS
        for outside, invert in ((False, False), (True, True))
    ]
    return hooks + lattices + [solidify_case(shell_options(*case)) for case in SHELL_CASES]


def shell_options(offset, even, hq, rim_only, clamp, angle):
    return dict(
        thickness=0.2,
        offset=offset,
        even=even,
        high_quality_normals=hq,
        rim=True,
        rim_only=rim_only,
        clamp=clamp,
        angle_clamp=angle,
    )


def main():
    target = Path(sys.argv[sys.argv.index("--") + 1])
    result = dict(
        blender=bpy.app.version_string,
        build=bpy.app.build_hash.decode(),
        vertices=VERTICES,
        faces=FACES,
        cases=cases(),
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Captured {len(result['cases'])} Blender modifier fixtures: {target}")


if __name__ == "__main__":
    main()
