"""Decode one bounded preview on the inbox worker; a reusable fitted read-only canvas."""

from PySide6.QtCore import Property, QBuffer, QIODevice, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QImage, QImageReader, QPainter
from PySide6.QtQml import QmlElement
from PySide6.QtQuick import QQuickPaintedItem

QML_IMPORT_NAME = "AnthroForge.Feedback"
QML_IMPORT_MAJOR_VERSION = 1


def load_preview(inbox, key):
    detail = inbox.read(key)
    buffer = QBuffer()
    buffer.setData(detail.annotated_png)
    buffer.open(QIODevice.ReadOnly)
    reader = QImageReader(buffer, b"png")
    size = reader.size()
    if not size.isValid() or size.width() * size.height() > 100_000_000:
        raise ValueError("Report screenshot is invalid or exceeds the preview size limit.")
    reader.setScaledSize(size.scaled(QSize(4096, 4096), Qt.KeepAspectRatio).boundedTo(size))
    image = reader.read()
    if image.isNull():
        raise ValueError("Cannot read report screenshot: " + reader.errorString())
    return detail, image


@QmlElement
class ReportImage(QQuickPaintedItem):
    imageChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image = QImage()

    @Property(QImage, notify=imageChanged)
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value
        self.imageChanged.emit()
        self.update()

    def paint(self, painter):
        if self._image.isNull():
            return
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        size = self._image.size().scaled(int(self.width()), int(self.height()), Qt.KeepAspectRatio)
        area = QRectF(
            (self.width() - size.width()) / 2,
            (self.height() - size.height()) / 2,
            size.width(),
            size.height(),
        )
        painter.drawImage(area, self._image)
