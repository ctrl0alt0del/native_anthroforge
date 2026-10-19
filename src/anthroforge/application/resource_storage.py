"""Resource-specific package adapters; no native handles are serialized."""

import io
import zipfile
from dataclasses import asdict
from typing import Any

import numpy as np

from anthroforge.native import material, paths, tissue_domain, topology
from anthroforge.native.mesh import GeometryEngine
from anthroforge.native.routing import Report

from . import attachment_storage, image_assets, object_codec
from .assets import Asset
from .path_assets import PathAsset
from .resources import Resources

MESH_BUFFERS = ("vertices", "corners", "offsets", "triangles", "polygons")


def describe(resources: Resources) -> dict[str, Any]:
    return {
        "assets": {key: mesh_metadata(asset) for key, asset in resources.meshes.items()},
        "paths": {key: path_metadata(asset) for key, asset in resources.paths.items()},
        "images": {key: {"digest": image.digest} for key, image in resources.images.items()},
        "attachments": attachment_storage.describe(resources.attachments),
    }


def mesh_metadata(asset: Asset) -> dict[str, Any]:
    return {name: getattr(asset, name) for name in ("source", "digest", "units", "y_up")}


def path_metadata(asset: PathAsset) -> dict[str, Any]:
    return dict(
        authored=object_codec.encode(asset.authored),
        diagnostics=asdict(asset.diagnostics) if asset.diagnostics else None,
    )


def write_array(archive: zipfile.ZipFile, name: str, array: Any) -> None:
    with archive.open(name, "w", force_zip64=True) as stream:
        np.lib.format.write_array(stream, array, allow_pickle=False)  # type: ignore[no-untyped-call]


def read_array(archive: zipfile.ZipFile, name: str) -> Any:
    with archive.open(name) as stream:
        return np.load(io.BytesIO(stream.read()), allow_pickle=False)


def write(archive: zipfile.ZipFile, resources: Resources) -> None:
    for key, asset in resources.meshes.items():
        write_mesh(archive, key, asset)
    for key, curve in resources.paths.items():
        write_array(archive, f"paths/{key}/samples.npy", curve.path.array())
        write_array(archive, f"paths/{key}/parameters.npy", curve.path.array(1))
    for key, image in resources.images.items():
        archive.writestr(f"images/{key}/source", image.encoded)
    attachment_storage.write(archive, resources.attachments)


def write_mesh(archive: zipfile.ZipFile, key: str, asset: Asset) -> None:
    for kind, label in enumerate(MESH_BUFFERS):
        write_array(archive, f"assets/{key}/{label}.npy", asset.mesh.array(kind))
    write_array(archive, f"assets/{key}/material.npy", material.array(asset.mesh))
    write_array(archive, f"assets/{key}/material_axes.npy", material.axes(asset.mesh))
    for label, values in zip(
        ("tissue", "tissue_weights"), tissue_domain.arrays(asset.mesh), strict=True
    ):
        write_array(archive, f"assets/{key}/{label}.npy", values)


def read_mesh(archive: zipfile.ZipFile, key: str, source: Any, engine: GeometryEngine) -> Asset:
    arrays = [read_array(archive, f"assets/{key}/{label}.npy") for label in MESH_BUFFERS]
    mesh = topology.restore(engine, arrays)
    domain = read_array(archive, f"assets/{key}/material.npy")
    coordinates = read_array(archive, f"assets/{key}/material_axes.npy")
    mesh = material.restore(mesh, domain, parameters=coordinates)
    tissue = [
        read_array(archive, f"assets/{key}/{kind}.npy") for kind in ("tissue", "tissue_weights")
    ]
    return Asset(tissue_domain.restore(mesh, *tissue), **source)


def read_path(archive: zipfile.ZipFile, key: str, source: Any, engine: GeometryEngine) -> PathAsset:
    from anthroforge.core.construction import Curve

    authored = object_codec.decode(source["authored"])
    if not isinstance(authored, Curve):
        raise ValueError("Accepted path input must be a curve or fiber.")
    samples = read_array(archive, f"paths/{key}/samples.npy")
    parameters = read_array(archive, f"paths/{key}/parameters.npy")
    report = source["diagnostics"]
    diagnostics = Report(tuple(report["counters"]), tuple(report["measures"])) if report else None
    return PathAsset(
        paths.restore(engine, samples, parameters, authored.closed), authored, diagnostics
    )


def read_image(
    archive: zipfile.ZipFile, key: str, source: Any, engine: GeometryEngine
) -> image_assets.ImageAsset:
    image = image_assets.decode(archive.read(f"images/{key}/source"), engine)
    if image.digest != source["digest"]:
        raise ValueError("Embedded reference image digest does not match its assignment.")
    return image


def read(archive: zipfile.ZipFile, data: Any, engine: GeometryEngine) -> Resources:
    meshes = {key: read_mesh(archive, key, value, engine) for key, value in data["assets"].items()}
    curves = {key: read_path(archive, key, value, engine) for key, value in data["paths"].items()}
    images = {key: read_image(archive, key, value, engine) for key, value in data["images"].items()}
    attachments = {
        key: attachment_storage.read(archive, key, value, engine)
        for key, value in data.get("attachments", {}).items()
    }
    return Resources(meshes, curves, images, attachments)
