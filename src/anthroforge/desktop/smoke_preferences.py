"""Read-only packaged style/registration inspection; no registry writes or OS launches."""

from PySide6.QtCore import QMetaObject, QObject, QTimer
from PySide6.QtQml import QQmlEngine, QQmlExpression

from .windows_associations import entries


def evaluate(item, expression):
    value = QQmlExpression(QQmlEngine.contextForObject(item), item, expression)
    result, _ = value.evaluate()
    if value.hasError():
        raise RuntimeError(value.error().toString())
    return result


def show(window, controller):
    dialog = window.findChild(QObject, "preferencesDialog")
    assert dialog is not None and QMetaObject.invokeMethod(dialog, "open")
    button = window.findChild(QObject, "preferencesFileAssociation")
    evaluate(button, "ToolTip.show(hint, 60000)")
    QTimer.singleShot(700, lambda: inspect(controller, button))


def inspect(controller, button):
    adapter = controller.system_integration
    tooltip = evaluate(button, "ToolTip.toolTip")
    controller.smoke_preferences = dict(
        executable=str(adapter.executable),
        enabled=button.property("enabled"),
        registration=entries(adapter.executable) if not adapter.associationUnavailable else [],
        tooltip=tooltip.objectName(),
        visible=tooltip.property("visible"),
        width=tooltip.property("width"),
        lines=tooltip.property("contentItem").property("lineCount"),
    )
