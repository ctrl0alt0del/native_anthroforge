"""Viewport adapter for accepted tissue stages and revision-qualified point evidence."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import tissue_inspection as inspection
from anthroforge.application import tissue_inspection_stages as stages
from anthroforge.core.tissues import TissueVCP

from . import stacking_inspection_view as stacking
from . import tissue_inspection_scene as scene
from .models import RenderModel
from .property_projection import PropertyProjection


class TissueInspectionTools(QObject):
    changed = Signal()
    findingsRequested = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.model = controller, RenderModel(controller)
        self.target, self.stage, self.reference, self.mode = "", "", "", "Overlay"
        self.armed, self.lines, self.finding = False, [], ""
        self.context, self.key, self.rows, self.point, self.summary = None, None, [], {}, {}
        self.refresh_stamp, self.point_status = None, dict(state="idle")
        self.stacking_status = dict(state="idle")
        self._state = PropertyProjection(self)
        self.model.activated.connect(self.activated)
        self.notify()

    @Property(QObject, constant=True)
    def geometry(self):
        return self.model

    @Property(QObject, constant=True)
    def state(self):
        return self._state

    def notify(self):
        self._state.synchronize(self.state_values())
        self.changed.emit()

    def state_values(self):
        row = scene.primary(self)
        return dict(
            self.evidence_state(),
            target=self.target,
            stage=self.stage,
            reference=self.reference,
            mode=self.mode,
            active=self.armed,
            hiddenOwner=row["owner"] if row else "",
            hiddenOwners=scene.hidden_owners(self),
            stages=self.rows,
        )

    def evidence_state(self):
        return dict(
            point=self.point,
            comparison=self.summary,
            pointStatus=self.point_status,
            stacking=stacking.summary(self),
        )

    @Slot(result="QVariantMap")
    def snapshot(self):
        return dict(self._state.as_dict(), lines=self.lines, footprint=stacking.lines(self))

    def activated(self):
        self.controller.activate_geometry()
        self.notify()

    def synchronize(self):
        from anthroforge.core.mirroring import source

        controller, session = self.controller, self.controller.session
        item = session.document.registry.records.get(source(controller.selection))
        self.update_context(self.selection_context(item))
        if not self.target:
            return
        if self.editing_geometry() and self.stage:
            self.clear()
        self.refresh_inspection()

    def update_context(self, context):
        if context != self.context:
            self.clear()
            self.context, self.target = context, context[2]
            self.notify()

    def refresh_inspection(self):
        stamp = self.inspection_stamp()
        if stamp == self.refresh_stamp:
            return
        self.refresh_stamp = stamp
        self.refresh_comparison()
        self.refresh_stacking()
        self.refresh_projection()
        self.refresh_evidence()

    def refresh_stacking(self):
        value = stacking.status(self)
        if value != self.stacking_status:
            self.stacking_status = value
            self.notify()

    @Slot(str, str, str)
    def showStacking(self, other, side, other_side):
        self.attempt(stacking.show, self, other, side, other_side)

    @Slot()
    def hideStacking(self):
        inspection.cancel(self.controller.session, "stacking")
        self.synchronize()

    def inspection_stamp(self):
        session = self.controller.session
        return (
            id(session.document),
            self.stage,
            self.reference,
            self.mode,
            self.context,
            session.issues.repository.revision,
            self.candidate_stamp(),
        )

    def candidate_stamp(self):
        session = self.controller.session
        return tuple(
            (k, v.job, v.state, id(v.asset), v.error)
            for k, v in (
                *session.tissue_inspection.values.items(),
                *session.painting.values.items(),
            )
        )

    def selection_context(self, item):
        session = self.controller.session
        return (
            str(session.document.id),
            session.active_workspace,
            self.controller.selection if isinstance(item, TissueVCP) else "",
        )

    def editing_geometry(self):
        return self.controller.authoring.editing or bool(
            self.controller.tissue_region_tools.options
        )

    def refresh_comparison(self):
        session = self.controller.session
        if self.stage and self.reference and self.mode == "Displacement":
            if inspection.status(session, "comparison")["state"] == "stale":
                inspection.start(
                    session, "comparison", self.target, stage=self.stage, reference=self.reference
                )

    def refresh_projection(self):
        session = self.controller.session
        rows = stages.describe(session, self.target)["stages"]
        settings = self.stage, self.reference, self.mode
        queries = tuple(inspection.status(session, kind) for kind in ("comparison", "paint"))
        key = rows, settings, queries, self.stacking_status
        if key == self.key:
            return
        self.key, self.rows = key, rows
        values, leases = scene.rows(self)
        self.model.publish(values, leases)
        self.notify()

    def refresh_evidence(self):
        session = self.controller.session
        status = inspection.status(session, "point")
        value = session.tissue_inspection.values.get("point")
        point = (
            status["report"] if status["state"] == "ready" and value.target == self.target else {}
        )
        summary = inspection.status(session, "comparison")
        if point != self.point or summary != self.summary or status != self.point_status:
            self.point, self.summary = point, summary
            self.point_status = status
            if not self.finding:
                self.lines = value.asset["lines"] if point else []
            self.notify()
        self.validate_finding()

    @Slot(str, str, str)
    def configure(self, stage, reference, mode):
        self.attempt(self.set_view, stage, reference, mode)

    def set_view(self, stage, reference, mode):
        self.prepare_view(stage)
        self.stage, self.reference, self.mode = stage, reference, mode
        self.finding, self.lines = "", []
        self.cancel()
        if stage and reference and mode == "Displacement":
            self.start_comparison()
        else:
            inspection.cancel(self.controller.session, "comparison")
        self.key = None
        self.synchronize()

    def prepare_view(self, stage):
        if self.editing_geometry():
            raise ValueError("Finish component editing before comparing tissue stages.")
        if stage != self.stage:
            inspection.cancel(self.controller.session, "point")

    def start_comparison(self):
        inspection.start(
            self.controller.session,
            "comparison",
            self.target,
            stage=self.stage,
            reference=self.reference,
        )

    @Slot()
    def explain(self):
        self.attempt(self.arm)

    def arm(self):
        if self.controller.session.history.before is not None:
            raise ValueError("Finish the current edit before selecting an inspection point.")
        self.controller.cancelViewportTools(self)
        self.armed = not self.armed
        self.finding, self.lines = "", []
        self.notify()

    @Slot("QVariantList", "QVariantList", bool)
    def probe(self, origin, direction, confirm):
        if self.armed and confirm:
            self.attempt(self.pick, origin, direction)

    def pick(self, origin, direction):
        session = self.controller.session
        stage = self.stage or displayed_stage(session, self.target)
        mesh = stages.mesh(session, self.target, stage)
        row = scene.primary(self) if self.stage else self.controller.pick_rows.get(self.target)
        asset = stages.result(stages.tissue(session, self.target), stage).asset
        if not row or row["geometry_asset"] != asset:
            raise ValueError("Waiting for the selected stage to be displayed.")
        from .section_queries import pick

        hit = pick(self.controller, self.target, mesh, row["matrix"], origin, direction)
        if hit:
            self.inspect_hit(stage, hit, asset)

    def inspect_hit(self, stage, hit, asset):
        inspection.start(
            self.controller.session,
            "point",
            self.target,
            stage=stage,
            triangle=int(hit[2]),
            weights=hit[7:10],
            expected_asset=asset,
        )
        self.finding = ""

    @Slot()
    def check(self):
        stage = self.stage or displayed_stage(self.controller.session, self.target)
        self.controller.run("tissue.inspect.check", dict(target=self.target, stage=stage))
        self.findingsRequested.emit()

    @Slot()
    def cancel(self):
        self.armed = False
        self.notify()

    def clear(self):
        inspection.cancel(self.controller.session)
        self.stage, self.reference, self.finding = "", "", ""
        self.armed, self.lines, self.point, self.key = False, [], {}, None
        self.refresh_stamp, self.point_status = None, dict(state="idle")
        self.model.publish([])
        self.stacking_status = dict(state="idle")
        self.rows, self.summary = [], {}

    def show_finding(self, identity):
        from .tissue_finding_view import show

        self.attempt(show, self, identity)

    def validate_finding(self):
        if not self.finding:
            return
        session = self.controller.session
        record = session.issues.repository.records.get(self.finding)
        if not record or session.issues.presentation.serialize(record)["freshness"] != "current":
            self.finding, self.lines = "", []
            self.notify()

    def attempt(self, action, *args):
        try:
            action(*args)
        except (ValueError, KeyError) as error:
            self.controller.message = str(error)
            self.controller.notify()


def displayed_stage(session, target):
    item = stages.tissue(session, target)
    return next(
        (
            s
            for s in ("final", "intrinsic", "rest")
            if stages.result(item, s).asset == item.result.asset
        ),
        "final",
    )
