"""Ambiguous groups are explicit, validated, cancellable and bounded for large selections."""

from anthroforge.application import surface_group_draft
from tests.test_branch_creation import branch, curve
from tests.test_point_placement import controller as controller
from tests.test_surface_grouping import ambiguous


def test_group_review_preserves_every_source_and_rejects_singleton_branch(session):
    keys = ambiguous(session)
    roles = {key: (0 if index < 2 else 1) for index, key in enumerate(keys)}
    good = surface_group_draft.review(session, keys, roles, {})
    assert good["valid"] and good["groups"][0]["boundary"] == keys[0]
    roles[keys[-1]] = 2
    bad = surface_group_draft.review(session, keys, roles, {})
    assert not bad["valid"] and "at least two" in bad["reason"]


def test_cancel_ambiguous_creation_is_read_only(controller):
    keys = ambiguous(controller.session)
    controller.refresh()
    before, cursor = controller.session.document, controller.session.history.cursor
    controller.surface_creation.request(keys, "AUTO")
    assert controller.surface_creation.state["curves"]
    controller.surface_creation.cancel()
    assert controller.session.document == before and controller.session.history.cursor == cursor


def test_changed_sources_cannot_commit_a_stale_group_dialog(controller):
    keys = ambiguous(controller.session)
    controller.refresh()
    tool = controller.surface_creation
    tool.request(keys, "AUTO")
    joint = controller.session.document.object(keys[-1]).points[0].junction
    controller.session.command("junction.remove", junction=joint)
    tool.accept()
    assert not tool.state["valid"] and tool.state["curves"]


def test_large_branch_selection_does_not_enumerate_all_partitions(session):
    source = session.command(
        "curve.create", engine="POLYLINE", points=[dict(position=[0, i, 0]) for i in range(102)]
    )
    keys = [source, curve(session), *(branch(session, source, i) for i in range(1, 101))]
    result = session.command("surface.grouping", curves=keys)
    assert result["ambiguous"] and len(result["plan"]["branches"]) == 1
    assert len(result["plan"]["branches"][0]["curves"]) == 100
