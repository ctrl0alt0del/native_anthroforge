"""Adaptive correspondence preserves crop coverage and opposite-side orientation."""

import numpy as np
import pytest

from anthroforge.core.tissue_settings import TissueCrop, TissuePart
from anthroforge.native import material_bindings, tissue_crop, tissue_parts
from tests.test_adaptive_material_frames import all_records, frames, loft
from tests.test_material_bindings import IDENTITY
from tests.test_tissue_envelopes import side


def sources(session):
    return [loft(session.engine, values) for values in ([0, 0.5, 1], [0, 0.2, 0.5, 0.8, 1])]


def envelope(base, disabled=False):
    parts = (TissuePart(),)
    return tissue_parts.compose(
        side(base, parts, False, disabled), side(base, parts, True, disabled), False
    )


def test_adaptive_compacted_envelope_keeps_opposite_side_offset_and_frame(session):
    before, after = sources(session)
    original, collapsed = envelope(before), envelope(after, disabled=True)
    rows = all_records(original)
    rows = rows[frames(original, rows)[:, 10] < 0]
    assert len(rows)
    resolved = material_bindings.frames(original, collapsed, IDENTITY, rows)
    np.testing.assert_allclose(resolved[:, 10], -1, atol=1e-10)
    np.testing.assert_allclose(resolved[:, 11], -0.04, atol=1e-10)


def test_adaptive_crop_resolves_retained_locations_but_rejects_removed_material(session):
    before, after = sources(session)
    first, second = [tissue_parts.evaluate(m, (TissuePart(),), "a", False) for m in (before, after)]
    crop = TissueCrop(enabled=True, origin=(0.2, 0, 0), normal=(1, 0, 0))
    clipped = tissue_crop.evaluate(before, first, crop)
    rows = all_records(clipped)
    assert np.isfinite(material_bindings.frames(clipped, second, IDENTITY, rows)).all()
    missing = tissue_crop.evaluate(after, second, TissueCrop(True, (100, 0, 0)))
    with pytest.raises(ValueError, match="outside the current surface"):
        material_bindings.frames(clipped, missing, IDENTITY, rows)
