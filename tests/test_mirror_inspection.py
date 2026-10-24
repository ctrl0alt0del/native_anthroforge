"""Instance inspection uses source stage resources and reflected evidence only."""

import numpy as np

from anthroforge.core.mirroring import MirrorInstance
from tests.test_stacking_inspection import inspect
from tests.test_tissue_stack_workflow import assembly


def mirrored_layers(session, shift=2):
    bone, first, second = assembly(session)
    session.command("mirror.configure", target=bone, enabled=True, shift=shift)
    session.wait()
    return bone, first, second, MirrorInstance(second, bone).id


def test_mirrored_stage_comparison_and_point_evidence_do_not_change_anatomy(session):
    bone, first, second, mirror = mirrored_layers(session)
    before = session.document
    session.command("tissue.inspect.compare", target=mirror, stage="rest", reference="base")
    session.wait()
    value = session.command("tissue.inspect.status", kind="comparison")
    assert value["state"] == "ready" and value["report"]["maximum"] > 0, value
    point_inspection(session, mirror)
    session.wait()
    value = session.command("tissue.inspect.status", kind="point")
    assert value["state"] == "ready", value
    assert value["report"]["target"] == mirror
    assert session.document is before


def point_inspection(session, target):
    session.command(
        "tissue.inspect.point",
        target=target,
        stage="intrinsic",
        triangle=0,
        weights=[0.2, 0.3, 0.5],
    )


def test_mirrored_geometry_findings_are_explicit_and_revision_qualified(session):
    from anthroforge.application.issues.tissue_geometry import NAME

    bone, first, second, mirror = mirrored_layers(session)
    assert (NAME, mirror + ":final") not in session.issues.repository.states
    session.command("tissue.inspect.check", target=mirror)
    session.wait()
    state = session.issues.repository.states[NAME, mirror + ":final"]
    assert state.status == "COMPLETE", state


def test_original_footprint_can_inspect_a_mirrored_final_provider(session):
    bone, first, second, mirror = mirrored_layers(session, shift=0)
    value = inspect(session, second, MirrorInstance(first, bone).id)
    assert value["state"] == "ready", value
    assert value["report"]["stages"][MirrorInstance(first, bone).id] == "final"


def test_mirror_footprint_is_reflected_source_evidence(session):
    bone, first, second, mirror = mirrored_layers(session, shift=2)
    source = inspect(session, second, first)
    other = MirrorInstance(first, bone).id
    value = inspect(session, mirror, other)
    assert value["state"] == "ready", value
    expected = np.asarray(source["report"]["lines"]) * [-1, 1, 1] + [4, 0, 0]
    np.testing.assert_allclose(value["report"]["lines"], expected)
    assert value["report"]["order"]["covering"] == mirror
