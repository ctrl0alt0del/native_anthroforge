from tests.test_assembly_resources import prepare_source
from tests.test_tissue_interaction import controller as controller


def inspect(controller, tmp_path):
    curve, path, _ = prepare_source(controller.session, tmp_path)
    panel = controller.assembly_panel
    panel.inspect(str(path))
    controller.session.wait()
    panel.synchronize()
    assert panel.constructionModel.rowCount() > 0
    return panel, curve


def test_desktop_selection_prepares_automatically_and_imports_once(controller, tmp_path):
    panel, curve = inspect(controller, tmp_path)
    before = controller.session.document.objects
    panel.construction.choose(curve.id, True)
    assert panel.timer.isActive()
    panel.timer.stop()
    panel.prepare()
    controller.session.wait()
    panel.synchronize()
    assert panel.state["ready"], panel.state
    panel.apply()
    assert len(controller.session.document.objects) == len(before) + 1
    controller.session.command("undo")
    assert controller.session.document.objects == before


def test_idle_panel_does_not_rebuild_source_inventory(controller, tmp_path, monkeypatch):
    panel, _ = inspect(controller, tmp_path)

    def fail():
        raise AssertionError("Idle import state must not be polled and rebuilt")

    monkeypatch.setattr(controller.session.assembly, "status", fail)
    for _ in range(20):
        panel.synchronize()


def test_reference_repair_keeps_mirrored_target_selection_visible():
    from anthroforge.core.assembly import ExternalReference, ReferenceUse
    from anthroforge.desktop.assembly_projection import pending_row

    use = ReferenceUse("receiver", "stacking", "final", "TISSUE_FINAL")
    reference = ExternalReference(
        "ref", "document", "source", 1, "Tissue", "TISSUE", (use,), source_instance="rule"
    )
    row = pending_row(reference, dict(action="map", target="provider", instance="plane"))
    assert row["name"] == "Tissue · mirrored"
    assert row["target"] == "provider" and row["target_instance"] == "plane"
