"""One-off authoring batch using the shared formula validators and driver installer."""

from dataclasses import replace

from anthroforge.application import driving_operations, shortcut_codec


class FormulaBatch:
    def __init__(self, session):
        self.session, self.pending = session, {}

    def __getattr__(self, name):
        return getattr(self.session, name)

    def command(self, operation, **arguments):
        if operation != "driver.formula.add":
            return self.session.command(operation, **arguments)
        driver = arguments.pop("driver")
        arguments["inputs"] = arguments.get("inputs") or []
        record = shortcut_codec.formula(arguments)
        driving_operations.validate_formula(self.session, record)
        self.pending.setdefault(driver, []).append(record)
        return record.id

    def flush(self):
        for identity, formulas in self.pending.items():
            before = driving_operations.selected(self.session, identity)
            driving_operations.install(
                self.session, replace(before, formulas=(*before.formulas, *formulas))
            )
            print("Installed", len(formulas), "formulas for", before.label, flush=True)
        self.pending.clear()
