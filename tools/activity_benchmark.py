"""Modal G-transform counterpart of the drag benchmark; uses production input paths."""

import numpy as np
from curve_interaction_acceptance import screen
from primitive_acceptance import settle
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from snap_drag_diagnostic import DragTrial
from ui_acceptance import find
from view_gesture_acceptance import position


class ModalTrial(DragTrial):
    def begin(self):
        self.before = position(self.controller, self.point_id)
        find(self.window, "viewport").forceActiveFocus()
        QTest.mouseMove(self.window, screen(self.window, self.before))
        QTest.keyClick(self.window, Qt.Key_G)
        if self.snapping:
            QTest.keyPress(self.window, Qt.Key_Control)
        QTest.qWait(200)
        assert find(self.window, "modalTransform").property("active")
        self.frames.clear()
        self.controller.session.scheduler.metrics.samples.clear()
        self.jobs = len(self.controller.session.scheduler.jobs)

    def finish(self):
        assert self.controller.session.history.before is not None
        if self.snapping:
            QTest.keyRelease(self.window, Qt.Key_Control)
        QTest.keyClick(self.window, Qt.Key_Return)
        settle(self.controller)
        self.controller.run("undo", {})
        settle(self.controller)
        np.testing.assert_allclose(position(self.controller, self.point_id), self.before, atol=1e-8)
        self.window.frameSwapped.disconnect(self.frame)
        self.deleteLater()
