"""Registration of skin-stage ABI boundaries on the shared geometry engine."""

from typing import Any

from . import (
    process,
    skin_annuli,
    skin_capture,
    skin_density,
    skin_fields,
    skin_flow,
    skin_gaps,
    skin_guides,
    skin_loops,
    skin_ownership,
    skin_proximity,
    skin_proxy,
    skin_stitch,
    skin_symmetry,
    skin_topology,
)

MODULES = (
    process,
    skin_annuli,
    skin_capture,
    skin_density,
    skin_fields,
    skin_flow,
    skin_gaps,
    skin_guides,
    skin_loops,
    skin_ownership,
    skin_proximity,
    skin_proxy,
    skin_stitch,
    skin_symmetry,
    skin_topology,
)


def configure(engine: Any) -> None:
    for module in MODULES:
        module.configure(engine)
