"""Visibility masks apply at ray-query boundaries, without altering source geometry."""

from anthroforge.native import scene, sections


def pick_scene(controller, origin, direction, owners=None, handles=None, matrices=None):
    owners = controller.pick_ids if owners is None else owners
    handles = controller.pick_handles if handles is None else handles
    matrices = controller.pick_matrices if matrices is None else matrices
    tool, engine = controller.section_tools, controller.session.engine
    if not tool.enabled or not tool.cut:
        return scene.pick(engine, handles, matrices, origin, direction)
    return sections.pick(engine, handles, matrices, tool.planes(owners), origin, direction)


def pick(controller, owner, mesh, frame, origin, direction):
    tool = controller.section_tools
    if not tool.applies(owner):
        return mesh.engine.pick(mesh, frame, origin, direction)
    hits = sections.pick(mesh.engine, [mesh.handle], [frame], [tool.plane], origin, direction)
    return hits[0][1:] if hits else None


def displayed(tool):
    from anthroforge.application import inspection_surfaces, tissue_sections

    rows = tool.controller.tissue_inspection.model.active_rows()
    if tool.controller.tissue_inspection.target != tool.target or not rows:
        selected = inspection_surfaces.get(tool.controller.session, tool.target, tool.stage)
        return [tissue_sections.record(selected)]
    result, seen = [], set()
    for row in rows:
        key = row["owner"], row["stage"]
        if row["content"]["kind"] not in ("MESH", "HEAT") or key in seen:
            continue
        seen.add(key)
        result.append(surface(row))
    return result


def surface(row):
    return dict(
        owner=row["owner"],
        stage=row["stage"],
        asset=row["geometry_asset"],
        frame=row["content"]["matrix"],
    )
