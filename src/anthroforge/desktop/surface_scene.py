"""Construction meshes use the existing staged mesh display and picking model."""

from anthroforge.core.surfaces import Surface

from .presentation import geometry_flags


def metadata(session, item, row):
    if not isinstance(item, Surface):
        return {}
    asset = session.resources.meshes.get(item.result.asset)
    mesh = asset.mesh if asset else None
    return dict(
        handle=mesh.handle if mesh else 0,
        chunks=mesh.counts[4] if mesh else 0,
        geometry_asset=item.result.asset,
        opacity=0.08 if row["readonly"] else 1.0,
        anchors=[],
        color="#c9a8bc",
        **geometry_flags(session.workspace, row),
    )


def records(controller):
    return [row for row in controller.construction.records.values() if row.get("kind") == "SURFACE"]
