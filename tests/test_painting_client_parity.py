"""Desktop input and authoring share candidates and authoritative edit restrictions."""

import numpy as np
import pytest

from anthroforge.core.mirroring import MirrorInstance
from anthroforge.desktop.tissue_inspection_capture import restore_paint
from tests.test_painting_system import painting_case as painting_case
from tests.test_skin_painting_view import brush as collagen
from tests.test_tissue_interaction import controller as controller
from tests.test_tissue_painting_view import brush as tissue
from tests.test_tissue_painting_view import preview


@pytest.mark.parametrize("factory", [tissue, collagen])
def test_desktop_and_authoring_return_identical_values(controller, factory):
    target, tool = factory(controller)
    preview(controller, tool)
    expected = tool.preview["resource"].values.copy()
    options = dict(tool.preview["options"])
    consumer = tool.domain.consumer
    tool.cancelStroke()
    state = controller.session.command(
        "painting.preview", consumer=consumer, target=target, **options
    )
    controller.session.wait()
    result = controller.session.command("painting.result", token=state["token"])
    np.testing.assert_array_equal(result["values"], expected)


def test_mirror_target_is_unavailable_without_starting_work(session, painting_case):
    options = dict(painting_case, target=MirrorInstance(painting_case["target"], "rule").id)
    before = session.document
    status = session.command("painting.describe", **options)
    assert not status["available"] and "read-only" in status["reason"]
    with pytest.raises(ValueError, match="read-only"):
        session.command("painting.begin", **options)
    assert session.document is before and not session.painting.active


def test_workspace_change_prevents_old_candidate_commit(session, painting_case):
    root = session.document.entities[0].id
    other = session.command("scp.empty", name="Other", parent=root)
    session.wait()
    state = session.command("painting.preview", **painting_case, samples=[[0, 0]])
    session.wait()
    session.command("workspace.create", name="Other", members=[other], children=False)
    before = session.document
    with pytest.raises(ValueError, match="workspace"):
        session.command("painting.commit", token=state["token"])
    assert session.document == before


def test_export_restore_uses_shared_candidate_and_is_cancellable(controller):
    _, tool = tissue(controller)
    preview(controller, tool)
    expected = tool.preview["resource"].values.copy()
    settings = dict(options=dict(tool.preview["options"]))
    tool.cancelStroke()
    before = controller.session.document
    restore_paint(controller, settings)
    np.testing.assert_array_equal(tool.preview["resource"].values, expected)
    assert controller.session.document == before and tool.token
    tool.cancelStroke()
    assert tool.preview is None
