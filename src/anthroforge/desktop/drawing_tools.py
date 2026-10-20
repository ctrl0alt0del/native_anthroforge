"""One provisional creation gesture over shared native projection and authoring commands."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from . import branch_placement, drawing_context
from .image_tools import context_owner

DEFAULTS = dict(
    depth="VIEW",
    selected_only=False,
    first_plane=0,
    offset=0.0,
    relative=False,
    radius=1.0,
    method="REFIT",
    error=0.002,
    corner_angle=70.0,
    closed=False,
    auto_close=True,
    screen_error=True,
    error_pixels=8.0,
    image="",
)


class DrawingTools(QObject):
    changed = Signal()
    pointsAdded = Signal(list)
    resetPreview = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.mode, self.stroke, self.leases = controller, "", None, ()
        self.painting, self.hover, self.context, self.created = False, [], None, []
        self.options = dict(DEFAULTS)
        self.snapping = False
        self.branch = branch_placement.BranchPlacement(controller)
        self.placement_mode = "POINTS"

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(
            active=bool(self.mode),
            mode=self.mode,
            painting=self.painting,
            count=self.stroke.count if self.stroke else 0,
            hover=self.hover,
            options=self.options,
            branched=self.mode == "BRANCH",
            placement_mode=self.placement_mode,
        )

    @Slot(str)
    def begin(self, mode):
        if (
            self.controller.session.history.before is not None
            or self.controller.session.waiting_save
        ):
            return
        self.cancel()
        self.mode = mode if mode in ("DRAW", "POINTS", "BRANCH", "CURSOR") else ""
        if self.mode in ("POINTS", "BRANCH"):
            self.placement_mode = self.mode
        self.context = self.signature()
        self.controller.authoring.setEditing(False)
        self.controller.cancelViewportTools(self)
        self.changed.emit()

    @Slot()
    def cancel(self):
        self.mode = ""
        self.snapping = False
        self.clear_stroke()

    @Slot()
    def clearStroke(self):
        self.clear_stroke()

    def clear_stroke(self):
        self.stroke, self.leases, self.hover, self.painting = None, (), [], False
        self.branch.reset()
        self.resetPreview.emit()
        self.changed.emit()

    @Slot()
    def addCurve(self):
        result = self.controller.run("curve.create", dict(owner=context_owner(self.controller)))
        if result:
            self.cancel()
            self.controller.select(result)
            self.controller.authoring.setEditing(True)

    @Slot(str)
    def traceImage(self, target):
        if self.controller.session.history.before is not None:
            return
        self.cancel()
        self.options = dict(self.options, depth="IMAGE", image=target)
        self.begin("DRAW")

    def signature(self):
        session = self.controller.session
        return session.document.id, session.active_workspace

    def synchronize(self):
        if self.context != self.signature():
            self.cancel()
            self.context, self.created = self.signature(), []
        published = [
            key for key in self.created if key in self.controller.session.document.registry.records
        ]
        self.created = [key for key in self.created if key not in published]
        if published and not self.mode:
            self.controller.select(published[-1])

    @Slot(str, "QVariant")
    def setting(self, key, value):
        if key not in self.options or (self.stroke and self.stroke.count):
            return
        candidate = dict(self.options, **{key: value})
        try:
            drawing_context.validate_settings(candidate)
            self.options = candidate
            self.clear_stroke()
        except (ValueError, TypeError) as error:
            self.controller.message = str(error)
            self.controller.notify()

    @Slot("QVariantList")
    def viewChanged(self, normal):
        if self.stroke is not None and self.options["depth"] != "IMAGE":
            self.stroke.view(normal)

    @Slot(bool)
    def setSnapping(self, enabled):
        self.snapping = enabled

    @Slot("QVariantList", bool)
    def setProjection(self, origin, perspective):
        self.branch.camera, self.branch.perspective = origin, perspective

    @Slot("QVariantList", "QVariantList", bool)
    def pointer(self, ray, normal, press):
        if not self.mode or self.controller.session.waiting_save:
            return
        try:
            if self.mode == "CURSOR":
                self.place_cursor(ray, press)
            else:
                self.update_stroke(ray, normal, press)
        except ValueError as error:
            self.hover = []
            if press:
                self.controller.message = str(error)
                self.controller.notify()
        self.changed.emit()

    def update_stroke(self, ray, normal, press):
        if self.mode == "BRANCH" and not self.branch.source:
            return branch_placement.update(self, ray, normal, press)
        if self.stroke is None or (press and self.stroke.count == 0):
            self.stroke = drawing_context.capture(self, normal)
        self.stroke.snapping(self.snapping and self.mode in ("POINTS", "BRANCH"))
        self.hover = self.stroke.probe(ray)[:3]
        if press or (self.mode == "DRAW" and self.painting):
            start = self.stroke.count
            substeps = drawing_context.substeps(self.options, self.mode)
            self.stroke.append(ray, substeps, sample=self.mode == "DRAW")
            self.pointsAdded.emit(self.stroke.read(start).tolist())
            self.painting = self.mode == "DRAW"

    def place_cursor(self, ray, press):
        from .curve_interaction import surface_hit

        hit = surface_hit(self.controller, ray[:3], ray[3:6], exclude_current=False)
        self.hover = hit.get("point", [])
        if press and self.hover:
            self.controller.run("workspace.update", dict(cursor=self.hover))
            self.cancel()

    @Slot()
    def release(self):
        if self.mode == "DRAW" and self.painting:
            self.finish()

    @Slot("QVariantList", "QVariantList", bool)
    def click(self, ray, normal, continue_placement):
        before = self.stroke.count if self.stroke else 0
        self.pointer(ray, normal, True)
        count = self.stroke.count if self.stroke else 0
        if self.mode in ("POINTS", "BRANCH") and count > max(1, before) and not continue_placement:
            self.finish()

    @Slot()
    def finish(self):
        if self.stroke is None or self.stroke.count < (3 if self.options["closed"] else 2):
            self.require_more_points()
            return
        samples = self.stroke.read().tolist()
        args = dict(owner=context_owner(self.controller))
        result = self.submit(samples, args)
        if result:
            self.created.append(result if isinstance(result, str) else result["object_id"])
            if self.mode in ("POINTS", "BRANCH"):
                self.mode = ""
            self.clear_stroke()

    def require_more_points(self):
        count = "three" if self.options["closed"] else "two"
        self.controller.message = f"Place at least {count} points."
        self.controller.notify()

    def submit(self, samples, args):
        if self.mode in ("POINTS", "BRANCH"):
            args.update(
                points=drawing_context.point_records(samples), closed=self.options["closed"]
            )
            args.update(
                values=[0, 0, 0, 0, 0, 0, 1, 1, 1],
                engine="POLYLINE" if self.options["method"] == "POLYLINE" else "BEZIER",
            )
            return self.submit_points(args)
        settings = drawing_context.finish_settings(self)
        return self.controller.run("curve.draw", dict(args, points=samples, settings=settings))

    @Slot()
    def removeLast(self):
        if self.mode not in ("POINTS", "BRANCH") or self.stroke is None:
            return
        self.stroke.pop()
        if not self.stroke.count:
            self.branch.source = {}
        self.resetPreview.emit()
        self.pointsAdded.emit(self.stroke.read().tolist())
        self.changed.emit()

    def submit_points(self, args):
        if self.mode == "BRANCH":
            args.pop("values", None)
            return self.controller.run("curve.branch.create", dict(args, source=self.branch.source))
        return self.controller.run("curve.create", args)
