"""Desktop draft/capture adapter; delivery is injected and never touches document history."""

import json
from dataclasses import replace
from datetime import UTC, datetime
from functools import partial
from uuid import uuid4

from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices, QImage

from anthroforge import __version__
from anthroforge.feedback.records import Annotation, Report
from anthroforge.feedback.service import ReportService
from anthroforge.feedback.storage import LocalReportConsumer
from anthroforge.profiling.identity import build_identity

from . import feedback_comparison


class FeedbackEditor(QObject):
    changed = Signal()
    ready = Signal()

    def __init__(self, controller, consumer=None):
        super().__init__(controller)
        self.controller = controller
        self.service = ReportService(consumer if consumer is not None else LocalReportConsumer())
        self.image, self.annotations, self.preview = QImage(), (), None
        self.active, self.capturing, self.error = False, False, ""
        self.id, self.created_at, self.context_json = "", "", "{}"
        self.comparison, self.include_comparison, self.include_replay = None, True, False
        self.timer = QTimer(self)
        self.timer.setInterval(40)
        self.timer.timeout.connect(self.poll)

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(
            active=self.active,
            busy=self.capturing or self.service.future is not None,
            count=len(self.annotations),
            error=self.error or self.service.error,
            saved=self.service.state == "saved",
            location=self.service.location,
            width=self.image.width(),
            height=self.image.height(),
            destination=self.service.consumer.description,
            comparison=self.comparison is not None,
        )

    @Slot(QObject)
    def request(self, window):
        if self.active:
            return
        self.active, self.capturing, self.error = True, True, ""
        self.changed.emit()
        QTimer.singleShot(0, partial(self.capture, window))

    def capture(self, window):
        try:
            image = window.grabWindow()
            if image.isNull():
                raise ValueError("The application window could not be captured. Try again.")
            self.begin_draft(image)
            self.ready.emit()
        except Exception as error:
            self.active = False
            self.image = QImage()
            self.controller.message = "Screenshot failed: " + str(error)
            self.controller.notify()
        finally:
            self.capturing = False
            self.changed.emit()

    def begin_draft(self, image):
        self.service.reset()
        self.image = QImage(image)
        self.image.setDevicePixelRatio(1)  # All annotations address actual stored pixels.
        self.annotations, self.preview = (), None
        self.id, self.created_at = uuid4().hex, datetime.now(UTC).isoformat()
        self.context_json = json.dumps(capture_context(self.controller), allow_nan=False)
        self.comparison = feedback_comparison.capture(self.controller)
        self.include_comparison, self.include_replay = True, False
        self.error, self.active = "", True

    def editable(self):
        return self.active and not self.capturing and self.service.state not in ("saving", "saved")

    def begin(self, x, y, kind, text, scale):
        if not self.editable() or kind not in ("rectangle", "arrow", "text"):
            return False
        if kind == "text" and not text.strip():
            self.error = "Enter the annotation text, then click the image to place it."
            self.changed.emit()
            return False
        self.error = ""
        self.preview = Annotation(kind, x, y, x, y, text[:2000], 3 / scale, 18 / scale)
        self.changed.emit()
        return True

    def extend(self, x, y):
        if self.preview is not None and self.editable():
            self.preview = replace(self.preview, x2=x, y2=y)
            self.changed.emit()

    @Slot()
    def finishStroke(self):
        item = self.preview
        if item is not None and self.editable() and meaningful(item):
            self.annotations = (*self.annotations, item)
        self.cancelStroke()

    @Slot()
    def cancelStroke(self):
        self.preview = None
        self.changed.emit()

    @Slot()
    def undoAnnotation(self):
        if self.editable():
            self.annotations = self.annotations[:-1]
            self.cancelStroke()

    @Slot()
    def clearAnnotations(self):
        if self.editable():
            self.annotations = ()
            self.cancelStroke()

    @Slot(str, str)
    def submit(self, category, description):
        if not self.editable():
            return
        if category not in ("bug", "recommendation") or not description.strip():
            self.error = "Add a description before saving the report."
            self.changed.emit()
            return
        self.error = ""
        report = self.envelope(category, description.strip())
        self.service.start(self.prepare_report(report))
        self.timer.start()
        self.changed.emit()

    def prepare_report(self, report):
        return partial(
            feedback_comparison.prepare_report,
            report,
            QImage(self.image),
            self.comparison,
            self.include_comparison,
            self.include_replay,
        )

    @Slot(bool, bool)
    def comparisonOptions(self, included, replay):
        self.include_comparison, self.include_replay = included, replay

    def envelope(self, category, description):
        return Report(
            self.id,
            self.created_at,
            category,
            description,
            self.context_json,
            self.image.width(),
            self.image.height(),
            self.annotations,
            b"",
            b"",
        )

    def poll(self):
        if self.service.poll():
            self.timer.stop()
            self.changed.emit()

    @Slot()
    def dismiss(self):
        if self.service.future is not None or self.capturing:
            return
        self.active, self.error = False, ""
        self.image, self.annotations, self.preview = QImage(), (), None
        self.comparison = None
        self.changed.emit()

    @Slot()
    def showReport(self):
        if self.service.receipt.reveal:
            QDesktopServices.openUrl(QUrl(self.service.receipt.reveal))

    def close(self):
        self.timer.stop()
        self.service.close()


def meaningful(item):
    if item.kind == "text":
        return True
    width, height = abs(item.x2 - item.x1), abs(item.y2 - item.y1)
    return (
        min(width, height) >= item.stroke
        if item.kind == "rectangle"
        else max(width, height) >= item.stroke
    )


def capture_context(controller):
    session = controller.session
    return dict(
        application_version=__version__,
        build=build_identity(),
        document_id=str(session.document.id),
        document_revision=session.document.revision,
        project_path=str(session.path or ""),
        selected_object=controller.selection,
        display="Application window before report editor; may include provisional or pending state",
    )
