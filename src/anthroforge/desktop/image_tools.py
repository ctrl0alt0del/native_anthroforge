"""Image file and landmark gestures adapt shared authoring operations."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import (
    curve_sources,
    image_operations,
    image_placement,
    workspace_policy,
)
from anthroforge.core.reference_images import ReferenceImage

from . import image_scene
from .controller_actions import local_path


class ImageTools(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.target, self.points, self.context = controller, "", [], None
        self.import_request = None

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(active=bool(self.target), target=self.target, points=self.points)

    @Slot(str, bool)
    def importFile(self, path, replacing):
        arguments = dict(path=local_path(path))
        if replacing:
            arguments["target"] = self.controller.selection
        else:
            arguments["owner"] = context_owner(self.controller)
        result = self.controller.run("image.replace" if replacing else "image.import", arguments)
        if result:
            self.controller.message = "Image loading in the background."
            self.controller.notify()

    def import_context(self):
        session = self.controller.session
        return session, session.document.id, session.active_workspace

    @Slot(str, str, result=bool)
    def prepareImport(self, parent, axis):
        self.import_request = None
        try:
            owner = context_owner(self.controller)
            image_placement.require_context(self.controller.session, parent, owner)
            self.import_request = self.import_context(), dict(parent=parent, owner=owner, axis=axis)
            return True
        except ValueError as error:
            self.controller.message = str(error)
            self.controller.notify()
            return False

    @Slot()
    def cancelImport(self):
        self.import_request = None

    @Slot(str)
    def acceptImport(self, path):
        request, self.import_request = self.import_request, None
        if request is None:
            return
        context, arguments = request
        if context != self.import_context():
            self.controller.message = "Image import cancelled: document or workspace changed."
            self.controller.notify()
            return
        self.controller.creation_selection.create(
            "image.import", dict(arguments, path=local_path(path))
        )

    @Slot()
    def start(self):
        session, target = self.controller.session, self.controller.selection
        if session.history.before is not None or session.waiting_save:
            return
        image_operations.selected(session, target)
        row = next((r for r in self.controller.image_model.active_rows() if r["id"] == target), {})
        if row.get("geometry_asset") != session.document.object(target).source:
            return
        self.controller.viewport_view.cancelViewportTools(self)
        self.target, self.points, self.context = target, [], self.signature(target)
        self.changed.emit()

    @Slot()
    def cancel(self):
        self.target, self.points, self.context = "", [], None
        self.changed.emit()

    def signature(self, target):
        session = self.controller.session
        item = session.document.registry.construction.get(target)
        frame = curve_sources.world(session.engine, session.document, target) if item else ()
        return session.document.id, session.active_workspace, item, frame

    def synchronize(self):
        if self.target and self.context != self.signature(self.target):
            self.cancel()

    @Slot("QVariantList", "QVariantList", bool)
    def probe(self, origin, direction, confirm):
        if not self.target or not confirm or len(self.points) == 2:
            return
        hit = image_scene.probe(self.controller, self.target, origin, direction)
        if hit:
            self.points = [*self.points, dict(uv=hit["uv"], position=hit["point"])]
            self.changed.emit()

    @Slot(float)
    def accept(self, distance):
        if len(self.points) != 2 or self.signature(self.target) != self.context:
            return
        arguments = dict(
            target=self.target,
            first=self.points[0]["uv"],
            second=self.points[1]["uv"],
            distance=distance,
        )
        self.controller.run("image.calibrate", arguments)


def context_owner(controller):
    session, target = controller.session, controller.selection
    related = workspace_policy.associations(session.document, target) if target else set()
    candidates = sorted(related & session.document.index.entities.keys())
    return next(
        (
            key
            for key in candidates
            if not session.workspace.focused or key in session.workspace.members
        ),
        "",
    )


def parent_choices(controller):
    selected = controller.selection
    objects = controller.session.document.registry.records
    return [
        dict(id="", name="World (no parent)"),
        *[
            dict(id=item.id, name=item.name)
            for item in objects.values()
            if not isinstance(item, ReferenceImage)
            and not descends_from(objects, item.id, selected)
        ],
    ]


def descends_from(objects, target, ancestor):
    visited = set()
    while target and target not in visited:
        if target == ancestor:
            return True
        visited.add(target)
        item = objects[target]
        target = getattr(item, "parent", "") or getattr(item, "follow", "")
    return False
