"""Searchable shortcut details; UI adapts values without defining formula semantics."""

from dataclasses import asdict

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.application import driving_operations, property_operations, shortcut_operations
from anthroforge.core.shortcuts import Shortcut

from .record_model import RecordModel
from .shortcut_policy_editor import ShortcutPolicyEditor
from .values import qml


class ShortcutEditor(QObject):
    changed = Signal()

    def __init__(self, panel):
        super().__init__(panel)
        self.panel, self.key, self.state = panel, "", {}
        self.policy_editor = ShortcutPolicyEditor(self)
        self.choices = RecordModel(self, ("key", "label", "reference", "driver"), "key")
        self.rows = RecordModel(
            self,
            ("formulaKey", "label", "expression", "inputs", "active", "status", "error"),
            "formulaKey",
        )

    @Property("QVariantMap", notify=changed)
    def details(self):
        return qml(self.state)

    @Property(QObject, constant=True)
    def targets(self):
        return self.choices

    @Property(QObject, constant=True)
    def formulas(self):
        return self.rows

    @Property(QObject, constant=True)
    def policies(self):
        return self.policy_editor

    @Slot(str)
    def select(self, key):
        self.key = key
        self.synchronize()

    def selected(self):
        document = self.panel.controller.session.document
        return next((v for v in shortcut_operations.ordered(document) if v.id == self.key), None)

    def synchronize(self):
        value = self.selected()
        updated = details(value)
        if updated != self.state:
            self.state = updated
            self.changed.emit()
        self.rows.synchronize_records(
            self.formula_rows(value) if updated.get("kind") == "DRIVER" else []
        )
        self.policy_editor.synchronize()

    def formula_rows(self, value):
        session = self.panel.controller.session
        results = {r.formula: r for r in session.document.formula_results}
        return [
            formula_row(session, formula, results.get(formula.id)) for formula in value.formulas
        ]

    @Slot(str, str)
    def discover(self, search, purpose):
        session = self.panel.controller.session
        values = property_operations.discover(session, search=search, values=False)
        rows = [
            row
            for value in values
            if purpose == "INPUT" or value["writable"]
            for row in property_choices(session, value)
        ]
        if purpose == "INPUT":
            rows.extend(driver_choices(session, search))
        self.choices.synchronize_records(rows)

    @Slot(str, "QVariant")
    def configure(self, field, value):
        current = self.selected()
        if current is None:
            return
        controller = self.panel.controller
        if isinstance(current, Shortcut):
            args = dict(
                reference=asdict(current.reference), label=str(value), exposed=current.exposed
            )
            controller.run("shortcut.expose", args)
        else:
            changes = typed_changes(current, field, value)
            controller.run("driver.configure", dict(driver=current.id, changes=changes))
        self.synchronize()

    @Slot("QVariantMap")
    def addFormula(self, reference):
        self.panel.controller.run(
            "driver.formula.add", dict(driver=self.key, target=reference, expression="value")
        )
        self.synchronize()

    @Slot(str, "QVariantMap")
    def updateFormula(self, formula, changes):
        self.panel.controller.run(
            "driver.formula.update", dict(driver=self.key, formula=formula, changes=changes)
        )
        self.synchronize()

    @Slot(str)
    def removeFormula(self, formula):
        self.panel.controller.run("driver.formula.remove", dict(driver=self.key, formula=formula))
        self.synchronize()

    @Slot(str, str, "QVariantMap", str)
    def addInput(self, formula, name, reference, driver):
        session = self.panel.controller.session
        value = driving_operations.formula_record(session, self.key, formula)
        entry = dict(name=name, property=reference) if reference else dict(name=name, driver=driver)
        self.updateFormula(formula, dict(inputs=[*(asdict(i) for i in value.inputs), entry]))

    @Slot(str, str)
    def removeInput(self, formula, name):
        value = driving_operations.formula_record(self.panel.controller.session, self.key, formula)
        self.updateFormula(
            formula, dict(inputs=[asdict(i) for i in value.inputs if i.name != name])
        )

    @Slot("QVariant")
    def setValue(self, value):
        self.panel.controller.run("driver.value", dict(driver=self.key, value=value))

    @Slot()
    def removeDriver(self):
        self.panel.controller.run("driver.remove", dict(driver=self.key))
        if self.selected() is None:
            self.select("")


def typed_changes(current, field, value):
    changes = {field: value}
    if field == "numeric_type" and value == "INTEGER" and float(current.value).is_integer():
        changes["value"] = int(current.value)
    return changes


def formula_row(session, formula, result):
    descriptor = property_operations.get(session, asdict(formula.target))
    owner = session.document.object(formula.target.target).name
    return qml(
        dict(
            formulaKey=formula.id,
            label=owner + " / " + component_label(descriptor),
            expression=formula.expression,
            inputs=[asdict(i) for i in formula.inputs],
            active=formula.enabled,
            status=result.status if result else "pending",
            error=result.error if result else "",
        )
    )


def property_choices(session, value):
    reference, rows = value["reference"], []
    count = value["components"]
    owner = session.document.object(reference["target"]).name
    for component in range(count):
        ref = dict(reference, component=component if count > 1 else None)
        label = owner + " / " + component_label(dict(value, reference=ref))
        rows.append(dict(key=repr(ref), label=label, reference=ref, driver=""))
    return rows


def component_label(value):
    component = value["reference"].get("component")
    if component is None or value["components"] == 1:
        return value["label"]
    axis = "XYZ"[component] if value["components"] == 3 else str(component + 1)
    return value["label"] + " · " + axis


def details(value):
    if value is None:
        return {}
    return dict(
        asdict(value),
        kind="PROPERTY" if isinstance(value, Shortcut) else "DRIVER",
        id=value.id,
        valueText=str(value.value) if hasattr(value, "value") else "",
    )


def driver_choices(session, search):
    return [
        dict(key=d.id, label=d.label + " · Driver", reference={}, driver=d.id)
        for d in session.document.driving_shortcuts
        if search.casefold() in d.label.casefold()
    ]
