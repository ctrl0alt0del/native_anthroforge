"""Two-side assembly preserves production compaction, disabled sides and material labels."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import tissue_domain, tissue_parts
from tests.test_tissue_branches import CASES as BRANCHES
from tests.test_tissue_branches import inputs

CASES = json.loads((Path(__file__).parent / "fixtures/tissue/envelopes.json").read_text())["cases"]
CORRECTED = json.loads(
    (Path(__file__).parent / "fixtures/tissue/distributed_correction.json").read_text()
)["envelopes"]


def side(source, parts, reverse, disabled):
    if disabled:
        parts = tuple(
            replace(p, a=replace(p.a, inflation=replace(p.a.inflation, enabled=False)))
            for p in parts
        )
    return tissue_parts.evaluate(source, parts, "a", reverse, envelope=True)


@pytest.mark.parametrize("row", CASES)
def test_corrected_envelope_keeps_zero_sides_and_exact_material_sources(session, row):
    source, parts = inputs(session, BRANCHES[row["source"]])
    first = side(source, parts, False, row["disabled"] in ("a", "both"))
    second = side(source, parts, True, row["disabled"] in ("b", "both"))
    result = tissue_parts.compose(first, second, False)
    expected = CORRECTED[f"{row['source']}:{row['disabled']}"]
    np.testing.assert_allclose(result.array(0), expected, atol=1e-10, rtol=0)
    np.testing.assert_array_equal(result.array(1), np.asarray(row["faces"]).ravel())
    records, weights = tissue_domain.arrays(result)
    assert records[1] == 5 and np.all(weights == 1)
    np.testing.assert_array_equal(records[-len(row["faces"]) :], row["origins"])
