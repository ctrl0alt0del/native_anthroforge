"""Run in Blender background to pin the addon's four finite radial unit meshes."""

import hashlib
import json
import sys
from pathlib import Path

import bmesh
import bpy


def sphere(level):
    mesh = bmesh.new()
    try:
        bmesh.ops.create_icosphere(mesh, subdivisions=level, radius=1.0)
        mesh.verts.ensure_lookup_table()
        mesh.verts.index_update()
        points = [tuple(v.co) for v in mesh.verts]
        faces = [tuple(v.index for v in f.verts) for f in mesh.faces]
        return points, faces
    finally:
        mesh.free()


def table(kind, name, rows):
    text = ",\n".join("{" + ",".join(map(repr, row)) + "}" for row in rows)
    return f"static const {kind} {name}[][3] = {{\n{text}\n}};\n"


def main():
    destination = Path(sys.argv[sys.argv.index("--") + 1])
    text = "// SPDX-License-Identifier: GPL-3.0-or-later\n"
    text += "// Blender bmesh unit icospheres; regenerate with capture_tissue_spheres.py.\n"
    for level in range(1, 5):
        points, faces = sphere(level)
        text += table("double", f"sphere_{level}_points", points)
        text += table("int64_t", f"sphere_{level}_faces", faces)
    destination.write_bytes(text.encode())
    provenance = dict(
        blender=bpy.app.version_string, sha256=hashlib.sha256(text.encode()).hexdigest()
    )
    destination.with_suffix(".json").write_text(json.dumps(provenance, indent=2) + "\n")


if __name__ == "__main__":
    main()
