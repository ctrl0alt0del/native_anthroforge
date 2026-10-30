"""Read-only viewport instances share source leases and never enter the trees."""

from dataclasses import asdict

from anthroforge.application import workspace_policy
from anthroforge.core import presentation
from anthroforge.core.mirroring import MirrorRule
from anthroforge.native import components, construction, scene


def synchronize(projection):
    controller = projection.controller
    document = controller.session.document
    sources = projection.records | controller.construction.records
    controller.mirror_records = {
        key: cached(controller, sources[value.source], value)
        for key, value in document.mirrors.instances.items()
        if value.source in sources
    }
    for key, row in sources.items():
        row["mirror_settings"] = asdict(document.mirrors.rules.get(key, MirrorRule(key)))
        row["mirror_boundaries"] = [asdict(r) for r in document.mirror_rules if key in r.scope]
    publish_markers(controller, sources)


def publish_markers(controller, sources):
    prune_cache(controller)
    controller.construction.points.synchronize(sources | controller.mirror_records)
    controller.marker_model.synchronize_records(
        [dict(id=row["id"], item=row) for row in controller.viewport_view.markerRows]
    )


def prune_cache(controller):
    controller._mirror_projection_cache = {
        k: v
        for k, v in controller._mirror_projection_cache.items()
        if k in controller.mirror_records
    }


def cached(controller, source, instance):
    rule = controller.session.document.mirrors.plane(instance)
    key = (dict(source), rule, controller.session.workspace)
    previous = controller._mirror_projection_cache.get(instance.id)
    if previous is None or previous[0] != key:
        previous = key, reflected(controller, source, instance)
        controller._mirror_projection_cache[instance.id] = previous
    return previous[1]


def reflected(controller, source, instance):
    session = controller.session
    rule = session.document.mirrors.plane(instance)
    frame = construction.matrix(session.engine, rule.frame, source["matrix"])
    row = dict(source, **identity(source, instance), **visibility(session, source, instance))
    row.update(
        matrix=list(frame),
        trs=session.engine.decompose(frame),
        anchors=[],
        quaternion=scene.quaternion(session.engine, frame),
    )
    return point_location(session, source, row, rule)


def point_location(session, source, row, rule):
    if source.get("world_position"):
        row["world_position"] = components.transformed(
            session.engine, [source["world_position"]], rule.frame
        )[0].tolist()
    return row


def identity(source, instance):
    return dict(
        id=instance.id,
        mirror_source=instance.source,
        mirror_rule=instance.rule,
        readonly=True,
        context_dimmed=source.get("context_dimmed", source.get("readonly", False)),
        transformable=False,
        name=source.get("name", "Preview") + " · mirrored",
        opacity=source.get("opacity", 1.0),
    )


def visibility(session, source, instance):
    workspace = session.workspace
    category = category_for(source)
    visible = workspace.mirror_display != "SOURCE" and instance.id not in workspace.hidden
    visible &= presentation.visible(workspace, category)
    pickable = visible and instance.id not in workspace.unpickable
    pickable &= workspace_policy.included(session.document, workspace, instance.source)
    pickable &= presentation.pickable(workspace, category)
    return dict(
        visible=visible,
        pickable=pickable,
        surface_visible=bool(source.get("handle")) and visible,
        surface_pickable=bool(source.get("handle")) and pickable,
    )


def category_for(row):
    if row.get("is_control"):
        return "cages" if row.get("kind") == "LATTICE" else "hooks"
    return "curves" if row.get("kind") in ("CURVE", "FIBER", "POINT", "ANCHOR") else "geometry"


def presented(controller, row):
    if controller.session.workspace.mirror_display != "MIRROR":
        return row["visible"]
    return row["visible"] and not any(
        v.source == row["id"] for v in controller.session.document.mirrors.instances.values()
    )


def rows(controller, originals):
    values = list(originals)
    sources = {v.source for v in controller.session.document.mirrors.instances.values()}
    if controller.session.workspace.mirror_display == "MIRROR":
        values = [dict(v, surface_visible=False) if v["id"] in sources else v for v in values]
    mirrors = [r for r in controller.mirror_records.values() if r.get("handle") and r.get("chunks")]
    return [*values, *mirrors]


def path_rows(controller, originals):
    values = list(originals)
    paths = controller.session.resources.paths
    for row in controller.mirror_records.values():
        if row.get("asset") not in paths or not row["visible"] or row.get("fiber_radius", 0):
            continue
        path = paths[row["asset"]].path
        values.extend(path_record(row, path, i) for i in range(path.chunks))
    if controller.session.workspace.mirror_display == "MIRROR":
        sources = {v.source for v in controller.session.document.mirrors.instances.values()}
        values = [v for v in values if v["id"] not in sources]
    return values


def path_record(row, path, chunk):
    return dict(
        row,
        handle=path.handle,
        chunk=chunk,
        geometry_asset=row["asset"],
        key=f"{row['id']}:{row['asset']}:{chunk}",
    )


def fiber_rows(controller, originals):
    rows = []
    instances = controller.session.document.mirrors.instances.values()
    by_source = {}
    for instance in instances:
        by_source.setdefault(instance.source, []).append(instance)
    for row in originals:
        rows.append(dict(row, visible=presented(controller, row)))
        for instance in by_source.get(row["id"], ()):
            mirror = reflected(controller, row, instance)
            rows.append(dict(mirror, key=row["key"] + ":" + instance.id))
    return rows


def previews(controller, rows, target):
    instances = [
        v for v in controller.session.document.mirrors.instances.values() if v.source == target
    ]
    originals = controller.session.workspace.mirror_display != "MIRROR" or not instances
    output = list(rows) if originals else []
    for row in rows:
        for instance in instances:
            value = reflected(controller, row, instance)
            value.update(id=row["id"] + ":" + instance.id, pickable=False, surface_pickable=False)
            if "key" in row:
                value["key"] = row["key"] + ":" + instance.id
            output.append(value)
    return output
