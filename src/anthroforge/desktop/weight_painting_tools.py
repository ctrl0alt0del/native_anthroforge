"""Pointer gestures preview in workers and commit one shared field edit on release."""

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from anthroforge.application import tissue_inspection as inspection
from anthroforge.application.inspection_context import scene_signature

from . import painting_domains as domains
from . import skin_painting_view
from .models import RenderModel


class WeightPaintingTools(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.name, self.target = controller, "", ""
        self.samples, self.options, self.job, self.commit_job = [], {}, "", ""
        self.dragging, self.document, self.workspace = False, None, None
        self.preview, self.domain, self.model = None, domains.TISSUE, RenderModel(controller)
        self.model.activated.connect(self.changed.emit)
        self.radius, self.weight, self.strength, self.falloff, self.through = 40, 1, 1, 1, False
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(60)
        self.timer.timeout.connect(self.submit)

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(
            **self.domain_state(),
            name=self.name,
            target=self.target,
            dragging=self.dragging,
            pending=bool(self.commit_job),
            radius=self.radius,
            weight=self.weight,
            strength=self.strength,
            falloff=self.falloff,
            through=self.through,
        )

    @Slot(str)
    def begin(self, name):
        self.attempt(self.start_domain, domains.TISSUE, name)

    def start(self, name):
        controller, session = self.controller, self.controller.session
        if session.history.before is not None or session.waiting_save:
            raise ValueError("Finish the current edit before painting.")
        self.domain.validate(controller, name)
        controller.authoring.setEditing(False)
        controller.cancelViewportTools(self)
        controller.section_tools.cancel()
        self.prepare_view()
        self.name, self.target = name, controller.selection
        self.workspace = session.active_workspace
        self.options = {}
        self.changed.emit()

    def prepare_view(self):
        self.domain.prepare(self.controller)

    def domain_state(self):
        rows = self.model.active_rows()
        return dict(
            active=bool(self.name),
            domain=self.domain.kind,
            hiddenOwner=rows[0]["owner"] if rows else "",
        )

    @Property(QObject, constant=True)
    def geometry(self):
        return self.model

    @Slot()
    def beginCollagen(self):
        self.attempt(self.start_domain, domains.COLLAGEN, "collagen")

    def start_domain(self, domain, name):
        domain.validate(self.controller, name)
        self.cancel()
        self.domain = domain
        self.start(name)

    @Slot()
    def cancel(self):
        self.cancelStroke()
        self.name, self.target, self.options = "", "", {}
        self.changed.emit()

    @Slot()
    def cancelStroke(self):
        self.timer.stop()
        inspection.cancel(self.controller.session, self.domain.kind)
        self.samples, self.job, self.commit_job, self.dragging = [], "", "", False
        self.document = None
        self.preview = None
        self.model.publish([])
        self.changed.emit()

    @Slot(str, "QVariant")
    def setting(self, name, value):
        if self.dragging or self.commit_job:
            return
        limits = dict(radius=(1, 4096), weight=(0, 1), strength=(0, 1), falloff=(0.05, 20))
        if name == "through":
            self.through = bool(value)
        elif name in limits and limits[name][0] <= float(value) <= limits[name][1]:
            setattr(self, name, float(value))
        self.changed.emit()

    @Slot("QVariantList", "QVariantList", bool)
    def pointer(self, position, camera, press):
        if self.name and not self.commit_job and not self.controller.session.waiting_save:
            self.attempt(self.sample, position, camera, press)

    def sample(self, position, camera, press):
        if press:
            self.cancelStroke()
            self.options = self.domain.capture(self, camera)
            self.document, self.dragging = scene_signature(self.controller.session.document), True
        if self.dragging:
            self.append(position)
        elif not self.options or self.options["view"] != camera:
            self.options = self.domain.capture(self, camera)
            self.samples = [list(position)]
        else:
            return
        if not self.timer.isActive():
            self.timer.start()
        self.changed.emit()

    def append(self, position):
        if len(self.samples) >= 4096:
            raise ValueError("Stroke reached its sample limit. Release to commit, then continue.")
        if not self.samples or self.samples[-1] != position:
            self.samples.append(list(position))

    def submit(self):
        self.attempt(self.request)

    def request(self):
        brush = [
            self.radius,
            self.weight,
            self.strength if self.dragging else 0,
            self.falloff,
            self.through,
        ]
        options = dict(self.options, samples=list(self.samples), brush=brush)
        value = inspection.start(self.controller.session, self.domain.kind, self.target, **options)
        self.job = value["job"]

    @Slot()
    def release(self):
        if not self.dragging:
            return
        self.timer.stop()
        self.submit()
        self.commit_job, self.dragging = self.job, False
        self.changed.emit()

    def synchronize(self):
        if not self.name:
            return
        session = self.controller.session
        self.retain_preview()
        if self.controller.selection != self.target or session.active_workspace != self.workspace:
            self.cancel()
        elif self.document is not None and scene_signature(session.document) != self.document:
            self.cancelStroke()
            self.options = {}
        elif self.commit_job:
            self.complete()

    def retain_preview(self):
        value = self.controller.session.tissue_inspection.values.get(self.domain.kind)
        if value and value.state == "ready" and value.asset:
            self.preview = value.asset
        skin_painting_view.publish(self)

    def complete(self):
        value = inspection.status(self.controller.session, self.domain.kind)
        if value["state"] in ("queued", "running"):
            return
        job = self.commit_job
        self.document, self.commit_job, self.options = None, "", {}
        if value["state"] == "ready":
            self.controller.run(self.domain.commit, dict(job=job))
        elif value.get("error"):
            self.controller.message = value["error"]
            self.controller.changed.emit()
        self.changed.emit()

    def attempt(self, action, *args):
        try:
            action(*args)
        except (ValueError, KeyError) as error:
            self.controller.message = str(error)
            self.controller.notify()
