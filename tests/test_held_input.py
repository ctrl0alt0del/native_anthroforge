from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent

from anthroforge.desktop.input_state import InputState


def key(state, pressed, code, modifiers=Qt.KeyboardModifier.NoModifier, repeat=False):
    kind = QEvent.Type.KeyPress if pressed else QEvent.Type.KeyRelease
    state.eventFilter(None, QKeyEvent(kind, code, modifiers, autorep=repeat))


def test_held_modifier_press_release_and_repeat():
    state = InputState()
    key(state, True, Qt.Key.Key_Shift)
    assert state.modifiers == Qt.KeyboardModifier.ShiftModifier.value
    key(state, False, Qt.Key.Key_Shift, repeat=True)
    assert state.modifiers == Qt.KeyboardModifier.ShiftModifier.value
    key(state, False, Qt.Key.Key_Shift, Qt.KeyboardModifier.ShiftModifier)
    assert state.modifiers == 0


def test_window_deactivation_clears_modifiers_and_cancels():
    state, canceled = InputState(), []
    state.canceled.connect(lambda: canceled.append(True))
    key(state, True, Qt.Key.Key_Control)
    assert state.modifiers == Qt.KeyboardModifier.ControlModifier.value
    state.eventFilter(None, QEvent(QEvent.Type.WindowDeactivate))
    assert state.modifiers == 0 and canceled == [True]


def button(state, pressed, code):
    kind = QEvent.Type.MouseButtonPress if pressed else QEvent.Type.MouseButtonRelease
    event = QMouseEvent(kind, QPointF(10, 10), QPointF(10, 10), code, code, Qt.NoModifier)
    return state.eventFilter(None, event)


def test_captured_reset_button_consumes_its_release_after_modifier_changes():
    state, resets = InputState(), []
    state.buttonCapture = Qt.MiddleButton.value
    state.buttonTriggered.connect(lambda: resets.append(True))
    assert not button(state, True, Qt.LeftButton)
    assert button(state, True, Qt.MiddleButton)
    state.buttonCapture = 0
    assert button(state, False, Qt.MiddleButton)
    assert not button(state, True, Qt.MiddleButton)
    assert resets == [True]
