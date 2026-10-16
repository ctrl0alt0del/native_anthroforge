"""Blender 5.0.1 reference matrices: 72 mode/follow/scale combinations."""

import json
from dataclasses import replace
from pathlib import Path
from threading import Event

import numpy as np
import pytest

from anthroforge.core.entities import SCP, Attachment
from anthroforge.native.attachments import capture, propagate

REFERENCE = json.loads((Path(__file__).parent / "fixtures/addon_attachments.json").read_text())


@pytest.fixture
def reference_mesh(session):
    faces = np.array(REFERENCE["faces"], dtype=np.int64)
    return session.engine.create_mesh(REFERENCE["vertices"], faces.ravel(), np.arange(5) * 3)


@pytest.mark.parametrize("case", REFERENCE["cases"])
def test_attachment_matches_blender_reference(session, reference_mesh, case):
    engine, meshes = session.engine, {"mesh": reference_mesh}
    parent = SCP("Parent", asset="mesh", matrix=tuple(case["initial"]["parent"]))
    child = SCP(
        "Child",
        parent=parent.id,
        asset="mesh",
        matrix=tuple(case["initial"]["child"]),
        attachment=Attachment(**case["settings"]),
    )
    child = capture(engine, child, parent, meshes)
    parent = replace(parent, matrix=tuple(case["target"]))
    actual = propagate(engine, [parent, child], meshes, {child.id}, Event())[1]
    assert actual.matrix == pytest.approx(case["expected"], abs=3e-5)
