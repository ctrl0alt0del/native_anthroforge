"""One temporary presentation filter shared by geometry, paths, images and picking."""


def project(controller, row):
    view = getattr(controller, "neighborhood", None)
    if not view or not view.members:
        return row
    visible = row["id"] in view.members
    pickable = visible and can_pick(controller, row)
    values = dict(row, visible=visible, pickable=pickable)
    if "surface_visible" in row:
        values.update(
            surface_visible=visible and bool(row.get("handle")),
            surface_pickable=pickable and bool(row.get("handle")),
        )
    return values


def records(controller, rows):
    return [project(controller, row) for row in rows]


def can_pick(controller, row):
    return not row.get("readonly") and row["id"] not in controller.session.workspace.unpickable
