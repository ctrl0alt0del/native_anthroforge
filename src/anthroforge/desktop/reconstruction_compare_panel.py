"""Focused stage comparison, region drafts and file evidence without document editing."""

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from anthroforge.application import reconstruction_regions, reconstruction_views

from .reconstruction_scene import ReconstructionScene


class ReconstructionComparePanel(QObject):
    changed = Signal()
    requested = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.subject, self.active = controller, "", False
        self.selections, self.options, self.report = [{}, {}], [], {}
        self.signature, self.error, self.plane = None, "", None
        self.region, self.pending_region = "", None
        self.scene = ReconstructionScene(controller, self)

    @Property(QObject, constant=True)
    def comparison(self):
        return self.scene

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(
            subject=self.subject,
            options=self.options,
            selections=self.selections,
            report=self.report,
            error=self.error,
            plane=self.plane,
            region=self.region,
        )

    @Slot(str)
    def inspect(self, subject):
        self.subject, self.active = subject, True
        self.region, self.pending_region = "", None
        try:
            self.options = reconstruction_views.options(self.controller.session, subject)["views"]
            if not self.options:
                raise ValueError("This anatomy has no accepted stages to compare yet.")
            self.selections = [self.options[0], self.options[-1]]
            self.submit()
            self.requested.emit()
        except ValueError as error:
            self.controller.message = str(error)
            self.controller.notify()

    @Slot(int, "QVariantMap")
    def choose(self, side, choice):
        self.selections[side] = dict(choice)
        self.submit()

    @Slot(bool, int, float, bool)
    def section(self, enabled, axis, position, flip):
        sign = -1 if flip else 1
        self.plane = (
            [*(sign * int(axis == i) for i in range(3)), -position * sign] if enabled else None
        )
        self.submit()

    @Slot()
    def submit(self):
        args = [
            dict(stage=s.get("stage", "final"), variant=s.get("variant", ""))
            for s in self.selections
        ]
        self.controller.run(
            "reconstruction.compare.start",
            dict(subject=self.subject, before=args[0], after=args[1], plane=self.plane),
        )
        self.scene.selectRegion(-1)
        self.signature = None
        self.synchronize()

    def synchronize(self):
        if not self.active:
            return
        service = self.controller.session.reconstruction_comparison
        value = service.value
        signature = (id(value), value.state if value else "", id(value.asset) if value else 0)
        if signature == self.signature:
            return
        self.signature = signature
        state = service.status()
        self.report, self.error = state.get("report", {}), state.get("error", "")
        self.scene.synchronize(service.pair)
        self.scene.set_sections(self.report)
        self.show_pending_region()
        self.changed.emit()

    @Slot(str)
    def inspectRegion(self, key):
        try:
            self.open_region(key)
        except ValueError as error:
            self.controller.message = str(error)
            self.controller.notify()

    def open_region(self, key):
        row = self.controller.session.command("catalogue.region.inspect", region=key)
        self.inspect(row["target"])
        self.region, self.pending_region = key, row
        role = "base" if row["role"] == "TISSUE_BASE" else "final"
        found = [r for r in self.options if r["stage"] == role and r["variant"] == row["variant"]]
        if not found:
            raise ValueError("Evaluate this region's surface before redefining it.")
        self.selections[1] = found[0]
        self.submit()

    def show_pending_region(self):
        if self.pending_region is None or not self.report or not self.scene.candidate:
            return
        row, self.pending_region = self.pending_region, None
        if row["available"]:
            self.scene.show_region(1, row["triangles"])
        else:
            self.scene.selectRegion(1)
            self.error = row["reason"]

    @Slot(str)
    def saveRegion(self, name):
        try:
            self.commit_region(name)
        except ValueError as error:
            self.error = str(error)
            self.changed.emit()

    def commit_region(self, name):
        if self.scene.patch is None or not self.scene.candidate:
            raise ValueError("Choose a view and select its surface triangles.")
        view = self.scene.candidate[self.scene.patch]
        arguments = reconstruction_regions.view_arguments(
            self.controller.session, view, name, sorted(self.scene.triangles)
        )
        if self.region:
            arguments["region"] = self.region
        self.controller.run("catalogue.region.set", arguments)
        self.scene.selectRegion(-1)
        self.region = ""

    @Slot()
    def cancel(self):
        self.active = False
        self.controller.session.reconstruction_comparison.cancel()
        self.scene.synchronize(None)

    @Slot(str)
    def export(self, url):
        self.controller.run(
            "reconstruction.compare.export",
            dict(path=QUrl(url).toLocalFile(), camera=self.scene.camera, mode=self.scene.mode),
        )
