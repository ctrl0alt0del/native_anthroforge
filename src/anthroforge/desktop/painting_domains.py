"""Field-specific policies for the shared weight-painting gesture."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from anthroforge.application import skin_collagen, tissue_painting

from . import skin_painting_view, tissue_painting_view
from .tissue_inspection_tools import displayed_stage


@dataclass(frozen=True)
class Domain:
    kind: str
    commit: str
    validate: Callable[..., Any]
    prepare: Callable[..., Any]
    capture: Callable[..., Any]


def tissue_validate(controller, name):
    tissue_painting.field(controller.session, controller.selection, dict(name=name))


def tissue_prepare(controller):
    tool = controller.tissue_inspection
    tool.hideStacking()
    stage = displayed_stage(controller.session, controller.selection)
    tool.set_view(stage, "", "Overlay")


def collagen_validate(controller, name):
    controller.session.editable(controller.selection)
    skin_collagen.mesh(controller.session, controller.selection)


def collagen_prepare(controller):
    controller.tissue_inspection.clear()


TISSUE = Domain(
    "paint",
    "tissue.field.paint.commit",
    tissue_validate,
    tissue_prepare,
    tissue_painting_view.capture,
)
COLLAGEN = Domain(
    "collagen",
    "skin.collagen.paint.commit",
    collagen_validate,
    collagen_prepare,
    skin_painting_view.capture,
)
