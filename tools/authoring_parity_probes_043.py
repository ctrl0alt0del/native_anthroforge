"""Observe UI/JSON differences in disposable sessions; do not repair production state."""

import json
import os
from contextlib import closing
from pathlib import Path
from threading import Event

from PySide6.QtCore import QCoreApplication

from anthroforge import authoring
from anthroforge.application.session import Session
from anthroforge.core.fibers import Fiber
from anthroforge.desktop import curve_context, skin_contributor
from anthroforge.desktop.controller import Controller

OUTPUT = Path(__file__).resolve().parents[1] / "build/authoring-parity-043"


def moved_fiber(session):
    cube = OUTPUT.parents[1] / "examples/primitives/cube.obj"
    target = session.command("import", path=str(cube), units=1.0)["entity_id"]
    session.wait()
    points = [dict(position=p) for p in [[-0.4, 0, 0.7], [0, 0.25, 0.8], [0.4, 0, 0.7]]]
    curve = session.command("curve.create", points=points)
    session.wait()
    session.command("fiber.create", curve=curve)
    session.wait()
    fiber = next(item.id for item in session.document.objects if isinstance(item, Fiber))
    session.command("scp.transform", entity=target, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    session.wait()
    return target, fiber


def literal_names():
    with closing(Controller()) as controller:
        controller.timer.stop()
        identity = controller.run("scp.empty", {"name": "$pelvis"})
        ui = controller.session.document.entity(identity).name
    with closing(Session()) as session:
        request = dict(operation="scp.empty", arguments=dict(name="$pelvis"))
        response = authoring.response(session, request, {})
    return dict(ui_name=ui, json_response=response, gap=not response["ok"])


def current_shape():
    with closing(Controller()) as controller:
        controller.timer.stop()
        _, fiber = moved_fiber(controller.session)
        controller.refresh()
        controller.select(fiber)
        return point_observation(controller, fiber)


def point_observation(controller, fiber):
    before = controller.session.document
    item = curve_context.owner(controller.authoring)
    public = controller.session.command("object.inspect", target=fiber)["state"]
    ui_points = [list(p.position) for p in item.points]
    api_points = [list(p["position"]) for p in public["points"]]
    assert before is controller.session.document
    assert item.result.status == "ready", item.result.error
    return dict(
        ui_points=ui_points,
        public_authored_points=api_points,
        gap=ui_points != api_points,
        mutation=False,
    )


def recovery_copy():
    with closing(Controller()) as controller:
        controller.timer.stop()
        session = controller.session
        session.command("scp.empty", name="Recovery audit")
        store = controller.project_library.autosave.store
        record = store.write(session.document, session.resources, "", Event())
        session.command("open", path=record["path"])
        public = ownership(session)
        controller.project_library.opened(
            Path(record["path"]), session.file_lock, session.document.revision
        )
        desktop = ownership(session)
        return dict(public_open=public, desktop_recovery=desktop, gap=public != desktop)


def ownership(session):
    return dict(
        path=str(session.path) if session.path else None,
        locked=session.file_lock is not None,
        saved_revision=session.saved_revision,
    )


def effective_skin_settings():
    with closing(Session()) as session:
        target = session.command("scp.empty", name="Nasal cartilage")
        session.command("skin.configure", section="envelope_settings", values={"gap_strength": 0.4})
        public = session.command("skin.inspect")
        ui = skin_contributor.describe(session, target)
        return dict(
            public_contributors=public["contributors"],
            ui_authored_defaults=ui["settings"],
            ui_effective=ui["effective"],
            observation="Effective AUTO/INHERIT values use an internal helper, not skin.inspect.",
        )


def uncommitted_preview():
    with closing(Session()) as session:
        points = [dict(position=p) for p in ((-0.5, 0, 0), (0, 1, 0), (0.5, 0, 0))]
        curve = session.command("curve.create", points=points)
        session.wait(5)
        before = session.document
        session.command("curve.conversion.preview", curve=curve, engine="POLYLINE", samples=12)
        session.wait(5)
        assert session.document is before
        return preview_observation(session)


def preview_observation(session):
    public = session.command("curve.conversion.status")
    assert public["state"] == "ready", public
    return dict(
        public_status=public,
        ui_path_samples=session.conversion.asset.path.count,
        observation="Desktop reads the candidate path; status carries no path/image.",
    )


def main():
    os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(OUTPUT / "preferences.json")
    app = QCoreApplication.instance() or QCoreApplication([])
    result = dict(literal_names=literal_names(), current_shape=current_shape())
    result["recovery"] = recovery_copy()
    result["skin_settings"] = effective_skin_settings()
    result["uncommitted_preview"] = uncommitted_preview()
    result["limitations"] = "Model/API observations; no physical desktop interaction."
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "behavioral-probes.json").write_text(json.dumps(result, indent=2), "utf-8")
    print(json.dumps(result))
    assert app


if __name__ == "__main__":
    main()
