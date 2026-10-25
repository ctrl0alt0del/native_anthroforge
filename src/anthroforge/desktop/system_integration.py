"""Explicit desktop setup actions, independent of document state and preferences data."""

import sys
from pathlib import Path

from PySide6.QtCore import Property, QObject, QUrl, Slot
from PySide6.QtGui import QDesktopServices

from . import windows_associations


def packaged_executable() -> Path:
    return Path(__file__).resolve().parents[2] / "AnthroForge.exe"


def unavailable(executable: Path) -> str:
    if sys.platform != "win32":
        return "File association setup is available on Windows."
    if not executable.is_file():
        return "Open the packaged AnthroForge app to set file associations."
    return ""


class SystemIntegration(QObject):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.executable = controller, packaged_executable()

    @Property(str, constant=True)
    def associationUnavailable(self):
        return unavailable(self.executable)

    @Slot()
    def setupAssociation(self):
        try:
            reason = unavailable(self.executable)
            if reason:
                raise ValueError(reason)
            target = windows_associations.register(self.executable)
            if not QDesktopServices.openUrl(QUrl(target)):
                raise OSError("Open Windows Settings → Apps → Default apps and choose AnthroForge.")
            self.controller.message = "In Windows Settings, choose AnthroForge for .anthroforge."
        except (OSError, ValueError) as error:
            self.controller.message = str(error)
        self.controller.notify()
