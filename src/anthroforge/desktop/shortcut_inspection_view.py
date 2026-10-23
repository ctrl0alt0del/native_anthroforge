"""Incremental optional inspection over the shared read-only shortcut operations."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import (
    shortcut_anchor_query,
    shortcut_effects,
    shortcut_formula_inspection,
    shortcut_policy_inspection,
    shortcut_progress,
)
from anthroforge.application import tissue_inspection as queries

from .record_model import RecordModel
from .values import qml

LABELS = dict(
    complete="Complete",
    updating="Updating",
    waiting_manual="Waiting for Manual",
    waiting_release="Waiting for release",
    failed="Failed · previous output retained",
    cancelled="Cancelled",
    superseded="Superseded",
)


class ShortcutInspectionView(QObject):
    changed = Signal()

    def __init__(self, editor):
        super().__init__(editor)
        self.editor, self.enabled, self.shown = editor, False, False
        self.signature, self.anchor_stamp, self.session = None, None, None
        self.value, self.search, self.offset = {}, "", 0
        self.effects = RecordModel(self, ("key", "label", "detail", "target", "direct"), "key")

    @Property("QVariantMap", notify=changed)
    def state(self):
        return qml(self.value)

    @Property(bool, notify=changed)
    def opened(self):
        return self.enabled

    @Property(QObject, constant=True)
    def affected(self):
        return self.effects

    @Slot(bool)
    def activate(self, enabled):
        if self.enabled == enabled:
            return
        self.enabled = enabled
        if not enabled:
            self.clear()
        self.signature = None
        self.synchronize()
        self.changed.emit()

    @Slot(bool)
    def showEffects(self, enabled):
        self.shown = enabled
        self.anchor_stamp = self.signature = None
        if not enabled:
            queries.cancel(self.controller.session, "shortcut")
        self.synchronize()

    @property
    def controller(self):
        return self.editor.panel.controller

    @Slot(str)
    def filter(self, search):
        self.search, self.offset, self.signature = search, 0, None
        self.synchronize()

    @Slot(int)
    def page(self, direction):
        self.offset = max(0, self.offset + direction * 50)
        self.signature = None
        self.synchronize()

    def clear(self):
        self.shown = False
        self.anchor_stamp = None
        if self.session is not None:
            queries.cancel(self.session, "shortcut")
        self.value = {}
        self.signature = None
        self.effects.synchronize_records([])
        self.changed.emit()

    def synchronize(self):
        session = self.controller.session
        if self.session is not session:
            self.clear()
            self.session = session
        if not self.enabled or not self.editor.selected():
            return
        self.refresh_if_changed(session)
        if self.shown:
            self.refresh_anchors()

    def refresh_if_changed(self, session):
        signature = (
            session.document.revision,
            session.shortcut_observation.serial,
            self.editor.key,
            session.active_workspace,
            self.shown,
            self.editor.panel.display_revision,
        )
        if signature != self.signature:
            self.signature = signature
            self.refresh()

    def refresh(self):
        session, key = self.controller.session, self.editor.key
        effects = shortcut_effects.inspect(session, key, self.search, self.offset, 50)
        self.effects.synchronize_records([effect_row(r) for r in effects["rows"]])
        progress = shortcut_progress.inspect(session, key)
        self.value = self.details(session, key, progress)
        self.value.update(showEffects=self.shown, total=effects["total"], offset=self.offset)
        self.changed.emit()

    def details(self, session, key, progress):
        return dict(
            progress=progress,
            status=badge(self.editor.panel, key) or LABELS[progress["state"]],
            formulas=shortcut_formula_inspection.inspect(session, key)["rows"],
            policy=shortcut_policy_inspection.inspect(session, key),
        )

    def refresh_anchors(self):
        session, key = self.controller.session, self.editor.key
        stamp = shortcut_anchor_query.signature(session, key, {})
        if stamp != self.anchor_stamp:
            self.anchor_stamp = stamp
            queries.start(session, "shortcut", key)
        status = queries.status(session, "shortcut")
        if status != self.value.get("anchors"):
            self.value["anchors"] = status
            self.changed.emit()

    @Slot(str, bool)
    def navigate(self, target, frame):
        controller = self.controller
        if controller.session.history.before is not None or controller.session.waiting_save:
            return
        if target in controller.session.document.registry.records:
            controller.inspection_panel.navigate(target, frame)
        else:
            record = controller.session.document.formula_index.formulas.get(target)
            key = record[0].id if record else target
            if key in controller.session.document.formula_index.drivers:
                self.editor.select(key)

    @Slot(result="QVariantMap")
    def snapshot(self):
        from .shortcut_effects_scene import snapshot

        return snapshot(self) if self.enabled and self.shown and self.editor.selected() else {}


def effect_row(row):
    parts = ("Direct" if row["direct"] else "Downstream", row["output"], row["status"])
    return dict(
        key=row["owner"] + ":" + row["output"],
        target=row["owner"],
        direct=row["direct"],
        label=row["name"],
        detail=" · ".join((*parts, "Editable" if row["editable"] else "Context")),
    )


def badge(panel, key):
    from .shortcut_effects_scene import publishing

    session = panel.controller.session
    if key not in session.shortcut_observation.latest:
        return ""
    cached = session.shortcut_observation.progress.get(key)
    state = (cached or shortcut_progress.inspect(session, key))["state"]
    return (
        "Preparing display"
        if state == "complete" and publishing(panel.controller, key)
        else LABELS[state]
    )
