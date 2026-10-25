"""Local editor presentation, independent of authored projects and their undo history."""

from PySide6.QtCore import Property, QObject, QSettings, Signal, Slot

from anthroforge.application.preferences import user_path


class WorkbenchState(QObject):
    changed = Signal()

    def __init__(self, parent=None, path=None):
        super().__init__(parent)
        self.settings = QSettings(
            str(path or user_path().with_name("workbench.ini")), QSettings.IniFormat
        )

    @Slot(str, result=str)
    def page(self, category):
        value = self.settings.value("pages/" + category, "Shape")
        return value if value in ("Shape", "Shortcuts", "Inspect") else "Shape"

    @Slot(str, str)
    def setPage(self, category, page):
        if page in ("Shape", "Shortcuts", "Inspect"):
            self.settings.setValue("pages/" + category, page)

    @Slot(str, bool, result=bool)
    def expanded(self, key, default):
        return self.settings.value("sections/" + key, default, type=bool)

    @Slot(str, bool)
    def setExpanded(self, key, value):
        self.settings.setValue("sections/" + key, value)

    @Slot(str, int, result=int)
    def paneWidth(self, name, default):
        try:
            return max(195, min(500, int(self.settings.value("panes/" + name, default))))
        except (ValueError, TypeError):
            return default

    @Slot(int, int)
    def savePanes(self, navigation, inspector):
        self.settings.setValue("panes/navigation", navigation)
        self.settings.setValue("panes/inspector", inspector)

    @Property(bool, notify=changed)
    def focusEditor(self):
        return self.settings.value("focusEditor", False, type=bool)

    @Slot(bool)
    def setFocusEditor(self, value):
        self.settings.setValue("focusEditor", value)
        self.changed.emit()
