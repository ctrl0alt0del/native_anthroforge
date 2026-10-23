"""Read-only native binding diagnostics on saved skeletal-edit failures."""

import json
import sys
from contextlib import closing
from dataclasses import asdict
from pathlib import Path

import numpy as np

from anthroforge.application import surface_providers
from anthroforge.application.projects import adopt
from anthroforge.application.resource_storage import MESH_BUFFERS
from anthroforge.application.session import Session
from anthroforge.application.storage import read_package
from anthroforge.core.fibers import Fiber
from anthroforge.native import material, material_basis, tissue_domain, triangle_material


def rejected(provider, meshes, reference, records, indices):
    try:
        surface_providers.binding_frames(provider, meshes, reference, records, 0)
        return []
    except ValueError as error:
        if len(records) == 1:
            return [(int(indices[0]), str(error))]
        split = len(records) // 2
        return rejected(provider, meshes, reference, records[:split], indices[:split]) + rejected(
            provider, meshes, reference, records[split:], indices[split:]
        )


def mesh_data(mesh):
    output = {name: mesh.array(i) for i, name in enumerate(MESH_BUFFERS)}
    output.update(material=material.array(mesh), axes=material.axes(mesh))
    for names, values in (
        (("basis", "parameters"), material_basis.arrays(mesh)),
        (("origins", "coordinates"), triangle_material.arrays(mesh)),
        (("tissue", "tissue_weights"), tissue_domain.arrays(mesh)),
    ):
        output.update(zip(names, values, strict=True))
    return output


def failure_rows(field, slots, failed):
    return [
        dict(
            node=int(slots[i, 0]),
            influence=int(slots[i, 1]),
            weight=float(field.weights[tuple(slots[i])]),
            kind="path" if slots[i, 0] < field.path.count else "control",
            record=field.bindings[tuple(slots[i])].tolist(),
            error=error,
        )
        for i, error in failed
    ]


def inspect_target(session, fiber, asset, index, target, output):
    field = asset.field
    provider, slots, records = target_records(session, field, target, index)
    failed = rejected(
        provider, session.assets, target.material_asset, records, np.arange(len(records))
    )
    if not failed:
        return None
    prefix = save_geometry(session, fiber, index, target, provider, output)
    parent = session.document.object(target.reference.target)
    return target_report(parent, target, provider, field, slots, failed, prefix)


def target_records(session, field, target, index):
    provider = surface_providers.get(
        session.engine, session.document, session.assets, target.reference
    )
    slots = np.argwhere((field.owners == index) & (field.weights > 0))
    return provider, slots, field.bindings[slots[:, 0], slots[:, 1]]


def save_geometry(session, fiber, index, target, provider, output):
    prefix = output / (fiber.id + "-" + str(index))
    np.savez_compressed(
        str(prefix) + "-before.npz", **mesh_data(session.assets[target.material_asset].mesh)
    )
    np.savez_compressed(str(prefix) + "-after.npz", **mesh_data(provider.resource.mesh))
    return str(prefix)


def target_report(parent, target, provider, field, slots, failed, prefix):
    return dict(
        target=asdict(target),
        parent=parent.name,
        current=provider.asset_id,
        total=len(slots),
        failed=failure_rows(field, slots, failed),
        geometry_files=prefix,
        parent_definition=asdict(parent),
    )


def inspect_fiber(session, fiber, output):
    asset = session.resources.attachments[fiber.attachment_asset]
    targets = [
        inspect_target(session, fiber, asset, i, target, output)
        for i, target in enumerate(asset.targets)
    ]
    return dict(
        fiber=fiber.name,
        identity=fiber.id,
        bindings=[asdict(b) for b in fiber.bindings],
        path_count=asset.field.path.count,
        point_ids=[p.id for p in fiber.points],
        targets=[t for t in targets if t is not None],
    )


def run(project, output):
    output.mkdir(parents=True, exist_ok=True)
    with closing(Session()) as session:
        adopt(session, *read_package(project, session.engine))
        fibers = [v for v in session.document.objects if isinstance(v, Fiber) and v.result.error]
        result = [inspect_fiber(session, fiber, output) for fiber in fibers]
        (output / "diagnosis.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print_summary(result)


def print_summary(result):
    for fiber in result:
        counts = [(t["parent"], t["total"], len(t["failed"])) for t in fiber["targets"]]
        print(fiber["fiber"], counts, flush=True)


if __name__ == "__main__":
    run(*(Path(v) for v in sys.argv[1:3]))
