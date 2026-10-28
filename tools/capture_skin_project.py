"""Freeze every accepted SCP/VCP contributor without recalculating or saving the project."""

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import asdict, astuple
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile

import numpy as np

from anthroforge.application import (
    resource_storage,
    skin_capture,
    skin_storage,
    storage,
    worker_memory,
)
from anthroforge.application.resources import Resources
from anthroforge.core import skin_sources
from anthroforge.core.results import geometry_asset
from anthroforge.native.mesh import GeometryEngine


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def load_resources(archive, manifest, document, engine):
    resources = Resources()
    for row in skin_sources.contributors(document):
        item = document.object(row.owner)
        key = geometry_asset(item) if row.kind == "SCP" else item.final_result.asset
        if key not in resources.meshes:
            resources.meshes[key] = resource_storage.read_mesh(
                archive, key, manifest["assets"][key], engine
            )
    resources.skin.update(skin_storage.read(archive, manifest.get("skin_assets", {})))
    return resources


def source_metadata(document, row):
    item = document.object(row.identity.owner)
    result = item.result if row.identity.kind == "SCP" else item.final_result
    return dict(
        **asdict(row.identity),
        name=item.name,
        asset=row.asset,
        vertices=row.mesh.counts[0],
        triangles=row.mesh.counts[3],
        revision=result.revision,
        status=result.status,
        error=result.error,
    )


def save(options, document, captured, started):
    arrays = dict(vars(captured.geometry), collagen=captured.collagen)
    arrays["settings"] = np.array(astuple(document.skin.envelope_settings))
    options.output.mkdir(parents=True, exist_ok=True)
    np.savez(options.output / "inputs.npz", **arrays)
    report = describe(options, document, captured, arrays)
    report["load_and_capture_seconds"] = perf_counter() - started
    path = options.output / "capture.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "sources"}), flush=True)


def describe(options, document, captured, arrays):
    return dict(
        project=str(options.project.resolve()),
        project_sha256=file_digest(options.project),
        sources=[source_metadata(document, row) for row in captured.sources],
        counts=dict(Counter(row.identity.kind for row in captured.sources)),
        mirror_instances=sum(bool(row.identity.instance) for row in captured.sources),
        settings=asdict(document.skin.envelope_settings),
        warnings=captured.warnings,
        **geometry_metadata(captured.geometry, arrays),
    )


def geometry_metadata(geometry, arrays):
    return dict(
        vertices=len(geometry.vertices),
        triangles=len(geometry.triangles),
        bytes=sum(a.nbytes for a in arrays.values()),
        budget=worker_memory.budget(),
        available_memory=worker_memory.available(),
    )


def file_digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    options, engine, started = arguments(), GeometryEngine(), perf_counter()
    with ZipFile(options.project) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        document = storage.decode_document(manifest["document"])
        resources = load_resources(archive, manifest, document, engine)
        captured = skin_capture.capture(engine, document, resources)
        save(options, document, captured, started)


if __name__ == "__main__":
    main()
