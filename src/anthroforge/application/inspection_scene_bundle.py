"""Numerical inspection payloads preserve native connectivity without retriangulation."""

import json
from pathlib import Path
from typing import Any

import numpy as np

from anthroforge.core.inspection_layers import Layer
from anthroforge.native import paths, topology

from . import inspection_snapshots, report_archive
from .query_projection import plain


def write(root: Path, snapshot: Any, view: Any, cancel: Any) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    layers = [write_layer(root, layer, i, cancel) for i, layer in enumerate(snapshot.layers)]
    result = metadata(snapshot, view, layers)
    (root / "inspection.json").write_text(
        json.dumps(result, indent=2, allow_nan=False), encoding="utf-8"
    )
    return result


def metadata(snapshot: Any, view: Any, layers: Any) -> dict[str, Any]:
    return dict(
        schema_version=2,
        format="anthroforge-inspection",
        snapshot=snapshot.identity,
        candidate_kind=snapshot.kind,
        token=snapshot.token,
        document=snapshot.document,
        revision=snapshot.revision,
        view=view,
        layers=layers,
        input_revisions=plain(snapshot.provenance),
    )


def write_layer(root: Path, layer: Layer, index: int, cancel: Any) -> dict[str, Any]:
    result = inspection_snapshots.metadata(layer)
    for name, description in result["buffers"].items():
        report_archive.check(cancel)
        path = f"geometry/{index}/{name}.npy"
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        np.save(root / path, inspection_snapshots.array(layer, name), allow_pickle=False)
        description["file"] = path
    return result


def read(root: Path, engine: Any) -> tuple[dict[str, Any], tuple[Layer, ...]]:
    data = json.loads((root / "inspection.json").read_text(encoding="utf-8"))
    if data.get("format") != "anthroforge-inspection" or data.get("schema_version") != 2:
        raise ValueError("Unsupported inspection scene format.")
    return data, tuple(read_layer(root, engine, row) for row in data["layers"])


def read_layer(root: Path, engine: Any, row: Any) -> Layer:
    options = {key: row[key] for key in Layer.__dataclass_fields__ if key in row}
    options.update(
        identity=row["id"], frame=tuple(row["frame"]), resource=restore(root, engine, row)
    )
    options["provenance"] = tuple(row.get("provenance", {}).items())
    return Layer(**options)


def restore(root: Path, engine: Any, row: Any) -> Any:
    if row["kind"] == "MESH":
        names = inspection_snapshots.MESH_BUFFERS
        return topology.restore(engine, [read_buffer(root, row, name) for name in names])
    if row["kind"] == "PATH":
        return paths.restore(
            engine,
            read_buffer(root, row, "samples"),
            read_buffer(root, row, "parameters"),
            row["closed"],
        )
    return None


def read_buffer(root: Path, row: Any, name: str) -> Any:
    path = (root / row["buffers"][name]["file"]).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Inspection buffer path escapes its scene bundle.")
    return np.load(path, allow_pickle=False)
