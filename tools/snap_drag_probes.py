"""Opt-in diagnostic spans and counterfactuals; never imported by the application."""

from functools import wraps
from threading import get_ident
from time import perf_counter
from unittest.mock import patch

from PySide6.QtQml import QQmlEngine, QQmlExpression, QQmlProperty

from anthroforge.desktop import authoring_actions, curve_interaction, models
from anthroforge.desktop.authoring import Authoring
from anthroforge.desktop.controller import Controller


class Probes:
    def __init__(self):
        self.events, self.patches = [], []
        self.active = False

    def wrap(self, owner, name):
        original = getattr(owner, name)

        @wraps(original)
        def measured(*args, **kwargs):
            if not self.active:
                return original(*args, **kwargs)
            start, thread = perf_counter(), get_ident()
            try:
                return original(*args, **kwargs)
            finally:
                self.append(original.__qualname__, start, thread)

        return measured

    def append(self, name, start, thread):
        self.events.append(
            dict(name=name, start=start, duration=perf_counter() - start, thread=thread)
        )

    def install(self):
        groups = (
            (Controller, ("refresh", "notify", "activate_geometry")),
            (Authoring, ("refresh", "notify", "publish_geometry")),
            (authoring_actions, ("transform_delta", "apply_delta")),
            (curve_interaction, ("surface_hit", "surface_record")),
            (models.RenderModel, ("publish", "drain", "presented")),
        )
        for owner, names in groups:
            for name in names:
                replacement = patch.object(owner, name, self.wrap(owner, name))
                replacement.start()
                self.patches.append(replacement)

    def close(self):
        for replacement in reversed(self.patches):
            replacement.stop()

    def watch_activity(self, window):
        activity_view(window).modelChanged.connect(self.model_changed)

    def model_changed(self):
        if self.active:
            self.append("Activity.modelChanged", perf_counter(), get_ident())


def freeze_activity(controller):
    controller._state = controller.snapshot()
    controller.changed.emit()


def intervention(controller, window, name):
    if name == "freeze-activity":
        controller.notify = lambda: freeze_activity(controller)
    if name == "hide-feedback":
        from ui_acceptance import find

        assert QQmlProperty.write(find(window, "curveCursorMarker").parentItem(), "visible", False)
    if name == "empty-activity":
        assert QQmlProperty.write(activity_view(window), "model", [])
    if name == "restore-activity":
        restore_activity(window)


def restore_activity(window):
    view = activity_view(window)
    expression = QQmlExpression(
        QQmlEngine.contextForObject(view),
        view,
        "model = Qt.binding(function() { return workspace.activityModel; })",
    )
    expression.evaluate()
    assert not expression.hasError(), expression.error().toString()


def activity_view(window):
    activity = next(
        item
        for item in items(window.contentItem())
        if item.metaObject().className().startswith("Activity_")
    )
    return next(
        item for item in items(activity) if item.metaObject().className() == "QQuickListView"
    )


def items(item):
    yield item
    for child in item.childItems():
        yield from items(child)
