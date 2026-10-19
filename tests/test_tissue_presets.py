"""Creation presets apply donor values and never impose anatomical evaluator types."""

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core import tissue_presets
from tests.test_anchor_operations import scene
from tests.test_fiber_creation import bind
from tests.test_surface_workflow import curve
from tests.test_tissue_workflow import assembly, mesh

DATA = json.loads((Path(__file__).parent / "fixtures/tissue/presets.json").read_text())["presets"]
INFLATION = {
    "inflation_amount": "amount",
    "minimum_amount": "minimum",
    "profile_width": "width",
    "profile_power": "power",
    "field_power": "power",
    "profile_segments": "segments",
    "endpoint_taper": "endpoint_taper",
}


def source(session, preset):
    if preset in ("LAYER", "POUCH", "CUSTOM"):
        return assembly(session)[1]
    parent, _, anchor = scene(session)
    return anchor.id if preset == "CLOSED_BULK" else bind(session, parent, curve(session, 0)).id


def verify_defaults(item, expected):
    inflation, relaxation = item.parts[0].a.inflation, item.relaxation
    assert inflation.mode == expected["inflation_mode"]
    assert relaxation.mode == expected["relaxation_mode"]
    for name, value in expected["values"]:
        if name in INFLATION:
            assert getattr(inflation, INFLATION[name]) == value
        elif name == "base_resolution":
            assert item.resolution == value
        else:
            assert getattr(relaxation, "slack" if name == "surface_slack" else name) == value
    assert [(r.mask, r.mode, r.strength) for r in item.constraints] == [
        tuple(r) for r in expected["attachments"]
    ]


@pytest.mark.parametrize("preset", DATA)
def test_preset_evaluates_with_actual_addon_defaults(session, preset):
    key = session.command("tissue.create", source=source(session, preset), preset=preset)
    session.wait()
    item = session.document.object(key)
    verify_defaults(item, DATA[preset])
    assert item.result.status == "ready", item.result.error
    assert not item.stacking
    assert np.isfinite(mesh(session, key)).all()
    if preset in ("LAYER", "POUCH"):
        base = session.assets[item.base_result.asset].mesh.array(0)
        np.testing.assert_array_equal(mesh(session, key)[len(base) :], base)


def test_classification_is_only_a_label_and_rejected_preset_creates_nothing(session):
    source_id = source(session, "RIM")
    before = session.document
    with pytest.raises(ValueError, match="compatible"):
        session.command("tissue.create", source=source_id, preset="POUCH")
    assert session.document == before
    key = session.command("tissue.create", source=source_id, preset="RIM")
    session.wait()
    original = asdict(session.document.object(key))
    session.command("tissue.configure", target=key, changes=dict(classification="MUSCLE"))
    session.wait()
    updated = asdict(session.document.object(key))
    for name in ("parts", "relaxation", "constraints", "stacking", "preset"):
        assert updated[name] == original[name]


def test_available_presets_follow_construction_capabilities(session):
    _, _, anchor = scene(session)
    assert [r["id"] for r in tissue_presets.available(anchor)] == [
        "MUSCLE",
        "CUSTOM",
        "CLOSED_BULK",
    ]
