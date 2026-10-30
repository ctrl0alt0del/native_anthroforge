"""A visible startup window does not establish that a large project has opened."""

from types import SimpleNamespace

from anthroforge.desktop.smoke import ready


def controller():
    return SimpleNamespace(
        project_view=SimpleNamespace(pending_document=None),
        session=SimpleNamespace(waiting_save=False, scheduler=SimpleNamespace(active_jobs=[])),
        geometry_models=lambda: [],
    )


def test_smoke_waits_for_document_and_scheduled_work():
    value = controller()
    assert ready(value)
    value.project_view.pending_document = "assembly.anthroforge"
    assert not ready(value)
    value.project_view.pending_document, value.session.waiting_save = None, True
    assert not ready(value)
    value.session.waiting_save, value.session.scheduler.active_jobs = False, [object()]
    assert not ready(value)


def test_smoke_waits_for_displayed_geometry():
    value = controller()
    model = SimpleNamespace(pending=[object()])
    value.geometry_models = lambda: [model]
    assert not ready(value)
    model.pending = []
    assert ready(value)
