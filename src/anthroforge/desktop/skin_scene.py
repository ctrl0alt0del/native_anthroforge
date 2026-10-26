"""Document skin uses existing staged mesh leases without an authored hierarchy node."""

from anthroforge.core.entities import IDENTITY


def displayed(session):
    mode = session.workspace.skin_display
    names = ("final", "topology", "envelope") if mode == "AUTO" else (mode.lower(),)
    return next(
        (
            getattr(session.document.skin, name)
            for name in names
            if name != "none" and getattr(session.document.skin, name).asset
        ),
        None,
    )


def rows(controller):
    session = controller.session
    stage = displayed(session)
    if stage is None or stage.asset not in session.assets:
        return []
    mesh = session.assets[stage.asset].mesh
    return [record(session.document, stage, mesh)]


def record(document, stage, mesh):
    return dict(
        id="skin:" + str(document.id),
        handle=mesh.handle,
        chunks=mesh.counts[4],
        geometry_asset=stage.asset,
        geometry_revision=stage.revision,
        asset=stage.asset,
        **placement(),
        **style(),
    )


def placement():
    return dict(
        matrix=list(IDENTITY),
        geometry_offset=[0, 0, 0],
        trs=[0, 0, 0, 0, 0, 0, 1, 1, 1],
        quaternion=[1, 0, 0, 0],
    )


def style():
    return dict(
        visible=True,
        pickable=False,
        readonly=True,
        anchors=[],
        opacity=1.0,
        color="#cbb8a5",
        surface_visible=True,
        surface_pickable=False,
        context_dimmed=False,
    )
