"""Presentation-only influence masks and anchors matching displayed native geometry."""

from anthroforge.application import shortcut_effects, tissue_inspection


def snapshot(view):
    session = view.controller.session
    shortcut = view.editor.selected()
    direct = {r.target for r in shortcut_effects.direct(shortcut)}
    affected = {p.owner for p in shortcut_effects.affected(session, shortcut)}
    colors = {key: "#ffc46b" if key in direct else "#67cee8" for key in affected}
    return dict(colors=colors, lines=anchor_lines(view), shown=True)


def anchor_lines(view):
    status = tissue_inspection.status(view.controller.session, "shortcut")
    if status.get("state") != "ready":
        return []
    result = []
    for row in status.get("report", {}).get("rows", []):
        if displayed(view.controller, row["target"]):
            for field in ("authored_anchors", "effective_anchors"):
                anchors = row.get(field)
                if anchors and anchors.get("available"):
                    result.extend(
                        (*anchors["owner_world_metres"], *anchors["support_world_metres"])
                    )
    return result


def displayed(controller, key):
    session = controller.session
    item = session.document.registry.records.get(key)
    if item is None:
        return False
    keys = {key, getattr(item, "parent", "")} - {""}
    rows = controller.render_model.active_rows()
    return all(matching_display(rows, session.document.entity(target)) for target in keys)


def matching_display(rows, item):
    return any(
        r["id"] == item.id
        and tuple(r["matrix"]) == item.matrix
        and r["geometry_revision"] == item.result.revision
        for r in rows
    )


def publishing(controller, key):
    record = controller.session.shortcut_observation.latest.get(key)
    owners = {p.owner for p in record.ports} if record else set()
    for model in (controller.render_model, controller.path_model):
        if any(r["id"] in owners for r in model.pending):
            return True
        if any(r["id"] in owners and not r["active"] for r in model.rows):
            return True
    return False
