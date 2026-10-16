"""GPU texture rendering through QQuickRenderControl; no native window is shown."""

import sys
from pathlib import Path

from PySide6.QtCore import QSize, QSizeF, QUrl
from PySide6.QtGui import (
    QImage,
    QRhiColorAttachment,
    QRhiReadbackDescription,
    QRhiReadbackResult,
    QRhiRenderBuffer,
    QRhiTexture,
    QRhiTextureRenderTargetDescription,
)
from PySide6.QtQml import QQmlComponent, QQmlEngine
from PySide6.QtQuick import (
    QQuickRenderControl,
    QQuickRenderTarget,
    QQuickWindow,
    QSGRendererInterface,
)

from .runtime import build_directory


class Offscreen:
    def __init__(self, controller, warnings):
        if sys.platform == "win32":
            QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.Direct3D11)
        self.control = QQuickRenderControl()
        self.window = QQuickWindow(self.control)
        self.engine = QQmlEngine()
        self.engine.addImportPath(str(build_directory() / "qml"))
        self.engine.rootContext().setContextProperty("workspace", controller)
        self.engine.warnings.connect(lambda errors: warnings.extend(e.toString() for e in errors))
        self.load_view()
        if not self.control.initialize():
            raise RuntimeError("Cannot initialize the offscreen GPU renderer.")
        self.rhi = self.control.rhi()
        self.create_buffers()
        self.create_target()

    def load_view(self):
        path = Path(__file__).parent / "qml/Viewport.qml"
        self.component = QQmlComponent(self.engine, QUrl.fromLocalFile(str(path)))
        self.root = self.component.create()
        if self.root is None:
            raise RuntimeError(str([e.toString() for e in self.component.errors()]))
        self.size = QSize(1280, 960)
        self.root.setSize(QSizeF(self.size))
        self.window.contentItem().setSize(QSizeF(self.size))
        self.window.setGeometry(0, 0, self.size.width(), self.size.height())
        self.root.setParentItem(self.window.contentItem())

    def create_buffers(self):
        flags = QRhiTexture.Flag.RenderTarget | QRhiTexture.Flag.UsedAsTransferSource
        self.texture = self.rhi.newTexture(QRhiTexture.Format.RGBA8, self.size, 1, flags)
        self.depth = self.rhi.newRenderBuffer(QRhiRenderBuffer.Type.DepthStencil, self.size, 1)
        if not self.texture.create() or not self.depth.create():
            raise RuntimeError("Cannot allocate offscreen GPU buffers.")

    def create_target(self):
        description = QRhiTextureRenderTargetDescription(QRhiColorAttachment(self.texture))
        description.setDepthStencilBuffer(self.depth)
        self.target = self.rhi.newTextureRenderTarget(description)
        self.render_pass = self.target.newCompatibleRenderPassDescriptor()
        self.target.setRenderPassDescriptor(self.render_pass)
        if not self.target.create():
            raise RuntimeError("Cannot create offscreen render target.")
        self.window.setRenderTarget(QQuickRenderTarget.fromRhiRenderTarget(self.target))

    def frame(self):
        self.control.polishItems()
        self.control.beginFrame()
        self.control.sync()
        self.control.render()
        result = QRhiReadbackResult()
        batch = self.rhi.nextResourceUpdateBatch()
        batch.readBackTexture(QRhiReadbackDescription(self.texture), result)
        self.control.commandBuffer().resourceUpdate(batch)
        self.control.endFrame()
        return self.readback_image(result)

    def readback_image(self, result):
        image = QImage(
            result.data.data(),
            self.size.width(),
            self.size.height(),
            QImage.Format.Format_RGBA8888_Premultiplied,
        )
        return image.mirrored() if self.rhi.isYUpInFramebuffer() else image.copy()

    def close(self):
        self.control.invalidate()
        for resource in (self.target, self.render_pass, self.depth, self.texture):
            resource.destroy()
