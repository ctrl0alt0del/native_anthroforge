"""Stage resources use the same bounded frame-boundary publication as authored geometry."""

from anthroforge.application import tissue_inspection_stages as stages
from anthroforge.native import scene


def stage_rows(tool, stage, reference=False, target=""):
    session, target = tool.controller.session, target or tool.target
    item = stages.tissue(session, target)
    row = stages.row(session, item, stage)
    if not row["available"]:
        return [], []
    key, kind = row["result"]["asset"], row["kind"]
    resource = resource_for(session, key, kind)
    metadata = stage_metadata(session, target, row, reference)
    return chunks(metadata, resource), [resource] if resource else []


def resource_for(session, key, kind):
    return (
        session.resources.meshes[key].mesh
        if kind == "MESH"
        else session.resources.paths[key].path
        if kind == "PATH"
        else None
    )


def stage_metadata(session, target, row, reference):
    return dict(
        placement(session, row["frame"]),
        id=target + (":reference" if reference else ":inspection"),
        owner=target,
        stage=row["stage"],
        kind=row["kind"],
        reference=reference,
        color="#78d9b5" if reference else "#dba2b4",
        geometry_asset=row["result"]["asset"],
        geometry_revision=row["result"]["revision"],
        status=row["result"]["status"],
    )


def placement(session, frame):
    return dict(
        matrix=list(frame),
        trs=session.engine.decompose(frame),
        quaternion=scene.quaternion(session.engine, frame),
        geometry_offset=[0, 0, 0],
        visible=True,
        surface_pickable=True,
        surface_visible=True,
        readonly=True,
    )


def chunks(metadata, resource):
    count = resource.counts[4] if metadata["kind"] == "MESH" else resource.chunks if resource else 1
    handle = resource.handle if resource else 0
    return [
        dict(
            metadata,
            handle=handle,
            key=f"{metadata['id']}:{metadata['stage']}:{handle}:{i}",
            chunk=i,
            mesh_handle=handle if metadata["kind"] == "MESH" else 0,
            content=content(metadata, handle if metadata["kind"] == "MESH" else 0),
        )
        for i in range(count)
    ]


def content(row, mesh_handle):
    keys = ("stage", "kind", "matrix", "trs", "quaternion")
    return dict({key: row[key] for key in keys}, mesh_handle=mesh_handle)


def rows(tool):
    if not tool.target or not tool.stage:
        return [], []
    output, resources = stage_rows(tool, tool.stage)
    if tool.reference and tool.mode == "Overlay":
        extra, leases = stage_rows(tool, tool.reference, True)
        output.extend(extra)
        resources.extend(leases)
    if tool.reference and tool.mode == "Displacement":
        output, resources = heat_rows(tool, output, resources)
    return additional_views(tool, output, resources)


def additional_views(tool, output, resources):
    from . import stacking_inspection_view, tissue_painting_view

    output, resources = tissue_painting_view.rows(tool, output, resources)
    stacking_inspection_view.decorate(tool, output)
    extra, leases = stacking_inspection_view.rows(tool)
    return output + extra, resources + leases


def heat_rows(tool, output, resources):
    from anthroforge.application.tissue_inspection import current

    value = tool.controller.session.tissue_inspection.values.get("comparison")
    if not value or not value.asset or not current(tool.controller.session, value.asset):
        return output, resources
    heat = value.asset["resource"]
    if not output or value.asset["options"] != dict(stage=tool.stage, reference=tool.reference):
        return output, resources
    return heat_chunks(output[0], heat), [heat]


def heat_chunks(row, heat):
    result = [
        dict(
            row,
            kind="HEAT",
            handle=heat.handle,
            key=f"heat:{heat.handle}:{i}",
            chunk=i,
            mesh_handle=heat.target.handle,
            content=dict(row["content"], kind="HEAT", mesh_handle=heat.target.handle),
        )
        for i in range(heat.chunks)
    ]
    return result


def primary(tool):
    row = next((row for row in tool.model.active_rows() if not row["reference"]), None)
    return dict(row, **row["content"]) if row else None


def picked_rows(tool, rows):
    active = [
        dict(r, **r["content"])
        for r in tool.model.active_rows()
        if not r["reference"] or r.get("related")
    ]
    owners = {row["owner"] for row in active}
    result = [r for r in rows if r["id"] not in owners]
    seen = set()
    for row in active:
        if row["mesh_handle"] and row["owner"] not in seen:
            result.append(dict(row, id=row["owner"], handle=row["mesh_handle"]))
            seen.add(row["owner"])
    return result


def hidden_owners(tool):
    return sorted({r["owner"] for r in tool.model.active_rows()})


def mesh(tool, row):
    resource = tool.model.leases.get(row["handle"])
    if resource is not None:
        return getattr(resource, "target", resource)
    return next(
        (
            r.target
            for r in tool.model.leases.values()
            if getattr(r, "target", None) and r.target.handle == row["handle"]
        ),
        None,
    )
