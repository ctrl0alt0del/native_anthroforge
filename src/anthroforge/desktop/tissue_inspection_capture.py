"""Reproduce an inspection view in the isolated renderer, from its frozen revision."""

from . import tissue_finding_view


def restore(controller, settings):
    if not settings:
        return
    tool = controller.tissue_inspection
    tool.synchronize()
    tool.set_view(settings["stage"], settings["reference"], settings["mode"])
    controller.session.wait()
    restore_point(controller, settings.get("point"))
    tool.synchronize()
    finding = settings.get("finding")
    if finding:
        tool.lines = tissue_finding_view.lines(
            controller.session, finding, finding["evidence"]["witness"]
        )
        tool.changed.emit()


def restore_point(controller, point):
    if not point:
        return
    controller.session.command(
        "tissue.inspect.point",
        target=point["target"],
        stage=point["stage"],
        triangle=point["triangle"],
        weights=point["weights"],
        expected_asset=point["asset"],
    )
    controller.session.wait()
