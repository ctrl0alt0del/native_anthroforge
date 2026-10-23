"""Read original Blender projects and capture narrow shortcut attachment references."""

import hashlib
import json
import sys
from pathlib import Path

import bpy

BINDING_FIELDS = (
    "parent_tri_vidx",
    "parent_tri_weights",
    "parent_flow_tri_vidx",
    "parent_flow_tri_weights",
    "parent_tangent_hint_local",
    "parent_offset_local",
    "child_origin_local",
    "child_tangent_local",
    "child_normal_local",
)


def register(addon):
    sys.path.insert(0, str(addon.parent))
    from anthroforge.properties.scp_properties import (
        AF_SCP_BoundObject_Property,
        AF_SCP_Property,
        AF_SCP_System_Property,
    )

    for cls in (AF_SCP_BoundObject_Property, AF_SCP_Property, AF_SCP_System_Property):
        bpy.utils.register_class(cls)
    bpy.types.Object.af_scp_system = bpy.props.PointerProperty(type=AF_SCP_System_Property)


def flat(matrix):
    return [float(value) for row in matrix for value in row]


def geometry(scp):
    obj = scp.geometry_object_ref.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = obj.to_mesh()
    frame = scp.transform_object_ref.matrix_world.inverted() @ obj.matrix_world
    try:
        return dict(
            vertices=[list(frame @ vertex.co) for vertex in mesh.vertices],
            faces=[list(face.vertices) for face in mesh.polygons],
        )
    finally:
        obj.to_mesh_clear()


def objects(scp, parent):
    return (
        scp.transform_object_ref,
        scp.geometry_object_ref,
        parent.transform_object_ref,
        parent.geometry_object_ref,
    )


def capture(scp, parent):
    from anthroforge.core.scp_runtime.attachment_runtime import capture_attachment_from_link

    capture_attachment_from_link(scp, *objects(scp, parent))
    return binding(scp, parent)


def binding(scp, parent):
    from anthroforge.core.scp_runtime.runtime_state import read_attachment_runtime

    values = [v for name in BINDING_FIELDS for v in read_attachment_runtime(scp, "attach_" + name)]
    rotation = parent.transform_object_ref.matrix_world.to_quaternion().inverted()
    hint = rotation @ parent.geometry_object_ref.matrix_world.to_quaternion()
    from mathutils import Vector

    values[12:15] = hint @ Vector(values[12:15])
    return [*values, read_attachment_runtime(scp, "attach_child_anchor_index")]


def state(scp, parent):
    return dict(
        child=flat(scp.transform_object_ref.matrix_world),
        parent=flat(parent.transform_object_ref.matrix_world),
        child_mesh=geometry(scp),
        parent_mesh=geometry(parent),
    )


def prepare(source, key):
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    root = next(obj for obj in bpy.data.objects if obj.af_scp_system.scps)
    scps = {scp.id: scp for scp in root.af_scp_system.scps}
    scp = scps[key]
    parent = scps[scp.parent_id]
    bpy.context.view_layer.update()
    return root, scp, parent


def change(object_name, property_name, delta):
    obj = bpy.data.objects[object_name]
    obj[property_name] += delta
    obj.update_tag()
    bpy.context.view_layer.update()


def cheekbone(source):
    from anthroforge.core.shortcuts.owner_backsolve import (
        apply_owner_backsolve,
        capture_owner_backsolve_snapshot,
    )

    root, child, parent = prepare(source, "SCP_6")
    result = dict(binding=capture(child, parent), before=state(child, parent))
    result["snapshot"] = capture_owner_backsolve_snapshot(root, bpy.context.scene, child.id)
    assert result["snapshot"] is not None
    change("Cheekbone_SuperHook", "AF Local X", 0.08)
    result["changed"] = state(child, parent)
    result["applied"] = apply_owner_backsolve(root, bpy.context.scene, result["snapshot"])
    return dict(result, expected=flat(child.transform_object_ref.matrix_world))


def pubis(source, strategy="DEFORMATION_FLOW"):
    from anthroforge.core.scp_runtime.attachment_runtime import AttachmentApply

    _, child, parent = prepare(source, "SCP_12")
    pubis_settings(child, strategy)
    result = dict(binding=capture(child, parent), before=state(child, parent), strategy=strategy)
    change("pubis_geom", "Pubis Arc Angle", -0.35)
    result["changed"] = state(child, parent)
    result["applied"] = AttachmentApply(
        child, *objects(child, parent), bpy.context.evaluated_depsgraph_get()
    ).run()
    return dict(result, expected=flat(child.transform_object_ref.matrix_world))


def pubis_settings(child, strategy):
    # Direct ID-property assignment avoids unrelated live addon update handlers.
    # Enum RNA fields use their numeric stored representation.
    for name, value in dict(
        parent_anchor_mode="SURFACE_NEAREST",
        child_anchor_mode="FACE_CENTER",
        follow_rotation=True,
        tangent_strategy=strategy,
    ).items():
        field = "attach_" + name
        prop = child.bl_rna.properties[field]
        child[field] = prop.enum_items[value].value if prop.type == "ENUM" else value


def source_hashes(paths):
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def run():
    addon, skeleton, skull, output = map(Path, sys.argv[sys.argv.index("--") + 1 :])
    register(addon)
    sources = source_hashes((skeleton, skull))
    result = dict(
        sources=sources,
        blender=bpy.app.version_string,
        pubis=pubis(skeleton),
        pubis_auto=pubis(skeleton, "AUTO"),
        cheekbone=cheekbone(skull),
    )
    assert sources == source_hashes((skeleton, skull))
    output.write_text(json.dumps(result), encoding="utf-8")
    print("Captured source shortcut attachment references", output)


if __name__ == "__main__":
    run()
