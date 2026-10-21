"""Saved-revision captures drain every staged resource before drawing the final view."""

from types import SimpleNamespace

from anthroforge.desktop.capture import stage_geometry
from anthroforge.desktop.models import RenderModel


def prepared(count):
    model = RenderModel()
    model.publish([dict(id="image", key=str(i), handle=0, chunk=i) for i in range(count)])
    return model


def test_capture_drains_paths_and_large_images_without_any_meshes():
    models = [prepared(count) for count in (0, 7, 64, 9)]
    controller = SimpleNamespace(
        render_model=models[0],
        path_model=models[1],
        image_model=models[2],
        geometry_models=lambda: models,
        frame_presented=lambda: [model.presented() for model in models],
    )
    stage_geometry(
        SimpleNamespace(processEvents=lambda: None), controller, SimpleNamespace(frame=lambda: None)
    )
    assert not any(model.pending for model in models)
    assert [len(model.rows) for model in models] == [0, 7, 64, 9]
    assert all(row["active"] for model in models for row in model.rows)
