"""Incremental shortcut presentation and on-demand numerical property discovery."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import property_operations, shortcut_operations
from anthroforge.application.shortcut_ownership import property_owners

from .record_model import RecordModel
from .shortcut_editor import ShortcutEditor
from .values import qml

FIELDS = (
    "key",
    "label",
    "reference",
    "values",
    "numericType",
    "dimension",
    "writable",
    "reason",
    "ownerLabel",
    "kind",
)


class ShortcutPanel(QObject):
    changed = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.active, self.all, self.search = False, False, ""
        self.signature = None
        self.model = RecordModel(self, FIELDS, "key")
        self.catalog = RecordModel(self, (*FIELDS, "exposed"), "key")
        self.editor = ShortcutEditor(self)

    @Property(QObject, constant=True)
    def editing(self):
        return self.editor

    @Property(QObject, constant=True)
    def rows(self):
        return self.model

    @Property(QObject, constant=True)
    def properties(self):
        return self.catalog

    @Slot(bool, bool, str)
    def configure(self, active, all_objects, search):
        self.active, self.all, self.search = active, all_objects, search
        self.signature = None
        self.synchronize()

    def selected_owner(self):
        session, selected = self.controller.session, self.controller.selection
        owners = property_owners(session.document, selected) if selected else set()
        return next(iter(owners)) if len(owners) == 1 else ""

    def synchronize(self):
        if not self.active:
            return
        session = self.controller.session
        signature = (session, session.document.revision, self.controller.selection)
        if signature == self.signature:
            return
        self.signature = signature
        selected = "" if self.all else self.selected_owner()
        values = shortcut_operations.listing(session, selected, self.search)
        rows = [
            self.shortcut_row(v) if "reference" in v else driver_row(session, v) for v in values
        ]
        self.model.synchronize_records(rows if self.all or selected else [])
        self.editor.synchronize()

    def shortcut_row(self, value):
        try:
            descriptor = property_operations.get(self.controller.session, value["reference"])
            return self.row(value["id"], descriptor, value["label"])
        except ValueError as error:
            return missing_row(value, str(error))

    def row(self, key, value, label=""):
        document = self.controller.session.document
        owners = ", ".join(document.object(v).name for v in value["owners"])
        return qml(
            dict(
                numeric_row(value),
                key=key,
                label=label or value["label"],
                ownerLabel=owners or "Unassigned",
            )
        )

    @Slot(str)
    def discover(self, search):
        from anthroforge.core.numeric_properties import decode_reference
        from anthroforge.core.shortcuts import implicit_identity

        session = self.controller.session
        values = property_operations.discover(session, self.controller.selection, search)
        exposed = {v.id for v in session.document.shortcuts if v.exposed}
        rows = [self.row(implicit_identity(decode_reference(v["reference"])), v) for v in values]
        self.catalog.synchronize_records([dict(v, exposed=v["key"] in exposed) for v in rows])

    @Slot("QVariantMap", str, bool)
    def expose(self, reference, label, exposed):
        self.controller.run(
            "shortcut.expose", dict(reference=reference, label=label, exposed=exposed)
        )
        self.discover("")

    @Slot()
    def createDriver(self):
        key = self.controller.run("driver.create", {})
        if key:
            self.editor.select(key)

    @Slot(str)
    def hide(self, key):
        value = next(
            v for v in shortcut_operations.ordered(self.controller.session.document) if v.id == key
        )
        if hasattr(value, "reference"):
            self.expose(qml(value.reference), value.label, False)
        else:
            self.controller.run("driver.configure", dict(driver=key, changes=dict(exposed=False)))

    @Slot(str, int)
    def move(self, key, direction):
        order = [v.id for v in shortcut_operations.ordered(self.controller.session.document)]
        index = order.index(key)
        destination = max(0, min(len(order) - 1, index + direction))
        order.insert(destination, order.pop(index))
        self.controller.run("shortcut.reorder", dict(identities=order))

    @Slot(str, int, float, bool)
    def editValue(self, key, component, value, uniform):
        current = next(
            v for v in shortcut_operations.ordered(self.controller.session.document) if v.id == key
        )
        if hasattr(current, "reference"):
            args = dict(
                reference=qml(current.reference),
                value=value,
                uniform=uniform,
                component=component if component >= 0 else None,
            )
            self.controller.run("shortcut.set", args)
        else:
            self.controller.run("driver.value", dict(driver=key, value=value))


def numeric_row(value):
    values = value["value"] if isinstance(value["value"], (tuple, list)) else [value["value"]]
    return dict(
        reference=value["reference"],
        values=values,
        numericType=value["numeric_type"],
        dimension=value["dimension"],
        writable=value["writable"] and not value["driven_by"],
        reason=value["reason"] or ("Driven by a formula" if value["driven_by"] else ""),
        kind="PROPERTY",
    )


def missing_row(value, reason):
    return dict(
        key=value["id"],
        label=value["label"],
        reference=value["reference"],
        values=[],
        numericType="REAL",
        dimension="SCALAR",
        writable=False,
        reason=reason,
        ownerLabel="Missing property",
        kind="PROPERTY",
    )


def driver_row(session, value):
    owners = ", ".join(session.document.object(v).name for v in value["owners"])
    return dict(
        key=value["id"],
        label=value["label"],
        reference={},
        values=[value["value"]],
        numericType=value["numeric_type"],
        dimension=value["dimension"],
        writable=True,
        reason="Virtual driver value",
        ownerLabel=owners or "Unassigned",
        kind="DRIVER",
    )
