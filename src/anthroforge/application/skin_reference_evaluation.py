"""Immutable deformation initialization, retained sampling and native identity replay."""

import json
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import numpy as np

from anthroforge.core.skin import DeformationSettings
from anthroforge.native import skin_contact, skin_deformation, skin_support

from . import skin_assets, skin_support_capture, skin_topology_evaluation, tetrahedral_backend
from .skin_results import ComputedStage


def geometry(mesh: Any) -> dict[str, Any]:
    names = "vertices", "corners", "offsets", "triangles", "polygons"
    return {name: mesh.array(i) for i, name in enumerate(names)} | dict(
        vertex_ids=np.arange(mesh.counts[0], dtype=np.int64)
    )


def symmetry(engine: Any, document: Any, mesh: Any, cancel: int) -> dict[str, Any]:
    plane = skin_topology_evaluation.plane(engine, document)
    partners, error = skin_contact.symmetry(engine, mesh.array(0), plane, cancel)
    return dict(
        symmetry_plane=np.zeros(6) if plane is None else plane,
        symmetry_partners=partners,
        symmetry_error=np.array([error]),
    )


def proxy(mesh: Any, settings: Any, cancel: Any) -> skin_assets.SkinAsset:
    with TemporaryDirectory(prefix="anthroforge-skin-proxy-") as folder:
        return tetrahedral_backend.run(mesh, settings.proxy_resolution, Path(folder), cancel)


def initialize(
    engine: Any, document: Any, resources: Any, mesh: Any, cancel: Any, policy: str
) -> ComputedStage:
    support = skin_support_capture.capture(engine, document, resources, policy, cancel.handle)
    settings = document.skin.deformation_settings
    volume = proxy(mesh, settings, cancel)
    arrays = geometry(mesh) | dict(volume.arrays) | dict(support.data.arrays)
    arrays.update(symmetry(engine, document, mesh, cancel.handle))
    info = json.loads(support.data.metadata) | dict(
        settings=asdict(settings), kind="skin_reference"
    )
    info["proxy"] = json.loads(volume.metadata)
    return prepare(engine, mesh, arrays, info, support.sources, cancel.handle)


def prepare(
    engine: Any, mesh: Any, arrays: Any, info: Any, sources: Any, cancel: int
) -> ComputedStage:
    settings = DeformationSettings(**info["settings"])
    solver = skin_deformation.Preparation(engine, arrays, settings, cancel)
    try:
        output = accept_reference(engine, mesh, arrays, info, sources, solver, cancel)
        assert output.reference is not None
        skin_deformation.remember(engine, output.reference.digest, settings, solver)
        return output
    except BaseException:
        solver.close()
        raise


def accept_reference(
    engine: Any, mesh: Any, arrays: Any, info: Any, sources: Any, solver: Any, cancel: int
) -> ComputedStage:
    replay, diagnostics, _ = solver.solve(arrays["samples"], cancel)
    info["identity_error"] = skin_support.validate_replay(engine, arrays["vertices"], replay)
    arrays["embedding_ids"], arrays["embedding_weights"] = solver.embedding()
    reference = skin_assets.create(arrays, info)
    data = skin_assets.create(
        dict(solver_diagnostics=diagnostics),
        dict(kind="final_skin", reference=reference.digest, warnings=[]),
    )
    return ComputedStage(mesh, data, reference, sources)
