"""Incremental shortcut presentation and on-demand numerical property discovery."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import property_operations, shortcut_operations
from anthroforge.application.shortcut_ownership import property_owners
from anthroforge.core.numeric_properties import decode_reference
from anthroforge.core.shortcuts import implicit_identity

from .quantity_values import QuantityValues, texts
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
    "statusText",
)


class ShortcutPanel(QObject):
    changed = Signal()
    revealRequested = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.active, self.all, self.search = False, False, ""
        self.signature = None
        self.display_revision = 0
        self.model = RecordModel(self, FIELDS, "key")
        self.catalog = RecordModel(self, (*FIELDS, "exposed"), "key")
        self.editor = ShortcutEditor(self)
        self.quantities = QuantityValues(self)

    def display_changed(self):
        self.display_revision += 1
        self.synchronize()
        self.editor.inspection.changed.emit()

    @Property(QObject, constant=True)
    def quantityValues(self):
        return self.quantities

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
        if not active:
            self.editor.inspection.clear()
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
        self.editor.inspection.synchronize()
        signature = self.current_signature(session)
        if signature == self.signature:
            return
        self.signature = signature
        self.refresh_rows()
        self.editor.synchronize()

    def current_signature(self, session):
        return (
            session,
            session.document.revision,
            self.controller.selection,
            session.shortcut_observation.serial,
            self.display_revision,
        )

    def refresh_rows(self):
        from .shortcut_inspection_view import badge

        session = self.controller.session
        selected = "" if self.all else self.selected_owner()
        values = shortcut_operations.listing(session, selected, self.search)
        rows = [
            self.shortcut_row(v) if "reference" in v else driver_row(session, v) for v in values
        ]
        rows = [dict(row, statusText=badge(self, row["key"])) for row in rows]
        self.model.synchronize_records(rows if self.all or selected else [])

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
                statusText="",
            )
        )

    @Slot(str)
    def discover(self, search):
        from anthroforge.core.numeric_properties import decode_reference
        from anthroforge.core.shortcuts import implicit_identity

        session = self.controller.session
        values = discover_for_panel(self, search)
        exposed = {v.id for v in session.document.shortcuts if v.exposed}
        rows = [self.row(implicit_identity(decode_reference(v["reference"])), v) for v in values]
        self.catalog.synchronize_records([dict(v, exposed=v["key"] in exposed) for v in rows])

    @Slot("QVariantMap", str, bool)
    def expose(self, reference, label, exposed):
        self.controller.run(
            "shortcut.expose", dict(reference=reference, label=label, exposed=exposed)
        )
        self.discover("")

    @Slot("QVariantMap", int, result="QVariantMap")
    def propertyState(self, reference, revision):
        try:
            return property_state(self.controller.session, reference)
        except (ValueError, KeyError):
            return dict(writable=False, reason="Property is unavailable", exposed=False)

    @Slot("QVariantMap")
    def openDriver(self, reference):
        key = self.propertyState(reference, 0).get("driver", "")
        if key:
            self.editor.select(key)
            self.revealRequested.emit()

    @Slot("QVariantMap", int, result=str)
    def propertyText(self, reference, revision):
        try:
            return str(property_operations.get(self.controller.session, reference)["value"])
        except (ValueError, KeyError):
            return ""

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

    @Slot(str, str, bool)
    def place(self, key, target, after):
        order = [v.id for v in shortcut_operations.ordered(self.controller.session.document)]
        if key == target or key not in order or target not in order:
            return
        original = list(order)
        order.remove(key)
        order.insert(order.index(target) + int(after), key)
        if order != original:
            self.controller.run("shortcut.reorder", dict(identities=order))

    @Slot(str, int, "QVariant", bool)
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
        values=texts(values, value["numeric_type"]),
        numericType=value["numeric_type"],
        dimension=value["dimension"],
        writable=value["writable"],
        reason=value["reason"] or ("Driven by a formula" if value["driven_by"] else ""),
        kind="PROPERTY",
    )


def discover_for_panel(panel, search):
    session = panel.controller.session
    selection = panel.controller.selection
    if panel.all:
        return property_operations.discover(session, search=search)
    owner = panel.selected_owner()
    targets = [
        key
        for key in session.document.registry.records
        if key == selection or owner and owner in property_owners(session.document, key)
    ]
    return [row for key in targets for row in property_operations.discover(session, key, search)]


def property_state(session, reference):
    value = property_operations.get(session, reference)
    key = implicit_identity(decode_reference(reference))
    driver = controlling_driver(session.document, value["driven_by"])
    return dict(
        writable=value["writable"] and driver is None,
        reason=value["reason"] or ("Driven by " + driver.label if driver else ""),
        exposed=any(s.id == key and s.exposed for s in session.document.shortcuts),
        driver=driver.id if driver else "",
        formula=value["driven_by"],
    )


def controlling_driver(document, formula):
    return next(
        (d for d in document.driving_shortcuts if any(f.id == formula for f in d.formulas)),
        None,
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
        values=texts([value["value"]], value["numeric_type"]),
        numericType=value["numeric_type"],
        dimension=value["dimension"],
        writable=True,
        reason="Virtual driver value",
        ownerLabel=owners or "Unassigned",
        kind="DRIVER",
    )
