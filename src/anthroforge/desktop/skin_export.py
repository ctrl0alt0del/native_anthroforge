"""Export controls delegate policy and capture to the shared skin export operation."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from .controller_actions import local_path


class SkinExport(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.job, self.path = controller, None, ""
        controller.changed.connect(self.synchronize)

    @Property(bool, notify=changed)
    def busy(self):
        return bool(self.job and self.job.active)

    @Slot(str, str)
    def start(self, path, policy):
        result = self.controller.run("skin.export", dict(path=local_path(path), policy=policy))
        if result and result.get("job"):
            self.path = result["path"]
            self.job = self.controller.session.scheduler.registry.by_id[result["job"]]
            self.changed.emit()

    def synchronize(self):
        if self.job is None or self.job.active:
            return
        job, self.job = self.job, None
        self.controller.message = (
            "Skin exported: " + self.path
            if job.state == "succeeded"
            else "Skin export " + job.state + ": " + job.error
        )
        self.changed.emit()
