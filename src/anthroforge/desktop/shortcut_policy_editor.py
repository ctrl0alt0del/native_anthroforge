"""Present inferred attachment scope; application operations retain policy authority."""

from dataclasses import asdict

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application.shortcut_ownership import attachment_scope, owners
from anthroforge.core.entities import descendants
from anthroforge.core.shortcuts import DescendantOverride, Shortcut

from .record_model import RecordModel


class ShortcutPolicyEditor(QObject):
    changed = Signal()

    def __init__(self, editor):
        super().__init__(editor)
        self.editor, self.owner, self.search, self.backsolve = editor, "", "", False
        self.rows = RecordModel(self, ("target", "label", "policy"), "target")
        self.scopes, self.scope = [], ""

    @Property(str, notify=changed)
    def ownerName(self):
        return self.owner

    @Property(bool, notify=changed)
    def preserveOwner(self):
        return self.backsolve

    @Property(QObject, constant=True)
    def descendants(self):
        return self.rows

    @Property("QVariantList", notify=changed)
    def scopeOptions(self):
        return self.scopes

    @Property(str, notify=changed)
    def scopeIdentity(self):
        return self.scope

    @Slot(str)
    def setScope(self, key):
        value = self.editor.selected()
        if value:
            self.apply(dict(scope=key, backsolve=False, descendants=[]))

    @Slot(str)
    def filter(self, search):
        self.search = search
        self.synchronize()

    def synchronize(self):
        value = self.editor.selected()
        document = self.editor.panel.controller.session.document
        owner = attachment_scope(document, value) if value else ""
        self.update_scopes(document, value)
        name = document.entity(owner).name if owner else ""
        backsolve = bool(value and value.policy.backsolve)
        if (self.owner, self.backsolve) != (name, backsolve):
            self.owner, self.backsolve = name, backsolve
            self.changed.emit()
        self.rows.synchronize_records(policy_rows(document, value, owner, self.search))

    def update_scopes(self, document, value):
        allowed = owners(document, value) & document.index.entities.keys() if value else set()
        scopes = [dict(id="", label="Automatic")]
        scopes += [dict(id=k, label=document.entity(k).name) for k in sorted(allowed)]
        scope = value.policy.scope if value else ""
        if (scopes, scope) != (self.scopes, self.scope):
            self.scopes, self.scope = scopes, scope
            self.changed.emit()

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
        self.apply(dict(asdict(value.policy), descendants=list(rows.values())))

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
