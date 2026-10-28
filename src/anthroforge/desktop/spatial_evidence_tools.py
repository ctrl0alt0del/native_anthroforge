"""Read-only spatial witnesses use staged resource leases for any accepted mesh stage."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import inspection_surfaces, spatial_evidence

from . import inspection_scene
from .models import RenderModel
from .tissue_finding_view import camera_frame


class SpatialEvidenceTools(QObject):
    changed = Signal()
    findingsRequested = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.model = controller, RenderModel(controller)
        self.row, self.lines, self.context = {}, [], None
        self.eligibility, self.frozen = None, False
        self.model.activated.connect(self.changed.emit)

    @Property(QObject, constant=True)
    def geometry(self):
        return self.model

    @Property("QVariantMap", notify=changed)
    def state(self):
        witness = self.row.get("evidence", {}).get("witness", {})
        return dict(
            active=bool(self.row),
            title=self.row.get("summary", ""),
            stage=witness.get("stage", ""),
            revision=witness.get("accepted_revision", 0),
            available=bool(self.eligibility and self.eligibility.available),
            reason=self.eligibility.reason if self.eligibility else "Select a surface.",
        )

    @Slot(result="QVariantMap")
    def snapshot(self):
        witness = self.row.get("evidence", {}).get("witness", {})
        displayed = any(
            r.get("geometry_asset") == witness.get("asset") for r in self.model.displayed
        )
        return dict(self.state, lines=self.lines if displayed else [])

    @Slot(str, str)
    def check(self, target, stage):
        if self.controller.run("geometry.check", dict(target=target, stage=stage)):
            self.findingsRequested.emit()

    @Slot(str)
    def show(self, identity):
        try:
            self.require_navigation()
            self.restore(spatial_evidence.issue(self.controller.session, identity))
            self.controller.frameRequested.emit(
                camera_frame(self.row["evidence"]["witness"]["bounds"])
            )
        except (ValueError, KeyError) as error:
            self.controller.message = str(error)
            self.controller.notify()

    def require_navigation(self):
        session = self.controller.session
        if session.history.before is not None or session.waiting_save:
            raise ValueError("Finish the current edit before locating a finding.")

    def restore(self, row, frozen=False):
        session = self.controller.session
        witness = row["evidence"]["witness"]
        surface = spatial_evidence.current_surface(session, witness)
        mesh = surface.mesh(session)
        metadata = self.metadata(surface)
        self.row, self.lines = row, spatial_evidence.lines(session, witness)
        self.frozen = frozen
        self.model.publish(inspection_scene.chunks(metadata, mesh), [mesh])
        self.context = self.signature()
        self.changed.emit()

    def metadata(self, surface):
        return dict(
            inspection_scene.placement(self.controller.session, surface.frame),
            id=surface.target + ":finding",
            owner=surface.target,
            stage=surface.stage,
            kind="MESH",
            reference=False,
            color="#dba2b4",
            geometry_asset=surface.asset,
            geometry_revision=surface.revision,
            status="ready",
            surface_pickable=False,
        )

    def signature(self):
        session = self.controller.session
        return (
            session,
            session.document,
            session.issues.repository.revision,
            self.controller.selection,
        )

    def synchronize(self):
        if self.signature() == self.context:
            return
        self.context = self.signature()
        self.eligibility = inspection_surfaces.eligibility(
            self.controller.session, self.controller.selection
        )
        self.changed.emit()
        if self.row:
            self.validate_witness()

    def validate_witness(self):
        try:
            if self.frozen:
                spatial_evidence.current_surface(
                    self.controller.session, self.row["evidence"]["witness"]
                )
            else:
                spatial_evidence.issue(self.controller.session, self.row["id"])
        except (ValueError, KeyError):
            self.clear()

    @Slot()
    def clear(self):
        self.row, self.lines, self.context = {}, [], None
        self.model.publish([])
        self.changed.emit()
