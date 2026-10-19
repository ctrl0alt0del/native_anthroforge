"""Fitted source-pixel annotation canvas; painting and hit mapping share one transform."""

from PySide6.QtCore import Property, QRectF, Signal, Slot
from PySide6.QtQml import QmlElement
from PySide6.QtQuick import QQuickPaintedItem

from .feedback_editor import FeedbackEditor
from .feedback_paint import paint

QML_IMPORT_NAME = "AnthroForge.Feedback"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class FeedbackCanvas(QQuickPaintedItem):
    editorChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._editor = None
        self.setAntialiasing(True)

    @Property(FeedbackEditor, notify=editorChanged)
    def editor(self):
        return self._editor

    @editor.setter
    def editor(self, value):
        if self._editor is not None:
            self._editor.changed.disconnect(self.update)
        self._editor = value
        if value is not None:
            value.changed.connect(self.update)
        self.editorChanged.emit()
        self.update()

    def placement(self):
        if self._editor is None or self._editor.image.isNull():
            return QRectF(), 1.0
        image = self._editor.image
        scale = min(self.width() / image.width(), self.height() / image.height())
        width, height = image.width() * scale, image.height() * scale
        return QRectF(
            (self.width() - width) / 2, (self.height() - height) / 2, width, height
        ), scale

    def paint(self, painter):
        area, scale = self.placement()
        if area.isEmpty():
            return
        painter.translate(area.left(), area.top())
        painter.scale(scale, scale)
        editor = self._editor
        items = (*editor.annotations, editor.preview) if editor.preview else editor.annotations
        paint(painter, editor.image, items)

    @Slot(float, float, str, str, result=bool)
    def begin(self, x, y, kind, text):
        area, scale = self.placement()
        if not area.contains(x, y) or scale <= 0:
            return False
        return self._editor.begin((x - area.x()) / scale, (y - area.y()) / scale, kind, text, scale)

    @Slot(float, float)
    def extend(self, x, y):
        area, scale = self.placement()
        if area.isEmpty():
            return
        x = max(area.left(), min(x, area.right()))
        y = max(area.top(), min(y, area.bottom()))
        self._editor.extend((x - area.x()) / scale, (y - area.y()) / scale)
