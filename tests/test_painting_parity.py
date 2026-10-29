"""Shared service returns the unmodified native effect across existing brush modes."""

import numpy as np
import pytest

from anthroforge.application import skin_painting, tissue_painting
from anthroforge.application.inspection_context import freeze
from anthroforge.core.entities import IDENTITY
from tests.test_painting_system import painting_case as painting_case
from tests.test_tissue_painting import setup
from tests.test_tissue_painting_native import VIEW


@pytest.mark.parametrize(
    "perspective,through,dense", [(0, False, False), (1, False, True), (1, True, False)]
)
def test_native_effect_matches_shared_candidate(
    session, painting_case, perspective, through, dense
):
    options = dict(painting_case)
    options["view"] = (*VIEW[:-1], perspective)
    options["brush"] = [100, 0.7, 0.4, 2.3, through]
    options["samples"] = [[x, 0] for x in range(-30, 31)] if dense else [[-30, 0], [30, 0]]
    options["obstacles"] = [dict(asset=next(iter(session.assets)), frame=IDENTITY)]
    verify(session, options)


def verify(session, options):
    case = dict(options)
    consumer, target = case.pop("consumer"), case.pop("target")
    adapter = skin_painting if consumer == "collagen" else tissue_painting
    case.setdefault("stage", "final")
    expected = adapter.compute(freeze(session), target, case, 0)["resource"].values.copy()
    before = session.document
    token = session.command("painting.preview", **options)["token"]
    session.wait()
    actual = session.command("painting.result", token=token)["values"]
    np.testing.assert_array_equal(actual, expected)
    assert session.document is before


@pytest.mark.parametrize("domain", ["BASE", "REST"])
def test_material_domain_is_preserved(session, domain):
    target = setup(session, domain)
    verify(
        session,
        dict(
            consumer="tissue_weights",
            target=target,
            name="paint",
            stage="rest",
            view=VIEW,
            samples=[[0, 0]],
            brush=[300, 0.3, 0.6, 0.5, True],
        ),
    )
