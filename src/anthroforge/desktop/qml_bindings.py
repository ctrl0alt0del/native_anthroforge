"""One typed model composition per QML engine, with explicit QObject ownership."""

from PySide6.QtQml import QQmlEngine

from .app_models import App


def bind(engine, controller, inputs=None):
    if hasattr(engine, "anthroforge_models"):
        raise ValueError("The QML engine already has application models.")
    model = App(controller, inputs, engine)
    QQmlEngine.setObjectOwnership(model, QQmlEngine.ObjectOwnership.CppOwnership)
    engine.anthroforge_models = model
    return model
