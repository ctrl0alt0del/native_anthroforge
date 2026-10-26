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
    skin_proximity,
    skin_proxy,
    skin_topology,
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
        skin_proximity,
        skin_proxy,
        skin_topology,
    ):
        module.configure(engine)
