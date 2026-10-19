"""Inflation parity uses actual addon outputs, not a Python production fallback."""

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from time import sleep

import numpy as np
import pytest

from anthroforge.core.tissue_settings import SectionProfile, TissueInflation
from anthroforge.native import material, tissue_inflation
from anthroforge.native.mesh import NativeCancellation

FIXTURE = Path(__file__).parent / "fixtures/tissue/inflation.json"


def settings(data):
    return TissueInflation(**dict(data, profile=SectionProfile(**data["profile"])))


def grid_mesh(engine, points):
    grid = np.asarray(points)
    rows, columns, _ = grid.shape
    faces = [
        (i * columns + j, (i + 1) * columns + j, (i + 1) * columns + j + 1, i * columns + j + 1)
        for i in range(rows - 1)
        for j in range(columns - 1)
    ]
    mesh = engine.create_mesh(
        grid.reshape(-1, 3), np.array(faces).ravel(), np.arange(len(faces) + 1) * 4
    )
    return material.restore(mesh, [rows, columns, 0, 0, rows * columns, *range(rows * columns)])


@pytest.mark.parametrize("case", json.loads(FIXTURE.read_text())["cases"], ids=lambda x: x["name"])
def test_native_inflation_matches_addon(session, case):
    source = grid_mesh(session.engine, case["points"])
    output = tissue_inflation.evaluate(source, settings(case["settings"]), case["reverse"])
    np.testing.assert_allclose(output.array(0), np.array(case["output"]).reshape(-1, 3), atol=1e-12)
    np.testing.assert_array_equal(source.array(0), np.array(case["points"]).reshape(-1, 3))
    np.testing.assert_array_equal(output.array(3), source.array(3))
    np.testing.assert_array_equal(material.array(output), material.array(source))


def test_profile_rejects_closed_material_axis_without_altering_input(session):
    case = json.loads(FIXTURE.read_text())["cases"][-1]
    source = grid_mesh(session.engine, case["points"])
    domain = material.array(source)
    domain[2] = 1
    closed = material.restore(source, domain)
    with pytest.raises(ValueError, match="ordinary open loft"):
        tissue_inflation.evaluate(closed, settings(case["settings"]))
    np.testing.assert_array_equal(closed.array(0), source.array(0))


def test_zero_amount_does_not_disable_section_profile(session):
    case = json.loads(FIXTURE.read_text())["cases"][-1]
    source = grid_mesh(session.engine, case["points"])
    value = replace(settings(case["settings"]), amount=0)
    output = tissue_inflation.evaluate(source, value)
    np.testing.assert_allclose(output.array(0), np.array(case["output"]).reshape(-1, 3), atol=1e-12)


def test_profile_cancels_inside_the_native_kernel(session):
    case = json.loads(FIXTURE.read_text())["cases"][-2]
    source = tissue_inflation.refine(grid_mesh(session.engine, case["points"]), 256)
    cancel = NativeCancellation(session.engine)
    with ThreadPoolExecutor(1) as executor:
        task = executor.submit(
            tissue_inflation.evaluate, source, settings(case["settings"]), False, cancel.handle
        )
        sleep(0.02)
        assert not task.done(), "Fixture must exercise an active native computation."
        cancel.set()
        with pytest.raises(ValueError, match="[Cc]ancel"):
            task.result(timeout=2)


def test_pinned_kernel_ranges_retain_source_bytes():
    import hashlib

    directory = Path(__file__).parents[1] / "native/migration/tissue"
    for record in json.loads((directory / "sources.json").read_text()):
        assert (
            hashlib.sha256((directory / record["file"]).read_bytes()).hexdigest()
            == record["sha256"]
        )
