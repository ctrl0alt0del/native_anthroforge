"""One QPainter implementation for source-resolution exports and fitted editor previews."""

from dataclasses import replace

from PySide6.QtCore import QBuffer, QIODevice, QLineF, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen

COLOR = QColor("#ff3434")


def paint(painter, image, annotations):
    painter.setRenderHint(QPainter.Antialiasing)
    painter.drawImage(QPointF(0, 0), image)
    for item in annotations:
        painter.setPen(QPen(COLOR, item.stroke, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        draw_annotation(painter, item, image.size())


def draw_annotation(painter, item, size):
    start, end = QPointF(item.x1, item.y1), QPointF(item.x2, item.y2)
    if item.kind == "rectangle":
        painter.drawRect(QRectF(start, end).normalized())
    elif item.kind == "arrow":
        arrow(painter, start, end, item.stroke)
    elif item.kind == "text":
        font = QFont("Segoe UI")
        font.setPixelSize(round(item.font_size))
        font.setBold(True)
        painter.setFont(font)
        bounds = QRectF(item.x1, item.y1, size.width() - item.x1, size.height() - item.y1)
        painter.drawText(bounds, Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, item.text)


def arrow(painter, start, end, stroke):
    painter.drawLine(start, end)
    direction = QLineF(end, start)
    length = min(direction.length() * 0.45, stroke * 4)
    for angle in (-28, 28):
        head = QLineF(direction)
        head.setLength(length)
        head.setAngle(direction.angle() + angle)
        painter.drawLine(head)


def annotated(image, annotations):
    result = QImage(image.size(), QImage.Format_ARGB32_Premultiplied)
    result.fill(Qt.transparent)
    painter = QPainter(result)
    try:
        paint(painter, image, annotations)
    finally:
        painter.end()
    return result


def png(image):
    buffer = QBuffer()
    buffer.open(QIODevice.WriteOnly)
    if not image.save(buffer, "PNG"):
        raise ValueError("Could not encode the report screenshot.")
    return bytes(buffer.data())


def prepare(report, image):
    return replace(
        report, original_png=png(image), annotated_png=png(annotated(image, report.annotations))
    )
