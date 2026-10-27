"""Reference-specific tissue policy and retained anatomical sample ownership."""

import json
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from anthroforge.core import skin_sources
from anthroforge.core.preferences import Preferences
from anthroforge.native import skin_support

from . import mirror_surfaces, skin_assets, skin_capture, skin_inputs, surface_providers
from .object_frames import Frames


@dataclass(frozen=True)
class Capture:
    data: skin_assets.SkinAsset
    sources: tuple[str, ...]


def source(engine: Any, document: Any, resources: Any, identity: Any, policy: str) -> Any:
    if identity.kind != "TISSUE" or policy == "FINISHED":
        return skin_capture.surface(engine, document, resources, identity)
    item = document.object(identity.owner)
    ref = skin_inputs.reference(identity)
    key = item.rest_material.rest if item.rest_material else ""
    surface_providers.require_ready(ref, item.rest_result, key, resources.meshes)
    frame = mirror_surfaces.frame(engine, document, ref, Frames(engine, document).world(item.id))
    return skin_capture.Source(identity, resources.meshes[key].mesh, frame, key)


def capture(engine: Any, document: Any, resources: Any, policy: str, cancel: int = 0) -> Capture:
    Preferences(skin_tissue_surface=policy)
    rows = tuple(
        source(engine, document, resources, row, policy)
        for row in skin_sources.contributors(document)
    )
    if not rows:
        raise ValueError("Skin deformation needs accepted SCP or tissue surfaces.")
    samples = tuple(skin_support.sample(row.mesh, row.frame, cancel) for row in rows)
    return assemble(engine, rows, samples, policy)


def assemble(engine: Any, rows: Any, samples: Any, policy: str) -> Capture:
    weights = skin_support.weights(engine, [s[2] for s in samples], [len(s[0]) for s in samples])
    arrays = {"samples": np.concatenate([s[1] for s in samples]), "sample_weights": weights}
    arrays.update({f"source_{i}_ids": sample[0] for i, sample in enumerate(samples)})
    metadata = dict(
        tissue_surface=policy, sources=[dict(asdict(r.identity), asset=r.asset) for r in rows]
    )
    return Capture(skin_assets.create(arrays, metadata), tuple(row.asset for row in rows))


def identities(document: Any, definitions: Any) -> Any:
    identities = tuple(
        skin_sources.Source(**{k: r[k] for k in ("owner", "kind", "instance")}) for r in definitions
    )
    if identities != skin_sources.contributors(document):
        raise ValueError("Skin contributors changed; rebuild the reference.")
    return identities


def targets(engine: Any, document: Any, resources: Any, reference: Any, cancel: int = 0) -> Any:
    metadata = json.loads(reference.metadata)
    definitions = metadata["sources"]
    rows = [
        source(engine, document, resources, row, metadata["tissue_surface"])
        for row in identities(document, definitions)
    ]
    arrays = reference.arrays
    outputs = [
        resolve(resources, row, definitions[i]["asset"], arrays[f"source_{i}_ids"], cancel)
        for i, row in enumerate(rows)
    ]
    return np.concatenate(outputs)


def resolve(resources: Any, row: Any, retained: str, ids: Any, cancel: int) -> Any:
    if retained not in resources.meshes:
        raise ValueError("Missing retained skin material reference; rebuild the reference.")
    return skin_support.targets(resources.meshes[retained].mesh, row.mesh, row.frame, ids, cancel)
