"""Production stacking and routed-path witnesses rendered in the hidden qualification scene."""

from tissue_stacking_scene import prepare
from vcp_visual_scene import OUTPUT, frames


def stacking(controller, renderer, app):
    provider, target = prepare(controller)
    controller.tissue_inspection.showStacking(provider, "a", "a")
    controller.session.wait()
    frames(controller, renderer, app, "stacking-footprints")
    assert controller.tissue_inspection.stacking_status["state"] == "ready"
    assert controller.tissue_inspection.snapshot()["footprint"]
    controller.tissue_inspection.configure("final", "intrinsic", "Displacement")
    controller.session.wait()
    frames(controller, renderer, app, "stacking-displacement")
    export(controller, "stacking")


def route(controller, renderer, app):
    target = create_route(controller)
    controller.cameraRequested.emit([0, 0, 0, -35, -25, 0, 2.3], True)
    controller.route_inspection.start(True)
    controller.session.wait()
    frames(controller, renderer, app, "route-final")
    route_steps(controller, renderer, app, target)


def create_route(controller):
    session = controller.session
    session.command("import", path="examples/primitives/cube.obj", units=1)
    session.wait()
    target = session.command(
        "curve.create",
        engine="ROUTED",
        points=[dict(position=[-0.8, 0, 0]), dict(position=[0.8, 0, 0])],
    )
    session.wait()
    controller.refresh()
    controller.select(target)
    return target


def route_steps(controller, renderer, app, target):
    tool = controller.route_inspection
    assert tool.report["success"], tool.state
    tool.select(next(i for i, r in enumerate(tool.report["records"]) if r["stage"] == "Planner"))
    frames(controller, renderer, app, "route-planner")
    tool.select(
        max(range(len(tool.labels)), key=lambda i: len(tool.report["records"][i]["contacts"]))
    )
    frames(controller, renderer, app, "route-contacts")
    export(controller, "route")
    failure(controller, renderer, app, target)


def failure(controller, renderer, app, target):
    session = controller.session
    point = session.document.object(target).points[0].id
    session.command("curve.point.update", curve=target, point=point, position=[0, 0, 0])
    session.wait()
    controller.refresh()
    controller.route_inspection.start(True)
    session.wait()
    frames(controller, renderer, app, "route-failure")
    assert not controller.route_inspection.report["success"]
    export(controller, "route-failure")


def export(controller, name):
    options = controller.inspection_export.options(str(OUTPUT / (name + ".afinspection.zip")))
    controller.session.command("inspection.export", **options, wait=True)
