"""Explicit desktop model composition; numerical operations remain in application services."""

from .construction_view import ConstructionView
from .mirror_view import MirrorView
from .project_view import ProjectView
from .runtime_view import RuntimeView
from .selection_view import SelectionView
from .viewport_view import ViewportView


def attach(controller):
    controller.project_view = ProjectView(controller)
    controller.selection_view = SelectionView(controller)
    controller.viewport_view = ViewportView(controller)
    controller.construction_view = ConstructionView(controller)
    controller.mirror_view = MirrorView(controller)
    controller.runtime_view = RuntimeView(controller)
