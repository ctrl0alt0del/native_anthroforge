"""Skin stage-specific computation and dependency policies for one shared job lifecycle."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from . import skin_evaluation, skin_inputs, skin_reference_evaluation, skin_topology_evaluation
from .skin_results import IncompleteBuild


@dataclass(frozen=True)
class Policy:
    title: str
    outputs: tuple[str, ...]
    inputs: Callable[[Any], Any]
    compute: Callable[..., Any]


def envelope(
    engine: Any, document: Any, resources: Any, cancel: Any, options: Any = None
) -> dict[str, Any]:
    return dict(envelope=skin_evaluation.evaluate(engine, document, resources, cancel.handle))


def topology(
    engine: Any, document: Any, resources: Any, cancel: Any, options: Any = None
) -> dict[str, Any]:
    key = document.skin.envelope.asset
    if not key:
        raise ValueError("Build a skin envelope before rebuilding topology.")
    mesh = resources.meshes[key].mesh
    return dict(
        topology=skin_topology_evaluation.evaluate(engine, document, resources, mesh, cancel)
    )


def construction(
    engine: Any, document: Any, resources: Any, cancel: Any, options: Any = None
) -> dict[str, Any]:
    output = envelope(engine, document, resources, cancel)
    try:
        finish_construction((engine, document, resources), output, cancel, options)
    except Exception as error:
        if cancel.is_set():
            raise
        raise IncompleteBuild(output, error) from error
    return output


def finish_construction(
    context: tuple[Any, Any, Any], output: Any, cancel: Any, options: Any
) -> None:
    output["topology"] = skin_topology_evaluation.evaluate(
        *context, output["envelope"].mesh, cancel
    )
    output["final"] = skin_reference_evaluation.initialize(
        *context, output["topology"].mesh, cancel, options.skin_tissue_surface
    )


def reference(
    engine: Any, document: Any, resources: Any, cancel: Any, options: Any
) -> dict[str, Any]:
    from .skin_status import pending_reason

    if reason := pending_reason(document):
        raise ValueError(reason)
    key = document.skin.pending_topology.asset or document.skin.topology.asset
    if not key or key not in resources.meshes:
        raise ValueError("Build skin topology before initializing its deformation reference.")
    output = skin_reference_evaluation.initialize(
        engine, document, resources, resources.meshes[key].mesh, cancel, options.skin_tissue_surface
    )
    return {"final": output}


POLICIES = {
    "reference": Policy(
        "Prepare skin reference", ("final",), skin_inputs.reference_build, reference
    ),
    "envelope": Policy("Build skin envelope", ("envelope",), skin_inputs.envelope, envelope),
    "topology": Policy("Build skin topology", ("topology",), skin_inputs.topology, topology),
    "construction": Policy(
        "Build skin", ("envelope", "topology", "final"), skin_inputs.complete_build, construction
    ),
}
