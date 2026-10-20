"""Direct surface creation; show a grouping editor only for ambiguous connections."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import surface_group_draft, surface_grouping

from .image_tools import context_owner


class SurfaceCreation(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.pending, self.roles, self.boundaries = controller, {}, {}, {}
        self.context = None

    @Property("QVariantMap", notify=changed)
    def state(self):
        return self.pending

    def request(self, curves, kind):
        self.cancel()
        try:
            info = (
                surface_grouping.inspect(self.controller.session, curves)
                if kind == "AUTO" and len(curves) > 1
                else {}
            )
            if info.get("ambiguous"):
                return self.open(info)
            return self.create(curves, kind)
        except ValueError as error:
            self.controller.message = str(error)
            self.controller.notify()

    def create(self, curves, kind, grouping=None):
        args = dict(curves=curves, kind=kind, owner=context_owner(self.controller))
        if grouping is not None:
            args["grouping"] = grouping
        return self.controller.creation_selection.create("surface.create", args)

    def open(self, info):
        self.context = self.controller.session.document.id, self.controller.session.active_workspace
        self.pending = dict(curves=info["curves"])
        self.roles = {key: 0 for key in info["plan"]["main"]}
        for index, group in enumerate(info["plan"]["branches"], 1):
            self.roles.update({key: index for key in group["curves"]})
            self.boundaries[str(index)] = group["boundary"]
        self.review()

    def review(self):
        curves = [row["id"] for row in self.pending["curves"]]
        try:
            result = surface_group_draft.review(
                self.controller.session, curves, self.roles, self.boundaries
            )
        except (KeyError, ValueError):
            result = dict(
                valid=False, reason="Sources changed. Cancel and select the source curves again."
            )
        self.pending = dict(self.pending, **result, roles=dict(self.roles))
        self.changed.emit()

    @Slot(str, int)
    def assign(self, curve, group):
        if curve in self.roles and 0 <= group <= len(self.roles) // 2:
            self.roles[curve] = group
            self.review()

    @Slot(int, str)
    def boundary(self, group, curve):
        self.boundaries[str(group)] = curve
        self.review()

    @Slot()
    def accept(self):
        if self.context != (
            self.controller.session.document.id,
            self.controller.session.active_workspace,
        ):
            return self.cancel()
        self.review()
        if self.pending["valid"]:
            curves = [row["id"] for row in self.pending["curves"]]
            if self.create(curves, "AUTO", self.pending["plan"]):
                self.cancel()

    @Slot()
    def cancel(self):
        self.pending, self.roles, self.boundaries = {}, {}, {}
        self.changed.emit()
