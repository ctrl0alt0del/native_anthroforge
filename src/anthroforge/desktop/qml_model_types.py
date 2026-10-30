"""Model names are distinct from visual QML components and cannot create extra sessions."""

from PySide6.QtQml import qmlRegisterUncreatableType


def register(types):
    for kind in types:
        qmlRegisterUncreatableType(
            kind,
            "AnthroForge.Desktop",
            1,
            0,
            "Af" + kind.__name__,
            "Desktop models belong to their application session.",
        )
