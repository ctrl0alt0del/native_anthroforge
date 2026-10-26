"""Registration of skin-stage ABI boundaries on the shared geometry engine."""

from typing import Any

from . import (
    process,
    skin_capture,
    skin_density,
    skin_fields,
    skin_flow,
    skin_gaps,
    skin_guides,
    skin_ownership,
)


def configure(engine: Any) -> None:
    for module in (
        process,
        skin_capture,
        skin_density,
        skin_fields,
        skin_flow,
        skin_gaps,
        skin_guides,
        skin_ownership,
    ):
        module.configure(engine)
