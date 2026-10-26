"""Skin stage-specific computation and dependency policies for one shared job lifecycle."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from . import skin_evaluation, skin_inputs, skin_topology_evaluation


@dataclass(frozen=True)
class Policy:
    title: str
    outputs: tuple[str, ...]
    inputs: Callable[[Any], Any]
    compute: Callable[..., Any]


def envelope(engine: Any, document: Any, resources: Any, cancel: Any) -> dict[str, Any]:
    return dict(envelope=skin_evaluation.evaluate(engine, document, resources, cancel.handle))


def topology(engine: Any, document: Any, resources: Any, cancel: Any) -> dict[str, Any]:
    key = document.skin.envelope.asset
    if not key:
        raise ValueError("Build a skin envelope before rebuilding topology.")
    mesh = resources.meshes[key].mesh
    return dict(
        topology=skin_topology_evaluation.evaluate(engine, document, resources, mesh, cancel)
    )


def construction(engine: Any, document: Any, resources: Any, cancel: Any) -> dict[str, Any]:
    output = envelope(engine, document, resources, cancel)
    output["topology"] = skin_topology_evaluation.evaluate(
        engine, document, resources, output["envelope"].mesh, cancel
    )
    return output


POLICIES = {
    "envelope": Policy("Build skin envelope", ("envelope",), skin_inputs.envelope, envelope),
    "topology": Policy("Build skin topology", ("topology",), skin_inputs.topology, topology),
    "construction": Policy(
        "Build skin and topology", ("envelope", "topology"), skin_inputs.construction, construction
    ),
}
