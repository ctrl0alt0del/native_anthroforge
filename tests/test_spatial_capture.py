"""Exports retain the displayed diagnostic revision; idle panels do no geometry work."""

from anthroforge.application import inspection_report, inspection_spatial_capture
from anthroforge.desktop.capture import restore_spatial
from tests.test_mesh_replacement import source
from tests.test_tissue_interaction import controller as controller


def measure(controller, target):
    controller.refresh()
    controller.select(target)
    controller.section_tools.enable(True)
    controller.section_tools.request()
    controller.surface_measurements.show(target, "final")
    controller.surface_measurements.submit()
    controller.surface_measurements.volumes.compare(target, "final", target, "SCP")
    controller.session.wait()
    controller.section_tools.synchronize()
    controller.surface_measurements.synchronize()


def test_capture_restores_section_axes_volume_and_neighborhood(controller):
    session = controller.session
    target = source(session)
    measure(controller, target)
    controller.neighborhood.inspect()
    frozen = freeze(controller, target)
    assert frozen.view["section"]["plane"] == controller.section_tools.plane
    controller.section_tools.cancel()
    controller.surface_measurements.cancel()
    controller.neighborhood.restore()
    restore_spatial(controller, frozen.view)
    assert controller.section_tools.reports
    assert controller.surface_measurements.report["section"]["available"]
    assert controller.surface_measurements.volumes.report["boundary"] == 8
    assert target in controller.neighborhood.members


def freeze(controller, target):
    frozen = inspection_report.capture(controller.session, target, False)
    inspection_spatial_capture.capture(
        controller.session, frozen, controller.inspection_export.spatial_options()
    )
    return frozen


def test_stable_measurements_reuse_projection_and_do_not_requeue(controller, monkeypatch):
    target = source(controller.session)
    measure(controller, target)
    controller.surface_measurements.timer.stop()
    jobs = tuple(controller.session.scheduler.jobs)
    monkeypatch.setattr("anthroforge.application.inspection_surfaces.get", forbidden)
    for _ in range(100):
        controller.surface_measurements.synchronize()
    assert tuple(controller.session.scheduler.jobs) == jobs


def forbidden(*args, **kwargs):
    raise AssertionError("Stable views must not rebuild accepted surface projections.")
