"""Renderer staging and picking observe the same complete geometry revision."""

from types import SimpleNamespace

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.models import RenderModel


def publish(model, handle, chunks, x=0):
    rows = [
        dict(id="scp", key=f"scp:{handle}:{i}", handle=handle, chunk=i, x=x) for i in range(chunks)
    ]
    model.publish(rows, [SimpleNamespace(handle=handle)])


def initial_model():
    model = RenderModel()
    publish(model, 1, 1)
    model.drain()
    model.presented()
    model.presented()
    return model


def test_complete_geometry_and_picking_retained_until_replacement_is_presented():
    model = initial_model()
    publish(model, 2, 4)
    model.drain()
    model.presented()
    assert [row["handle"] for row in model.rows if row["active"]] == [1]
    model.drain()
    model.presented()
    assert {row["handle"] for row in model.rows if row["active"]} == {2}
    assert {row["handle"] for row in model.active_rows()} == {1}
    assert set(model.leases) == {1, 2}
    model.presented()
    assert {row["handle"] for row in model.active_rows()} == {2}
    assert set(model.leases) == {2}


def test_obsolete_staging_is_discarded_without_discarding_visible_geometry():
    model = initial_model()
    publish(model, 2, 6)
    model.drain()
    publish(model, 3, 3, x=2)
    assert {row["handle"] for row in model.rows} == {1}
    assert model.rows[0]["x"] == 2
    assert set(model.leases) == {1, 3}
    model.drain()
    model.presented()
    assert {row["handle"] for row in model.active_rows()} == {1}
    model.drain()
    model.presented()
    model.presented()
    assert {row["handle"] for row in model.active_rows()} == {3}


def presentation_controller(models, snapshots):
    metrics = SimpleNamespace(observe=lambda *args: None)
    controller = SimpleNamespace(
        session=SimpleNamespace(scheduler=SimpleNamespace(metrics=metrics)),
        _presenting=False,
        _geometry_dirty=False,
        last_frame=0,
    )
    controller.geometry_models = lambda: models
    controller.publish_displayed = lambda: snapshots.append([m.active_rows() for m in models])
    controller.activate_geometry = lambda: Controller.activate_geometry.__wrapped__(controller)
    for model in models:
        model.activated.connect(controller.activate_geometry)
    return controller


def test_multiple_model_notifications_publish_one_coherent_displayed_frame():
    models, snapshots = [initial_model(), initial_model()], []
    controller = presentation_controller(models, snapshots)
    for model in models:
        publish(model, 2, 1)
        model.drain()
    Controller.frame_presented(controller)
    assert len(snapshots) == 1
    assert [rows[0]["handle"] for rows in snapshots[0]] == [1, 1]
    Controller.frame_presented(controller)
    assert len(snapshots) == 2
    assert [rows[0]["handle"] for rows in snapshots[1]] == [2, 2]
    controller.activate_geometry()
    assert len(snapshots) == 3
