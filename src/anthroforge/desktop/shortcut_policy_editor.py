"""Present inferred attachment scope; application operations retain policy authority."""

from dataclasses import asdict

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application.shortcut_ownership import scp_owner
from anthroforge.core.entities import descendants
from anthroforge.core.shortcuts import DescendantOverride, Shortcut

from .record_model import RecordModel


class ShortcutPolicyEditor(QObject):
    changed = Signal()

    def __init__(self, editor):
        super().__init__(editor)
        self.editor, self.owner, self.search, self.backsolve = editor, "", "", False
        self.rows = RecordModel(self, ("target", "label", "policy"), "target")

    @Property(str, notify=changed)
    def ownerName(self):
        return self.owner

    @Property(bool, notify=changed)
    def preserveOwner(self):
        return self.backsolve

    @Property(QObject, constant=True)
    def descendants(self):
        return self.rows

    @Slot(str)
    def filter(self, search):
        self.search = search
        self.synchronize()

    def synchronize(self):
        value = self.editor.selected()
        document = self.editor.panel.controller.session.document
        owner = scp_owner(document, value) if value else ""
        name = document.entity(owner).name if owner else ""
        backsolve = bool(value and value.policy.backsolve)
        if (self.owner, self.backsolve) != (name, backsolve):
            self.owner, self.backsolve = name, backsolve
            self.changed.emit()
        self.rows.synchronize_records(policy_rows(document, value, owner, self.search))

    @Slot(bool)
    def setBacksolve(self, enabled):
        value = self.editor.selected()
        if value:
            self.apply(dict(asdict(value.policy), backsolve=enabled))

    @Slot(str, str, str)
    def override(self, target, field, choice):
        value = self.editor.selected()
        if value is None:
            return
        rows = {p.target: asdict(p) for p in value.policy.descendants}
        rows[target] = dict(rows.get(target, asdict(DescendantOverride(target))), **{field: choice})
        rows = {key: row for key, row in rows.items() if row != asdict(DescendantOverride(key))}
        self.apply(dict(backsolve=value.policy.backsolve, descendants=list(rows.values())))

    def apply(self, policy):
        value, controller = self.editor.selected(), self.editor.panel.controller
        if isinstance(value, Shortcut):
            controller.run(
                "shortcut.configure", dict(reference=asdict(value.reference), policy=policy)
            )
        elif value:
            controller.run("driver.configure", dict(driver=value.id, changes=dict(policy=policy)))
        self.synchronize()


def policy_rows(document, value, owner, search):
    if not owner:
        return []
    configured = {p.target: p for p in value.policy.descendants}
    allowed = descendants(document.entities, owner) - {owner}
    return [
        dict(
            target=key,
            label=document.entity(key).name,
            policy=asdict(configured.get(key, DescendantOverride(key))),
        )
        for key in sorted(allowed, key=lambda key: document.entity(key).name.casefold())
        if search.casefold() in document.entity(key).name.casefold()
    ]
