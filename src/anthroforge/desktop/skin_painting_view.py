"""SCP brush previews use displayed revisions and staged heat resources."""

from anthroforge.application import skin_painting
from anthroforge.application import tissue_inspection as inspection

from . import tissue_inspection_scene as scene
from .tissue_painting_view import obstacles


def capture(tool, view):
    controller, target = tool.controller, tool.target
    rows = controller.render_model.active_rows()
    row = next((r for r in rows if r["id"] == target and r["surface_visible"]), None)
    if row is None:
        raise ValueError("Show the selected SCP surface before painting collagen.")
    options = dict(
        expected_asset=row["geometry_asset"],
        view=list(view),
        obstacles=obstacles(controller, target),
    )
    skin_painting.validate(controller.session, target, dict(options, samples=[[0, 0]]))
    return options


def publish(tool):
    value = tool.preview
    if (
        tool.domain.kind != "collagen"
        or not value
        or not inspection.current(tool.controller.session, value)
    ):
        tool.model.publish([])
        return
    session, heat = tool.controller.session, value["resource"]
    provider = skin_painting.provider(session, tool.target)
    metadata = metadata_for(session, tool.target, provider)
    rows = scene.chunks(metadata, provider.resource.mesh)
    tool.model.publish(scene.heat_chunks(rows[0], heat), [heat])


def metadata_for(session, target, provider):
    return dict(
        scene.placement(session, provider.frame),
        id=target + ":collagen",
        owner=target,
        stage="collagen",
        kind="MESH",
        reference=False,
        color="#ffffff",
        geometry_asset=provider.asset_id,
        geometry_revision=provider.result.revision,
        status="ready",
    )
