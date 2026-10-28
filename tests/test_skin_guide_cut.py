"""Guide holes preserve addon depth/radius/centered-scale policy and source geometry."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import skin_annuli
from tools.check_skin_annuli import evaluate

ROOT = Path(__file__).parent / "fixtures/skin"
ROWS = json.loads((ROOT / "annuli.json").read_text())["cases"]
CUTS = json.loads((ROOT / "guide_cuts.json").read_text())


@pytest.mark.parametrize("cut", CUTS)
def test_guide_cut_faces_match_addon(session, cut):
    row = ROWS[cut["case"]]
    surface, _, annuli = evaluate(session.engine, row)
    plane = [0, 0, 0, 1, 0, 0] if cut["centered"] else None
    result = skin_annuli.cut_guides(surface, annuli, plane)
    np.testing.assert_array_equal(
        result.array(1).reshape(-1, 3), np.array(row["faces"])[cut["kept"]]
    )
    np.testing.assert_array_equal(result.array(0), row["vertices"])
    np.testing.assert_array_equal(surface.array(1).reshape(-1, 3), row["faces"])
