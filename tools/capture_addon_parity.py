"""Run in Blender's background process; read addon behavior, emit portable reference cases."""

import itertools
import json
import sys
from pathlib import Path

addon, output = map(Path, sys.argv[sys.argv.index("--") + 1 :])
sys.path[:0] = [str(addon.parent), str(addon), str(addon / "tests/blender")]

import bpy  # noqa: E402
from _helpers import reset_scene, root, scp_with_object  # noqa: E402
from core.scp_runtime.attachment_runtime import (  # noqa: E402
    apply_scp_attachments,
    capture_attachment_from_link,
)
from core.scp_runtime.common import scp_prop_map  # noqa: E402
from core.scp_runtime.lookup import set_parent_relation  # noqa: E402
from mathutils import Euler, Matrix, Vector  # noqa: E402

VERTICES = [(-0.7, -0.4, -0.2), (0.9, -0.3, -0.1), (0.1, 0.8, -0.3), (0.2, 0.1, 1.1)]
FACES = [(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)]


def geometry(name):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(VERTICES, (), FACES)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def flat(matrix):
    return [value for row in matrix for value in row]


def pose(location, rotation, scale):
    return Matrix.LocRotScale(Vector(location), Euler(rotation).to_quaternion(), Vector(scale))


def setup(parent_mode, child_mode, strategy, follow):
    reset_scene()
    document = root()
    parent = scp_with_object(document, "Parent", geometry("Parent"))
    child = scp_with_object(document, "Child", geometry("Child"))
    child.attach_parent_anchor_mode, child.attach_child_anchor_mode = parent_mode, child_mode
    child.attach_tangent_strategy, child.attach_follow_rotation = strategy, follow
    set_parent_relation(child.transform_object_ref, child, parent.transform_object_ref)
    child.transform_object_ref.matrix_world = pose(
        (1.4, 0.23, 0.17), (0.13, 0.24, 0.31), (0.2, 0.3, 0.25)
    )
    bpy.context.view_layer.update()
    return document, parent, child


def case(parent_mode, child_mode, strategy, follow, scale):
    document, parent, child = setup(parent_mode, child_mode, strategy, follow)
    settings = dict(
        parent_mode=parent_mode, child_mode=child_mode, strategy=strategy, follow_rotation=follow
    )
    return evaluate(document, parent, child, scale, settings)


def evaluate(document, parent, child, scale, settings):
    p, c = parent.transform_object_ref, child.transform_object_ref
    initial = {"parent": flat(p.matrix_world), "child": flat(c.matrix_world)}
    assert capture_attachment_from_link(child, c, c, p, p)
    p.matrix_world = pose((0.3, 0.2, 0.7), (0.4, -0.2, 0.8), scale)
    bpy.context.view_layer.update()
    apply_scp_attachments(
        None, document, bpy.context.scene, scp_prop_map(document), parent_ids={parent.id}
    )
    return dict(
        initial=initial,
        target=flat(p.matrix_world),
        expected=flat(c.matrix_world),
        settings=settings,
    )


def capture():
    variants = itertools.product(
        ["OBJECT_ORIGIN", "SURFACE_NEAREST"],
        ["FACE_CENTER", "VERTEX_NEAREST", "OBJECT_ORIGIN"],
        ["AUTO", "STABLE_SURFACE", "DEFORMATION_FLOW"],
        [True, False],
        [(1.3, 0.8, 1.1), (-1.3, 0.8, 1.1)],
    )
    cases = [case(*values) for values in variants]
    output.write_text(json.dumps(dict(vertices=VERTICES, faces=FACES, cases=cases), indent=2))
    print(f"Captured {len(cases)} Blender attachment references: {output}")


capture()
