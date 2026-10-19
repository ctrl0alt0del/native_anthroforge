"""Packaged inbox qualification deletes only a copied QA report in its own directory."""

import shutil

from PySide6.QtCore import QMetaObject, QObject, Qt

from anthroforge.feedback.local_inbox import LocalReportInbox


class ReportBrowserProbe:
    def __init__(self, controller, window, source, directory):
        self.browser, self.window = controller.report_browser, window
        directory.mkdir(parents=True, exist_ok=True)
        self.path = directory / source.name
        shutil.copyfile(source, self.path)
        self.browser.inbox = LocalReportInbox(directory)
        self.phase = "preview"
        self.invoke("feedbackDialog", "close")
        self.invoke("reportBrowserDialog", "open")

    def invoke(self, name, signal):
        target = self.window.findChild(QObject, name)
        if target is None or not QMetaObject.invokeMethod(target, signal, Qt.DirectConnection):
            raise RuntimeError("Missing packaged report control: " + name)

    def poll(self):
        if self.browser.state["busy"]:
            return False
        if self.browser.state["error"]:
            raise RuntimeError(self.browser.state["error"])
        if self.phase == "preview":
            self.edit_text()
            return False
        if self.phase == "edited":
            assert self.browser.description == "Portable report text updated."
            self.inspect()
            return False
        assert self.browser.state["count"] == 0 and not self.path.exists()
        self.invoke("reportsClose", "clicked")
        return True

    def edit_text(self):
        assert self.browser.description and not self.browser.image.isNull()
        self.invoke("reportEditText", "clicked")
        self.window.findChild(QObject, "reportDescription").setProperty(
            "text", "Portable report text updated."
        )
        self.invoke("reportEditSave", "clicked")
        self.phase = "edited"

    def inspect(self):
        assert self.browser.description and not self.browser.image.isNull()
        assert self.browser.state["count"] == 1
        assert self.window.grabWindow().save(str(self.path.parent / "browser.png"))
        self.invoke("reportsDelete", "clicked")
        self.invoke("reportDeleteCancel", "clicked")
        assert self.path.exists()
        self.invoke("reportsDelete", "clicked")
        self.invoke("reportDeleteConfirm", "clicked")
        self.phase = "deleted"
