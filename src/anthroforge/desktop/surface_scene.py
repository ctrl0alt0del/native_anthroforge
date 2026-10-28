"""Construction meshes use the existing staged mesh display and picking model."""

from anthroforge.core.surfaces import Surface
from anthroforge.core.tissues import TissueVCP

from .presentation import geometry_flags


def metadata(session, item, row):
    if not isinstance(item, (Surface, TissueVCP)):
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
    return [
        r
        for r in controller.construction.records.values()
        if r.get("kind") in ("SURFACE", "MEMBRANE")
    ]


def preview_rows(controller):
    from anthroforge.application.previews import current

    value = controller.session.surface_preview
    if value.state != "ready" or value.asset is None or not current(controller.session, value):
        return []
    return [preview_record(controller.session, value)]


def preview_record(session, value):
    item, mesh = value.asset.surface, value.asset.mesh
    return preview_mesh(session, value, item, mesh)


def preview_mesh(session, value, item, mesh):
    return dict(
        id="preview:" + value.token,
        handle=mesh.handle,
        chunks=mesh.counts[4],
        geometry_asset=value.token,
        geometry_revision=0,
        **preview_placement(session, item),
        **preview_style(),
    )


def preview_placement(session, item):
    from anthroforge.application.curve_sources import world
    from anthroforge.native import construction, scene

    frame = construction.matrix(
        session.engine, world(session.engine, session.document, item.parent), item.matrix
    )
    return dict(
        matrix=list(frame),
        geometry_offset=[0, 0, 0],
        trs=session.engine.decompose(frame),
        quaternion=scene.quaternion(session.engine, frame),
    )


def preview_style():
    return dict(
        visible=True,
        pickable=False,
        readonly=False,
        opacity=0.55,
        color="#72da95",
        asset="",
        anchors=[],
        surface_visible=True,
        surface_pickable=False,
    )


def resources(controller):
    yield from (asset.mesh for asset in controller.session.assets.values())
    if controller.session.surface_preview.asset is not None:
        yield controller.session.surface_preview.asset.mesh
    if controller.session.tissue_preview.asset is not None:
        yield controller.session.tissue_preview.asset.mesh
    if controller.session.skin_fit_preview.asset is not None:
        yield controller.session.skin_fit_preview.asset.mesh


def tissue_preview_rows(controller):
    from anthroforge.application.previews import current

    from .mirror_scene import previews

    value = controller.session.tissue_preview
    if value.state != "ready" or value.asset is None or not current(controller.session, value):
        return []
    rows = [preview_mesh(controller.session, value, value.asset.item, value.asset.mesh)]
    return previews(controller, rows, value.target)
