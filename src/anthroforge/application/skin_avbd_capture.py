"""Serialize the dispatched anatomy in the qualified AVBD worker's input format."""

import json
import struct
from pathlib import Path
from typing import Any

import numpy as np

from anthroforge.core.mirroring import MirrorInstance
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import skin_capture, tissue_domain

from . import skin_stage_policy, surface_providers
from .skin_draft_build import DraftRequest

Stage = dict[str, Any]
SurfaceTable = dict[str, tuple[Any, Any, Any, int]]


def identity(source: Any) -> str:
    return MirrorInstance(source.owner, source.instance).id if source.instance else source.owner


def indexed_surfaces(capture: Any) -> SurfaceTable:
    table = {}
    v, f = 0, 0
    for row in capture.sources:
        count, _, _, triangles, _ = row.mesh.counts
        vertices = capture.geometry.vertices[v : v + count]
        # Store a view and offset. Rebase only the surface currently being serialized.
        faces = capture.geometry.triangles[f : f + triangles]
        table[identity(row.identity)] = (row.identity, vertices, faces, v)
        v, f = v + count, f + triangles
    return table


def write_meshes(path: Path, meshes: Any) -> None:
    with path.open("wb") as stream:
        stream.write(struct.pack("<i", len(meshes)))
        for vertices, triangles, first in meshes:
            stream.write(struct.pack("<ii", len(vertices), len(triangles)))
            np.ascontiguousarray(vertices, dtype="<f8").tofile(stream)
            np.ascontiguousarray(triangles - first, dtype="<i4").tofile(stream)


def ordered_rows(plan: Stage, key: str, defaults: list[str]) -> list[Stage]:
    rows: list[Stage] = plan.get(key, [{"id": value} for value in defaults])
    selected, actual = {row["id"] for row in rows}, set(defaults)
    if selected != actual or len(rows) != len(actual):
        raise ValueError(
            f"AVBD {key} source mismatch. Missing {actual - selected}, extra {selected - actual}"
        )
    return rows


def stage_lists(document: Any, table: SurfaceTable, plan: Stage) -> tuple[list[Stage], list[Stage]]:
    bones, tissues = skin_stage_policy.ordered_sources(document, table)
    if not bones:
        raise ValueError("AVBD draft construction needs an SCP root.")
    if "bones" in plan:
        if any(r.limb or r.build_mode != "INHERIT" for r in document.skin.contributors):
            raise ValueError("Developer plan conflicts with authored SCP skin settings.")
        rows = ordered_rows(plan, "bones", [key for key, _ in bones])
    else:
        rows = [
            dict(id=key, mode=p.mode, mode_owner=p.mode_owner, limb_owner=p.limb_owner)
            for key, p in bones
        ]
    return rows, ordered_rows(plan, "muscles", tissues)


def write_frame(folder: Path, root: Any, override: Any) -> None:
    if override is None:
        low, high = root.min(axis=0), root.max(axis=0)
        override = [*((low + high) * 0.5), np.linalg.norm(high - low)]
    frame = np.asarray(override, dtype="<f8")
    if frame.shape != (4,) or not np.isfinite(frame).all() or frame[3] <= 0:
        raise ValueError("AVBD normalization requires a finite XYZ center and positive scale.")
    frame.tofile(folder / "frame.bin")


def base_surface(request: DraftRequest, source: Any) -> Any:
    engine, cancel = request.engine, request.cancel
    ref = SurfaceReference(source.owner, "TISSUE_BASE", source.instance)
    provider = surface_providers.get(engine, request.document, request.resources.meshes, ref)
    mesh = provider.resource.mesh
    base = skin_capture.capture_sources(engine, [mesh], [0], [provider.frame], [(0, 0, 0)], cancel)
    return base.vertices, base.triangles, 0


def tissue_for_capture(request: DraftRequest, owner: str) -> TissueVCP:
    item = request.document.object(owner)
    if not isinstance(item, TissueVCP):
        raise ValueError(f"Expected a tissue contributor for {owner}.")
    if item.final_material and item.final_material.base != item.base_result.asset:
        raise ValueError(f"{item.name}: final material belongs to another base revision.")
    return item


def paired_base(request: DraftRequest, source: Any, target_faces: Any, vertices: Any) -> Any:
    base, faces, _ = base_surface(request, source)
    ref = SurfaceReference(source.owner, "TISSUE_FINAL", source.instance)
    assets = request.resources.meshes
    provider = surface_providers.get(request.engine, request.document, assets, ref)
    item = tissue_for_capture(request, source.owner)
    samples = tissue_domain.base_samples(provider.resource.mesh, base, request.cancel)
    if samples is not None:
        return samples, target_faces, 0
    if len(base) != len(vertices) or not np.array_equal(faces, target_faces):
        raise ValueError(f"{item.name}: missing base correspondence for the final tissue surface.")
    return base, faces, 0


def write_tissue(
    folder: Path, table: SurfaceTable, row: Stage, index: int, request: DraftRequest
) -> Stage:
    name = f"tissue-{index}"
    directory = folder / name
    directory.mkdir()
    source, vertices, triangles, first = table[row["id"]]
    base = paired_base(request, source, triangles - first, vertices)
    write_meshes(directory / "base.bin", [base])
    write_meshes(directory / "muscle.bin", [(vertices, triangles, first)])
    return dict(id=row["id"], name=name, assets=name, frames=row.get("frames", 63))


def stage(folder: Path, request: DraftRequest) -> None:
    plan = json.loads(request.document.skin.draft_settings.plan)
    table = indexed_surfaces(request.capture)
    bones, tissues = stage_lists(request.document, table, plan)
    if "bones" not in plan:
        bones = skin_stage_policy.compile_steps(request, bones, table)
    write_frame(folder, table[bones[0]["id"]][1], plan.get("normalization"))
    write_meshes(folder / "bones.bin", [table[row["id"]][1:] for row in bones])
    steps = [
        dict(route="follow") | row | dict(mesh_index=i, name=f"bone-{i}")
        for i, row in enumerate(bones)
    ]
    muscles = [write_tissue(folder, table, row, i, request) for i, row in enumerate(tissues)]
    recipe = dict(bones=steps, muscles=muscles, frame="frame.bin", meshes="bones.bin")
    (folder / "recipe.json").write_text(json.dumps(recipe, allow_nan=False), encoding="utf-8")
