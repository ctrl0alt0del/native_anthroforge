"""Material fields retain their sampled-domain identity across geometry deformation."""

from typing import Any

from .field_domains import mesh_domain as mesh_domain


def domain(resources: Any, item: Any, name: str) -> tuple[int, str]:
    if name not in ("BASE", "REST"):
        raise ValueError("Field domain must be Base or Rest.")
    if name == "REST":
        return mesh_domain(resources.meshes[item.rest_result.asset].mesh)
    if item.base_state.kind == "SURFACE":
        return mesh_domain(resources.meshes[item.base_result.asset].mesh)
    if item.base_state.kind == "POINT":
        return 1, "point:1"
    path = resources.paths[item.base_result.asset].path
    return item.resolution, f"path:{item.resolution}:{int(path.closed)}"


def positions(session: Any, item: Any, name: str) -> Any:
    from anthroforge.native import components, paths

    domain(session.resources, item, name)
    if name == "REST":
        return session.assets[item.rest_result.asset].mesh.array(0)
    if item.base_state.kind == "SURFACE":
        return session.assets[item.base_result.asset].mesh.array(0)
    if item.base_state.kind == "POINT":
        return components.transformed(session.engine, [(0, 0, 0)], item.base_state.frame)
    path = session.resources.paths[item.base_result.asset].path
    return paths.sample(path, item.resolution, 0, 1, item.base_state.frame)[:, :3]


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
