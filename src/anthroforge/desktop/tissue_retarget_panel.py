"""Attached construction selection shares review and commit behavior with mesh replacement."""

from PySide6.QtCore import Property, Signal, Slot

from .replacement_panel import ReplacementPanel


class TissueRetargetPanel(ReplacementPanel):
    choicesChanged = Signal()

    def __init__(self, controller):
        super().__init__(
            controller, "tissue_retarget", "tissue.source.replace", "Change tissue source"
        )
        self._choices = []

    @Property("QVariantList", notify=choicesChanged)
    def choices(self):
        return self._choices

    @Slot(str)
    def choose(self, target):
        values = self.controller.run("tissue.source.options", dict(target=target))
        if values is None:
            return
        self._choices = values
        self.choicesChanged.emit()
        super().choose(target)

    @Slot(str)
    def assess(self, source):
        self.begin(dict(target=self.target, source=source))
