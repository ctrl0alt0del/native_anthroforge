"""Document skin uses existing staged mesh leases without an authored hierarchy node."""

from anthroforge.application.skin_fit_preview import displayed as fitted_preview
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
    preview = fitted_preview(session)
    if preview is not None:
        return [preview_row(session, preview)]
    stage = displayed(session)
    if stage is None or stage.asset not in session.assets:
        return []
    mesh = session.assets[stage.asset].mesh
    return [record(session.document, stage, mesh)]


def preview_row(session, candidate):
    return dict(
        id="skin:" + str(session.document.id),
        handle=candidate.mesh.handle,
        chunks=candidate.mesh.counts[4],
        geometry_asset=session.skin_fit_preview.token,
        geometry_revision=0,
        asset="",
        **placement(),
        **style(),
    )


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
