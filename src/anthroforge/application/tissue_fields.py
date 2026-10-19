"""Material fields retain their sampled-domain identity across geometry deformation."""

from hashlib import sha256
from struct import pack
from typing import Any

from anthroforge.native import material


def mesh_domain(mesh: Any) -> tuple[int, str]:
    digest = sha256(pack("<q", mesh.counts[0]))
    for kind in (1, 2):
        digest.update(memoryview(mesh.array(kind)))
    digest.update(memoryview(material.axes(mesh)))
    return mesh.counts[0], digest.hexdigest()


def domain(resources: Any, item: Any, name: str) -> tuple[int, str]:
    if name == "REST":
        return mesh_domain(resources.meshes[item.rest_result.asset].mesh)
    if item.base_state.kind == "SURFACE":
        return mesh_domain(resources.meshes[item.base_result.asset].mesh)
    if item.base_state.kind == "POINT":
        return 1, "point:1"
    path = resources.paths[item.base_result.asset].path
    return item.resolution, f"path:{item.resolution}:{int(path.closed)}"


def validate(resources: Any, item: Any, name: str) -> None:
    fields = [f for f in item.fields if f.domain == name]
    if not fields:
        return
    count, signature = domain(resources, item, name)
    for field in fields:
        if len(field.values) != count or field.topology != signature:
            raise ValueError(
                f"Field '{field.name}' no longer matches its {name.lower()} topology. "
                "Remove or explicitly replace its weights before evaluation."
            )
