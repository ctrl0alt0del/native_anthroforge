import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from anthroforge.core.construction import Deformer, Target
from anthroforge.core.shrinkwrap import Shrinkwrap
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.native.mesh import GeometryEngine
from anthroforge.native.shrinkwrap import deform

REFERENCE = json.loads(
    (Path(__file__).parent / "fixtures/primitives/blender501_shrinkwrap.json").read_text()
)


@pytest.fixture(scope="module")
def target_mesh():
    engine = GeometryEngine()
    return engine.create_mesh(REFERENCE["vertices"], [0, 1, 2, 0, 2, 3], [0, 3, 6])


@pytest.mark.parametrize("case", REFERENCE["cases"])
def test_nearest_surface_matches_blender_501(target_mesh, case):
    settings = Shrinkwrap(SurfaceReference("target"), case["offset"], case["mode"])
    binding = Deformer(
        "SHRINKWRAP", "", Target("source"), weights=tuple(case["weights"]), shrinkwrap=settings
    )
    provider = SimpleNamespace(frame=case["target"], resource=SimpleNamespace(mesh=target_mesh))
    result = deform(target_mesh.engine, case["points"], binding, case["owner"], provider, 0)
    np.testing.assert_allclose(result, case["expected"], atol=2e-6)
