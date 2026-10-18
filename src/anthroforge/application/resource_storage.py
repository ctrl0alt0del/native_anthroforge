"""Resource-specific package adapters; no native handles are serialized."""

import io
import zipfile
from typing import Any

import numpy as np

from anthroforge.native import paths, topology
from anthroforge.native.mesh import GeometryEngine

from . import image_assets
from .assets import Asset
from .resources import Resources

MESH_BUFFERS = ("vertices", "corners", "offsets", "triangles", "polygons")


def describe(resources: Resources) -> dict[str, Any]:
    return {
        "assets": {key: mesh_metadata(asset) for key, asset in resources.meshes.items()},
        "paths": {key: {"closed": path.closed} for key, path in resources.paths.items()},
        "images": {key: {"digest": image.digest} for key, image in resources.images.items()},
    }


def mesh_metadata(asset: Asset) -> dict[str, Any]:
    return {name: getattr(asset, name) for name in ("source", "digest", "units", "y_up")}


def write_array(archive: zipfile.ZipFile, name: str, array: Any) -> None:
    with archive.open(name, "w", force_zip64=True) as stream:
        np.lib.format.write_array(stream, array, allow_pickle=False)  # type: ignore[no-untyped-call]


def read_array(archive: zipfile.ZipFile, name: str) -> Any:
    with archive.open(name) as stream:
        return np.load(io.BytesIO(stream.read()), allow_pickle=False)


def write(archive: zipfile.ZipFile, resources: Resources) -> None:
    for key, asset in resources.meshes.items():
        for kind, label in enumerate(MESH_BUFFERS):
            write_array(archive, f"assets/{key}/{label}.npy", asset.mesh.array(kind))
    for key, path in resources.paths.items():
        write_array(archive, f"paths/{key}/samples.npy", path.array())
        write_array(archive, f"paths/{key}/parameters.npy", path.array(1))
    for key, image in resources.images.items():
        archive.writestr(f"images/{key}/source", image.encoded)


def read_mesh(archive: zipfile.ZipFile, key: str, source: Any, engine: GeometryEngine) -> Asset:
    arrays = [read_array(archive, f"assets/{key}/{label}.npy") for label in MESH_BUFFERS]
    return Asset(topology.restore(engine, arrays), **source)


def read_path(
    archive: zipfile.ZipFile, key: str, source: Any, engine: GeometryEngine
) -> paths.Path:
    samples = read_array(archive, f"paths/{key}/samples.npy")
    parameters = read_array(archive, f"paths/{key}/parameters.npy")
    return paths.restore(engine, samples, parameters, source["closed"])


def read_image(archive: zipfile.ZipFile, key: str, source: Any) -> image_assets.ImageAsset:
    image = image_assets.decode(archive.read(f"images/{key}/source"))
    if image.digest != source["digest"]:
        raise ValueError("Embedded reference image digest does not match its assignment.")
    return image


def read(archive: zipfile.ZipFile, data: Any, engine: GeometryEngine) -> Resources:
    meshes = {key: read_mesh(archive, key, value, engine) for key, value in data["assets"].items()}
    curves = {key: read_path(archive, key, value, engine) for key, value in data["paths"].items()}
    images = {key: read_image(archive, key, value) for key, value in data["images"].items()}
    return Resources(meshes, curves, images)
