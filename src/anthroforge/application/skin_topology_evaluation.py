"""Owned topology stage; retained resources and accepted paths are never mutated."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.entities import IDENTITY
from anthroforge.native import skin_annuli, skin_symmetry

from . import (
    skin_assets,
    skin_capture,
    skin_density,
    skin_loop_capture,
    skin_remeshing,
    skin_topology_capture,
)
from .skin_evaluation import source_metadata
from .skin_results import ComputedStage


def plane(engine: Any, document: Any) -> Any:
    settings = document.skin.topology_settings
    if settings.symmetry == "NONE":
        return None
    matrix = next((row.matrix for row in document.entities if not row.parent), IDENTITY)
    origin, normal = settings.plane_origin, settings.plane_normal
    if settings.symmetry != "CUSTOM":
        origin = (0, 0, 0)
        normal = tuple(int(axis == settings.symmetry) for axis in "XYZ")
    return skin_symmetry.world_plane(engine, matrix, (*origin, *normal))


def evaluate(
    engine: Any, document: Any, resources: Any, envelope: Any, cancel: Any
) -> ComputedStage:
    frame = plane(engine, document)
    sources = skin_capture.capture(engine, document, resources, cancel.handle)
    loops = skin_loop_capture.capture(engine, document, resources, envelope, cancel, frame)
    guides = skin_topology_capture.capture(engine, document, resources, cancel)
    density = skin_density.evaluate(document, sources, envelope, cancel.handle)
    annuli = skin_annuli.build(envelope, loops.data, frame, cancel.handle)
    inputs = skin_remeshing.Inputs(
        envelope, annuli, density, guides.data, frame, document.skin.topology_settings
    )
    return solve(inputs, sources, loops, guides, cancel)


def solve(inputs: Any, sources: Any, loops: Any, guides: Any, cancel: Any) -> ComputedStage:
    try:
        output, backend, attempts = skin_remeshing.run(inputs, cancel)
        return complete(inputs, output, backend, attempts, sources, loops, guides)
    finally:
        inputs.annuli.close()


def arrays(inputs: Any, output: Any, loops: Any) -> dict[str, Any]:
    return dict(
        regions=output.topology.regions,
        guide_indices=output.topology.guides,
        transitions=output.transitions,
        density_lengths=inputs.density.density.lengths,
        density_regions=inputs.density.regions,
        loop_samples=loops.data.samples,
        loop_pairs=loops.data.pairs,
    )


def complete(
    inputs: Any, output: Any, backend: Any, attempts: Any, sources: Any, loops: Any, guides: Any
) -> ComputedStage:
    captures = (sources, loops, guides, inputs.density, backend)
    warnings = tuple(text for row in captures for text in row.warnings)
    warnings += (output.warning,) if output.warning else ()
    info = metadata(inputs, output, attempts, sources, loops, guides)
    info["warnings"] = list(dict.fromkeys(warnings))
    return ComputedStage(
        output.topology.mesh, skin_assets.create(arrays(inputs, output, loops), info)
    )


def metadata(
    inputs: Any, output: Any, attempts: Any, sources: Any, loops: Any, guides: Any
) -> dict[str, Any]:
    return details(inputs, output, attempts) | dict(
        sources=[source_metadata(row) for row in sources.sources],
        loops=[asdict(row.identity) for row in loops.sources],
        flow=[asdict(row.identity) for row in guides.sources],
    )


def details(inputs: Any, output: Any, attempts: Any) -> dict[str, Any]:
    return dict(
        kind="quad_topology",
        settings=asdict(inputs.settings),
        attempts=attempts,
        plane=None if inputs.plane is None else inputs.plane.tolist(),
        budgets=[asdict(row) for row in inputs.density.plan.regions],
        adaptive=inputs.density.adaptive,
        refinement=inputs.density.refinement,
        requested_quads=inputs.settings.target_quads,
        quads=output.topology.mesh.counts[1],
        reference_available=False,
    )
