"""Support selection binds displayed material faces and never edits until accepted."""

import pytest

from anthroforge.native import tissue_regions
from tests.test_tissue_interaction import controller as controller
from tests.test_tissue_stack_workflow import assembly


def draft(controller):
    _, provider, target = assembly(controller.session)
    controller.refresh()
    controller.select(target)
    for _ in range(8):
        controller.render_model.drain()
        controller.frame_presented()
    tool = controller.tissue_region_tools
    tool.begin(dict(other=provider, mode="EXPLICIT", cover="SELF"))
    assert tool.state["active"], controller.message
    return target, tool


def pick(tool):
    tool.probe([0.013, 0.019, 2], [0, 0, -1], False)
    assert tool.hover and tool.outline
    tool.probe([0.013, 0.019, 2], [0, 0, -1], True)
    assert len(tool.selected) == 1


def test_region_hover_pick_cancel_and_accept_are_coherent(controller):
    target, tool = draft(controller)
    before, cursor = controller.session.document, controller.session.history.cursor
    pick(tool)
    assert controller.session.document == before
    selected = tool.selected.copy()
    tool.commit()
    controller.session.wait(30)
    assert (
        set(controller.session.document.object(target).stack_relationships[0].regions) == selected
    )
    assert controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    controller.session.wait(30)
    assert not controller.session.document.object(target).stack_relationships


def test_cancel_and_stale_draft_preserve_authored_relationships(controller):
    target, tool = draft(controller)
    before = controller.session.document
    pick(tool)
    tool.cancel()
    assert controller.session.document == before and not tool.outline
    provider = before.object(target).stack_plan.providers[0]
    tool.begin(dict(other=provider, mode="EXPLICIT"))
    controller.run("tissue.inflation", dict(target=target, changes=dict(amount=0.09)))
    assert tool.state["error"]
    with pytest.raises(ValueError, match="inputs changed"):
        tool.commit()
    assert not controller.session.document.object(target).stack_relationships


@pytest.mark.parametrize(
    "regions,topology", [([("missing", 0)], ""), ([("main", 999999)], ""), ([("main", 0)], "old")]
)
def test_headless_rejects_unavailable_material_faces_and_stale_topology(session, regions, topology):
    _, provider, target = assembly(session)
    with pytest.raises(ValueError, match="part|selection|topology"):
        session.command(
            "tissue.stacking.relationship",
            target=target,
            other=provider,
            mode="EXPLICIT",
            regions=regions,
            topology=topology,
        )
    assert not session.document.object(target).stack_relationships


def test_native_region_side_lookup_excludes_generated_rims(session):
    _, _, target = assembly(session)
    session.command("tissue.inflation", target=target, changes=dict(mode="NORMAL"))
    session.wait(30)
    item = session.document.object(target)
    mesh = session.assets[item.rest_result.asset].mesh
    assert tissue_regions.face(mesh, 0, "a") == (0, 0)
    assert tissue_regions.face(mesh, 0, "b") is None
    assert tissue_regions.face(mesh, mesh.counts[1] - 1, "a") is None
