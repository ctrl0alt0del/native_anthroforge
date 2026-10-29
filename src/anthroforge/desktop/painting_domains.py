"""Field-specific policies for the shared weight-painting gesture."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from . import skin_painting_view, tissue_painting_view
from .tissue_inspection_tools import displayed_stage


@dataclass(frozen=True)
class Domain:
    kind: str
    consumer: str
    validate: Callable[..., Any]
    prepare: Callable[..., Any]
    capture: Callable[..., Any]


def tissue_validate(controller, name):
    require(
        controller,
        "tissue_weights",
        name=name,
        stage=displayed_stage(controller.session, controller.selection),
    )


def tissue_prepare(controller):
    tool = controller.tissue_inspection
    tool.hideStacking()
    stage = displayed_stage(controller.session, controller.selection)
    tool.set_view(stage, "", "Overlay")


def collagen_validate(controller, name):
    require(controller, "collagen")


def require(controller, consumer, **options):
    value = controller.session.command(
        "painting.describe", consumer=consumer, target=controller.selection, **options
    )
    if not value["available"]:
        raise ValueError(value["reason"])


def collagen_prepare(controller):
    controller.tissue_inspection.clear()


TISSUE = Domain(
    "paint",
    "tissue_weights",
    tissue_validate,
    tissue_prepare,
    tissue_painting_view.capture,
)
COLLAGEN = Domain(
    "collagen",
    "collagen",
    collagen_validate,
    collagen_prepare,
    skin_painting_view.capture,
)
