"""Application-wide attached tooltip style with unchanged Basic controls as fallback."""

from PySide6.QtQuickControls2 import QQuickStyle


def configure() -> None:
    QQuickStyle.setFallbackStyle("Basic")
    QQuickStyle.setStyle("AnthroForgeStyle")
