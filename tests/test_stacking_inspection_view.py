"""Related tissues share displayed-stage picking and frozen report provenance."""

from anthroforge.application import inspection_report
from tests.test_tissue_inspection_view import publish
from tests.test_tissue_interaction import controller as controller
from tests.test_tissue_stack_workflow import assembly


def setup(controller):
    _, provider, receiver = assembly(controller.session)
    controller.refresh()
    controller.select(receiver)
    tool = controller.tissue_inspection
    tool.showStacking(provider, "a", "a")
    controller.session.wait()
    publish(controller)
    return provider, receiver, tool


def test_stacking_evidence_displays_receiver_and_provider_with_matching_picks(controller):
    provider, receiver, tool = setup(controller)
    assert tool.stacking_status["state"] == "ready", tool.stacking_status
    assert tool.snapshot()["footprint"]
    assert set(tool.state["hiddenOwners"]) == {provider, receiver}
    for key in (provider, receiver):
        item = controller.session.document.object(key)
        assert controller.pick_rows[key]["geometry_asset"] == item.intrinsic_result.asset
    tool.hideStacking()
    publish(controller)
    assert not tool.snapshot()["footprint"] and provider not in tool.state["hiddenOwners"]


def test_frozen_stacking_report_keeps_order_and_material_footprint(controller):
    provider, receiver, tool = setup(controller)
    options = controller.inspection_export.options("build/stacking.afinspection.zip")
    snapshot = inspection_report.capture(controller.session, receiver, False, options["tissue"])
    evidence = snapshot.view["tissue"]["stacking"]
    assert evidence["options"]["other"] == provider
    assert evidence["report"]["active"] and evidence["report"]["lines"]
    tool.hideStacking()
    assert snapshot.view["tissue"]["stacking"] == evidence
