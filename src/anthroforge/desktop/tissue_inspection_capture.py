"""Reproduce an inspection view in the isolated renderer, from its frozen revision."""

from . import tissue_finding_view


def restore(controller, settings):
    if not settings:
        return
    tool = controller.tissue_inspection
    tool.synchronize()
    tool.set_view(settings["stage"], settings["reference"], settings["mode"])
    restore_stacking(controller, settings.get("stacking"))
    restore_paint(controller, settings.get("paint"))
    restore_section(controller, settings.get("section"))
    controller.session.wait()
    restore_point(controller, settings.get("point"))
    tool.synchronize()
    restore_finding(controller, settings.get("finding"))


def restore_finding(controller, finding):
    if finding:
        tool = controller.tissue_inspection
        tool.lines = tissue_finding_view.lines(
            controller.session, finding, finding["evidence"]["witness"]
        )
        tool.changed.emit()


def restore_stacking(controller, settings):
    if not settings:
        return
    options = settings["options"]
    controller.tissue_inspection.showStacking(
        options["other"], options.get("side", "a"), options.get("other_side", "a")
    )


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


def restore_paint(controller, settings):
    if not settings:
        return
    options = settings["options"]
    brush = controller.tissue_painting
    brush.begin(options["name"])
    controller.tissue_inspection.set_view(options["stage"], "", "Overlay")
    controller.session.command("tissue.inspect.paint", target=controller.selection, **options)
    controller.session.wait()
    brush.retain_preview()


def restore_section(controller, snapshot):
    if not snapshot:
        return
    settings, tool = snapshot["settings"], controller.section_tools
    for key in ("enabled", "target", "axis", "position", "flip", "cut"):
        setattr(tool, key, settings[key])
    tool.whole_scene = settings["wholeScene"]
    tool.reports = snapshot.get("report", {}).get("surfaces", [])
    tool.context = (
        id(controller.session.document),
        id(controller.tissue_inspection.model.displayed),
        tool.plane,
    )
    tool.changed.emit()
