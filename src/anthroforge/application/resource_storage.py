"""Resource-specific package adapters; no native handles are serialized."""

import io
import zipfile
from typing import Any

import numpy as np

from anthroforge.native import paths, topology
from anthroforge.native.mesh import GeometryEngine

from . import image_assets, object_codec
from .assets import Asset
from .path_assets import PathAsset
from .resources import Resources

MESH_BUFFERS = ("vertices", "corners", "offsets", "triangles", "polygons")


def describe(resources: Resources) -> dict[str, Any]:
    return {
        "assets": {key: mesh_metadata(asset) for key, asset in resources.meshes.items()},
        "paths": {
            key: object_codec.encode(asset.authored) for key, asset in resources.paths.items()
        },
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
    for key, curve in resources.paths.items():
        write_array(archive, f"paths/{key}/samples.npy", curve.path.array())
        write_array(archive, f"paths/{key}/parameters.npy", curve.path.array(1))
    for key, image in resources.images.items():
        archive.writestr(f"images/{key}/source", image.encoded)


def read_mesh(archive: zipfile.ZipFile, key: str, source: Any, engine: GeometryEngine) -> Asset:
    arrays = [read_array(archive, f"assets/{key}/{label}.npy") for label in MESH_BUFFERS]
    return Asset(topology.restore(engine, arrays), **source)


def read_path(archive: zipfile.ZipFile, key: str, source: Any, engine: GeometryEngine) -> PathAsset:
    from anthroforge.core.construction import Curve

    authored = object_codec.decode(source)
    if not isinstance(authored, Curve):
        raise ValueError("Accepted path input must be a curve or fiber.")
    samples = read_array(archive, f"paths/{key}/samples.npy")
    parameters = read_array(archive, f"paths/{key}/parameters.npy")
    return PathAsset(paths.restore(engine, samples, parameters, authored.closed), authored)


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
    return Resources(meshes, curves, images)
