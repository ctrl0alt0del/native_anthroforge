"""Shortcuts operation declarations; common execution lives in command_execution."""

from .. import driving_operations, property_operations, shortcut_operations
from ..command_contracts import direct, edit, query
from ..shortcut_inspection import operations

COMMANDS = (
    edit("driver.create", driving_operations.create),
    edit("driver.configure", driving_operations.configure),
    edit("driver.value", driving_operations.set_value),
    edit("driver.remove", driving_operations.remove),
    edit("driver.formula.add", driving_operations.add_formula),
    edit("driver.formula.update", driving_operations.update_formula),
    edit("driver.formula.remove", driving_operations.remove_formula),
    edit("property.set", property_operations.set_value),
    edit("shortcut.expose", shortcut_operations.expose),
    edit("shortcut.configure", shortcut_operations.configure),
    edit("shortcut.set", shortcut_operations.set_value),
    edit("shortcut.reorder", shortcut_operations.reorder),
    direct("driver.inspect", lambda session, **a: driving_operations.inspect(session, **a)),
    query("property.discover", property_operations.discover),
    query("property.get", property_operations.get),
    query("shortcut.inspect", shortcut_operations.inspect),
    query("shortcut.list", shortcut_operations.listing),
    *(query(name, handler) for name, handler in operations().items()),
)
