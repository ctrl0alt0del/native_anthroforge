"""Pointer/settings adapter; application painting owns all stroke jobs and commits."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application.painting_state import presented
from anthroforge.core.painting import brush

from . import painting_domains as domains
from . import skin_painting_view
from .models import RenderModel


class WeightPaintingTools(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.name, self.target = controller, "", ""
        self.options, self.token, self.workspace, self.last_error = {}, "", None, ""
        self.last_position = None
        self.domain, self.model = domains.TISSUE, RenderModel(controller)
        self.model.activated.connect(self.changed.emit)
        self.radius, self.weight, self.strength, self.falloff, self.through = 40, 1, 1, 1, False

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(
            **self.domain_state(),
            name=self.name,
            target=self.target,
            dragging=self.dragging,
            pending=self.stroke_state().get("pending", False),
            radius=self.radius,
            weight=self.weight,
            strength=self.strength,
            falloff=self.falloff,
            through=self.through,
        )

    def stroke_state(self):
        if not self.token:
            return {}
        try:
            return self.call("status", token=self.token)
        except ValueError:
            return {}

    @property
    def dragging(self):
        session = self.controller.session
        return bool(
            self.token
            and session.painting.active == self.token
            and not self.stroke_state().get("pending", False)
        )

    @property
    def preview(self):
        return presented(self.controller.session, self.domain.kind)

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

    @Slot(str)
    def begin(self, name):
        self.attempt(self.start_domain, domains.TISSUE, name)

    @Slot()
    def beginCollagen(self):
        self.attempt(self.start_domain, domains.COLLAGEN, "collagen")

    def start_domain(self, domain, name):
        domain.validate(self.controller, name)
        self.cancel()
        self.domain = domain
        self.start(name)

    def start(self, name):
        controller, session = self.controller, self.controller.session
        if session.history.before is not None or session.waiting_save:
            raise ValueError("Finish the current edit before painting.")
        controller.authoring.setEditing(False)
        controller.cancelViewportTools(self)
        controller.section_tools.cancel()
        self.domain.prepare(controller)
        self.name, self.target, self.workspace = (
            name,
            controller.selection,
            session.active_workspace,
        )
        self.changed.emit()

    @Slot()
    def cancel(self):
        self.cancelStroke()
        self.name, self.target = "", ""
        self.changed.emit()

    @Slot()
    def cancelStroke(self):
        if self.token and self.stroke_state():
            self.call("cancel", token=self.token)
        self.options, self.token, self.last_error = {}, "", ""
        self.last_position = None
        self.model.publish([])
        self.changed.emit()

    @Slot(str, "QVariant")
    def setting(self, name, value):
        if self.dragging or self.stroke_state().get("pending", False):
            return
        self.attempt(self.configure, name, value)

    def configure(self, name, value):
        settings = dict(
            radius=self.radius,
            weight=self.weight,
            strength=self.strength,
            falloff=self.falloff,
            through=self.through,
        )
        if name not in settings:
            return
        settings[name] = bool(value) if name == "through" else float(value)
        brush(settings)
        setattr(self, name, settings[name])
        self.changed.emit()

    def brush_settings(self, hover=False):
        return dict(
            radius=self.radius,
            weight=self.weight,
            strength=0 if hover else self.strength,
            falloff=self.falloff,
            through=self.through,
        )

    @Slot("QVariantList", "QVariantList", bool)
    def pointer(self, position, camera, press):
        if (
            self.name
            and not self.stroke_state().get("pending", False)
            and not self.controller.session.waiting_save
        ):
            self.attempt(self.sample, position, camera, press)

    def sample(self, position, camera, press):
        if press:
            self.start_stroke(camera)
        if self.dragging:
            self.append_pointer(position)
        elif not self.options or self.options["view"] != camera:
            self.hover(position, camera)
        self.changed.emit()

    def append_pointer(self, position):
        if position != self.last_position:
            self.call("append", token=self.token, samples=[position])
            self.last_position = list(position)

    def start_stroke(self, camera):
        self.cancelStroke()
        self.options = self.domain.capture(self, camera)
        result = self.call(
            "begin",
            consumer=self.domain.consumer,
            target=self.target,
            brush=self.brush_settings(),
            **self.options,
        )
        self.token = result["token"]

    def hover(self, position, camera):
        self.options = self.domain.capture(self, camera)
        result = self.call(
            "preview",
            consumer=self.domain.consumer,
            target=self.target,
            brush=self.brush_settings(True),
            samples=[position],
            **self.options,
        )
        self.token = result["token"]

    @Slot()
    def release(self):
        if self.dragging:
            self.attempt(self.call, "finish", token=self.token)
        self.changed.emit()

    def synchronize(self):
        if not self.name:
            return
        session, state = self.controller.session, self.stroke_state()
        if self.controller.selection != self.target or session.active_workspace != self.workspace:
            self.cancel()
        elif state.get("state") in ("stale", "obsolete", "cancelled"):
            self.cancelStroke()
        elif state.get("state") in ("committed", "failed"):
            self.options = {}
        self.report(state.get("error", ""))
        skin_painting_view.publish(self)
        self.changed.emit()

    def call(self, operation, **arguments):
        return self.controller.session.command("painting." + operation, **arguments)

    def report(self, message):
        if message and message != self.last_error:
            self.last_error = message
            self.controller.message = message
            self.controller.changed.emit()

    def attempt(self, action, *args, **kwargs):
        try:
            action(*args, **kwargs)
        except (ValueError, KeyError) as error:
            self.report(str(error))
