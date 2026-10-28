"""Saved fit selection and playback presentation; application operations own semantics."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import skin_fit_preview, skin_fit_results

from .record_model import RecordModel
from .values import qml


class SkinFitPanel(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.selected, self.current = controller, "", None
        self.details, self.filter = {}, ""
        self.rows = RecordModel(self, ("key", "label", "stale"), "key")
        controller.changed.connect(self.refresh)
        self.refresh()

    def refresh(self):
        session = self.controller.session
        key = id(session.document), self.selected, self.filter, id(session.skin_fit_preview)
        if key == self.current:
            return
        self.current = key
        fits = [skin_fit_results.inspect(session, f.id) for f in session.document.skin.fits]
        self.details = next((f for f in fits if f["id"] == self.selected), {})
        self.rows.synchronize_records([row(f) for f in fits if self.matches(f)])
        self.changed.emit()

    def matches(self, fit):
        return self.filter.casefold() in fit["report"].get("label", "Fitted shortcut").casefold()

    @Property(QObject, constant=True)
    def results(self):
        return self.rows

    @Property("QVariantMap", notify=changed)
    def state(self):
        return qml(self.details)

    @Property("QVariantMap", notify=changed)
    def previewState(self):
        return skin_fit_preview.status(self.controller.session)

    @Property("QVariantMap", notify=changed)
    def refitEligibility(self):
        return qml(skin_fit_results.refit_eligibility(self.controller.session, self.selected))

    @Slot(str)
    def select(self, identity):
        self.selected = identity
        self.refresh()

    @Slot(str)
    def search(self, value):
        self.filter = value
        self.refresh()

    @Slot(float)
    def preview(self, value):
        self.controller.run("skin.fit.preview", dict(identity=self.selected, value=value))

    @Slot()
    def hide(self):
        self.controller.run("skin.fit.preview.cancel", {})

    @Slot()
    def remove(self):
        self.controller.run("skin.fit.remove", dict(identity=self.selected))

    @Slot()
    def refit(self):
        report = self.details.get("report", {})
        self.controller.run(
            "skin.fit",
            dict(shortcut=self.details.get("shortcut", ""), settings=report.get("settings", {})),
        )


def row(fit):
    return dict(
        key=fit["id"], label=fit["report"].get("label", "Fitted shortcut"), stale=fit["stale"]
    )
