"""Window-local held input state, independent of semantic action bindings."""

from PySide6.QtCore import Property, QEvent, QObject, Qt, Signal, Slot

MODIFIER_KEYS = {
    Qt.Key.Key_Shift: Qt.KeyboardModifier.ShiftModifier.value,
    Qt.Key.Key_Control: Qt.KeyboardModifier.ControlModifier.value,
    Qt.Key.Key_Alt: Qt.KeyboardModifier.AltModifier.value,
    Qt.Key.Key_Meta: Qt.KeyboardModifier.MetaModifier.value,
}


class InputState(QObject):
    changed = Signal()
    canceled = Signal()
    wheelTurned = Signal(float)
    buttonTriggered = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._modifiers = 0
        self._wheel_capture, self._button_capture, self._pressed_capture = False, 0, 0

    @Property(bool)
    def wheelCapture(self):
        return self._wheel_capture

    @wheelCapture.setter
    def wheelCapture(self, value):
        self._wheel_capture = value

    @Property(int)
    def buttonCapture(self):
        return self._button_capture

    @buttonCapture.setter
    def buttonCapture(self, value):
        self._button_capture = value

    @Property(int, notify=changed)
    def modifiers(self):
        return self._modifiers

    def set_modifiers(self, value):
        if value != self._modifiers:
            self._modifiers = value
            self.changed.emit()

    @Slot()
    def clear(self):
        self.set_modifiers(0)

    def eventFilter(self, watched, event):
        kind = event.type()
        if kind in (QEvent.Type.WindowDeactivate, QEvent.Type.Hide):
            self.clear()
            self.canceled.emit()
        elif kind in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease) and not event.isAutoRepeat():
            self.key_event(event, kind == QEvent.Type.KeyPress)
        return self.pointer_event(event)

    def pointer_event(self, event):
        if event.type() == QEvent.Type.Wheel and self._wheel_capture:
            amount = event.angleDelta().y() / 120 or event.pixelDelta().y() / 40
            self.wheelTurned.emit(amount)
            return True
        return self.button_event(event)

    def button_event(self, event):
        kind = event.type()
        if kind == QEvent.Type.MouseButtonPress and event.button().value == self._button_capture:
            self._pressed_capture = self._button_capture
            self.buttonTriggered.emit()
            return True
        if kind == QEvent.Type.MouseButtonRelease and event.button().value == self._pressed_capture:
            self._pressed_capture = 0
            return True
        return False

    def key_event(self, event, pressed):
        mask = event.modifiers().value
        bit = MODIFIER_KEYS.get(event.key(), 0)
        self.set_modifiers(mask | bit if pressed else mask & ~bit)
