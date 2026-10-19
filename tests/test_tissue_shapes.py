"""Production-addon fixtures qualify native shell and sweep geometry and connectivity."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.tissue_settings import TissueInflation
from anthroforge.native import tissue_domain, tissue_shapes

CASES = json.loads((Path(__file__).parent / "fixtures/tissue/shapes.json").read_text())["cases"]


def shell(session, row):
    faces = row["faces"]
    base = session.engine.create_mesh(
        row["points"], np.array(faces).ravel(), np.arange(len(faces) + 1) * 4
    )
    spec = row["settings"]
    settings = TissueInflation(
        mode="NORMAL",
        amount=spec["max_thickness"],
        minimum=spec["min_thickness"],
        power=spec["thickness_power"],
    )
    return tissue_shapes.normal(base, settings, () if row["custom"] is None else row["custom"])


def sweep(session, row, disabled=False):
    samples = np.zeros((len(row["points"]), 11))
    samples[:, :3], samples[:, 6:9] = row["points"], row["normals"]
    spec = row["settings"]
    settings = TissueInflation(
        mode="PROFILE",
        amount=spec["depth"],
        width=spec["half_width"],
        power=spec["profile_power"],
        segments=spec["profile_segments"],
        endpoint_taper=spec["endpoint_taper"],
    )
    return tissue_shapes.sweep(
        session.engine, samples, spec["cyclic"], replace(settings, enabled=not disabled)
    )


@pytest.mark.parametrize("row", CASES)
def test_native_shapes_match_addon_outputs_and_canonical_polygons(session, row):
    result = shell(session, row) if row["kind"] == "NORMAL" else sweep(session, row)
    np.testing.assert_allclose(result.array(0), row["output"]["vertices"], atol=1e-12, rtol=0)
    faces = row["output"]["faces"]
    np.testing.assert_array_equal(result.array(1), [i for face in faces for i in face])
    np.testing.assert_array_equal(result.array(2), np.cumsum([0, *map(len, faces)]))
    domain, _ = tissue_domain.arrays(result)
    assert domain[1] == (3 if row["kind"] == "NORMAL" else 2)


def test_disabled_curve_keeps_canonical_connectivity_and_finite_geometry(session):
    enabled, disabled = sweep(session, CASES[3]), sweep(session, CASES[3], True)
    np.testing.assert_array_equal(enabled.array(3), disabled.array(3))
    assert np.isfinite(disabled.array(0)).all()
    assert not np.array_equal(enabled.array(0), disabled.array(0))


@pytest.mark.parametrize(
    "resolution,vertices,faces", [(3, 12, 20), (24, 42, 80), (64, 162, 320), (128, 642, 1280)]
)
def test_radial_uses_blender_subdivision_thresholds(session, resolution, vertices, faces):
    settings = TissueInflation(mode="RADIAL", amount=0.1, scale=(1, 2, 3))
    result = tissue_shapes.radial(session.engine, np.eye(4).ravel(), settings, resolution)
    assert result.counts[:2] == (vertices, faces)
    norms = np.linalg.norm(result.array(0) / [0.1, 0.2, 0.3], axis=1)
    # Blender's unsubdivided ico seed is rounded; preserve it rather than normalize.
    np.testing.assert_allclose(norms, 1, atol=1.2e-5, rtol=0)


def test_radial_tables_are_pinned_to_blender_source_capture():
    root = Path(__file__).resolve().parents[1] / "native/migration/tissue/unit_spheres"
    import hashlib

    metadata = json.loads(root.with_suffix(".json").read_text())
    assert metadata["blender"] == "5.0.1"
    assert hashlib.sha256(root.with_suffix(".hpp").read_bytes()).hexdigest() == metadata["sha256"]
