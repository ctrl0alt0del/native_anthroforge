"""Read production .blend examples and capture compact local-coordinate reference fixtures.

Never saves a Blender file. Source SHA-256 records identify the untouched input revision.
"""

import hashlib
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture_curve_parity import body_object, curve_record, evaluated  # noqa: E402
from capture_primitive_parity import dispose, flat  # noqa: E402

PREFIXES = (
    "brow_ridge_curve",
    "mandible_front_",
    "mandible_side_curve",
    "clavicle_curve",
    "acromion_curve",
    "ilium_arc",
    "ribs_profile",
    "ribs_curve",
)


def clone_curve(source):
    obj = source.copy()
    obj.data = source.data.copy()
    obj.parent = None
    obj.matrix_world = source.matrix_world.copy()
    for modifier in list(obj.modifiers):
        if modifier.type != "HOOK":
            obj.modifiers.remove(modifier)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def hook_record(modifier):
    return dict(
        target=flat(modifier.object.matrix_world),
        target_name=modifier.object.name,
        options=dict(
            strength=modifier.strength,
            radius=modifier.falloff_radius,
            center=list(modifier.center),
            bind=flat(modifier.matrix_inverse),
            falloff=modifier.falloff_type,
            uniform=modifier.use_falloff_uniform,
            indices=list(modifier.vertex_indices),
            restrict=True,
        ),
    )


def resample_nodes():
    group = bpy.data.node_groups.new("AnthroForge parity sampling", "GeometryNodeTree")
    group.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    source, output = group.nodes.new("NodeGroupInput"), group.nodes.new("NodeGroupOutput")
    sample, mesh = (
        group.nodes.new("GeometryNodeResampleCurve"),
        group.nodes.new("GeometryNodeCurveToMesh"),
    )
    sample.inputs["Count"].default_value = 64
    group.links.new(source.outputs["Geometry"], sample.inputs["Curve"])
    group.links.new(sample.outputs["Curve"], mesh.inputs["Curve"])
    group.links.new(mesh.outputs["Mesh"], output.inputs["Geometry"])
    return group


def body_reference(curve):
    body, vertices, faces = body_object()
    body.matrix_world = curve.matrix_world.copy()
    curve.data.use_stretch = curve.data.use_deform_bounds = True
    modifier = body.modifiers.new("Reference curve", "CURVE")
    modifier.object, modifier.deform_axis = curve, "POS_X"
    result = dict(vertices=vertices, faces=faces, expected=evaluated(body))
    dispose(body)
    return result


def curve_case(source, shift=0):
    obj = clone_curve(source)
    obj.matrix_world.translation.x += shift
    bpy.context.view_layer.update()
    result = dict(
        name=source.name,
        owner=flat(obj.matrix_world),
        shift=shift,
        curve=curve_record(obj),
        hooks=[hook_record(m) for m in obj.modifiers],
        body=body_reference(obj),
    )
    result["samples"] = sampled(obj)
    dispose(obj)
    return result


def sampled(obj):
    modifier = obj.modifiers.new("Reference resample", "NODES")
    modifier.node_group = resample_nodes()
    return evaluated(obj)


def cage_case(cage):
    body, vertices, faces = body_object()
    body.matrix_world = cage.matrix_world.copy()
    modifier = body.modifiers.new("Reference lattice", "LATTICE")
    modifier.object = cage
    result = dict(cage_metadata(cage), vertices=vertices, faces=faces, expected=evaluated(body))
    dispose(body)
    return result


def cage_metadata(cage):
    data = cage.data
    return dict(
        name=cage.name,
        matrix=flat(cage.matrix_world),
        points=[list(p.co_deform) for p in data.points],
        resolution=[data.points_u, data.points_v, data.points_w],
        interpolation=[
            getattr(data, "interpolation_type_" + a).removeprefix("KEY_") for a in "uvw"
        ],
        outside=data.use_outside,
        hooks=[hook_record(m) for m in cage.modifiers if m.type == "HOOK"],
    )


def capture(source):
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    curves = [
        obj for obj in bpy.data.objects if obj.type == "CURVE" and obj.name.startswith(PREFIXES)
    ]
    cases = [curve_case(curve) for curve in curves]
    cases += shifted_connections(curves)
    cages = [
        cage_case(obj) for obj in bpy.data.objects if obj.type == "LATTICE" and "brow" in obj.name
    ]
    return dict(source_metadata(source), curves=cases, cages=cages)


def shifted_connections(curves):
    return [
        curve_case(curve, 5)
        for curve in curves
        if "clavicle" in curve.name or "acromion" in curve.name
    ]


def source_metadata(source):
    with source.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return dict(source=str(source), sha256=digest)


def main():
    arguments = sys.argv[sys.argv.index("--") + 1 :]
    data = capture(Path(arguments[0]))
    data.update(blender=bpy.app.version_string, build=bpy.app.build_hash.decode())
    Path(arguments[1]).write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Captured {len(data['curves'])} curves and {len(data['cages'])} cages")


if __name__ == "__main__":
    main()
