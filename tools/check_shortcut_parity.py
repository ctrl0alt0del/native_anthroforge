"""Compare native kernels against captured real Pubis/Cheekbone addon evaluations."""

import json
import sys
from dataclasses import replace
from pathlib import Path
from threading import Event

import numpy as np

from anthroforge.core.construction import BodyPiece, Primitive
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.entities import SCP, Attachment
from anthroforge.native.attachments import propagate
from anthroforge.native.mesh import GeometryEngine
from anthroforge.native.shortcut_attachments import backsolve


def mesh(engine, data):
    faces = data["faces"]
    return engine.create_mesh(
        data["vertices"], [i for f in faces for i in f], np.cumsum([0, *map(len, faces)])
    )


def prepare(engine, case):
    data = case["changed"]
    meshes = {key: mesh(engine, data[key + "_mesh"]) for key in ("parent", "child")}
    parent = SCP("Parent", asset="parent", matrix=tuple(data["parent"]))
    child = SCP(
        "Child",
        asset="child",
        parent=parent.id,
        matrix=tuple(data["child"]),
        attachment=Attachment(binding=tuple(case["binding"])),
    )
    return parent, child, meshes


def check_cheekbone(engine, case):
    parent, child, meshes = prepare(engine, case)
    snapshot = case["snapshot"]
    retained = (
        snapshot["anchor_mode"],
        snapshot["anchor_index"],
        snapshot["anchor_local"],
        snapshot["parent_local"],
    )
    actual = backsolve(engine, child, parent, meshes, retained)
    return compare(actual, case)


def check_pubis(engine, case):
    parent, child, meshes = prepare(engine, case)
    primitive = Primitive("BODY", curves=(CurveUse("guide"),), pieces=(BodyPiece("guide"),))
    parent = replace(parent, primitive=primitive)
    child = replace(child, attachment=replace(child.attachment, strategy=case["strategy"]))
    actual = propagate(engine, [parent, child], meshes, {child.id}, Event())[1]
    assert actual.status == "ready", actual.error
    return compare(actual.matrix, case)


def compare(actual, case):
    assert case["applied"], "Reference did not exercise a changing pose"
    error = float(np.max(np.abs(np.asarray(actual) - case["expected"])))
    np.testing.assert_allclose(actual, case["expected"], atol=3e-5, rtol=0)
    return dict(max_matrix_error=error, tolerance=3e-5)


def run(path):
    data, engine = json.loads(path.read_text()), GeometryEngine()
    result = dict(
        sources=data["sources"],
        blender=data["blender"],
        pubis=check_pubis(engine, data["pubis"]),
        pubis_auto=check_pubis(engine, data["pubis_auto"]),
        cheekbone=check_cheekbone(engine, data["cheekbone"]),
    )
    path.with_suffix(".comparison.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run(Path(sys.argv[1]))
