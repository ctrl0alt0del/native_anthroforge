"""Read-only viewport instances share source leases and never enter the trees."""

from dataclasses import asdict

from anthroforge.core.mirroring import MirrorRule
from anthroforge.native import construction, scene


def synchronize(projection):
    controller = projection.controller
    document = controller.session.document
    sources = projection.records | controller.construction.records
    controller.mirror_records = {
        key: reflected(controller, sources[value.source], value)
        for key, value in document.mirrors.instances.items()
        if value.source in sources
    }
    for key, row in projection.records.items():
        row["mirror_settings"] = asdict(document.mirrors.rules.get(key, MirrorRule(key)))


def reflected(controller, source, instance):
    session = controller.session
    rule = session.document.mirrors.rules[instance.rule]
    frame = construction.matrix(session.engine, rule.frame, source["matrix"])
    return dict(
        source, id=instance.id, mirror_source=instance.source, mirror_rule=instance.rule,
        readonly=True, transformable=False, name=source["name"] + " · mirrored",
        matrix=list(frame), trs=session.engine.decompose(frame), anchors=[],
        quaternion=scene.quaternion(session.engine, frame),
        visible=source["visible"] and session.workspace.mirror_display != "SOURCE",
        surface_visible=source.get("surface_visible", False) and session.workspace.mirror_display != "SOURCE",
        opacity=1.0 if not source["readonly"] else source.get("opacity", .08),
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
        if row.get("asset") not in paths or not row["visible"]:
            continue
        path = paths[row["asset"]].path
        values.extend(dict(row, handle=path.handle, chunk=i, geometry_asset=row["asset"],
                           key=f"{row['id']}:{row['asset']}:{i}") for i in range(path.chunks))
    if controller.session.workspace.mirror_display == "MIRROR":
        sources = {v.source for v in controller.session.document.mirrors.instances.values()}
        values = [v for v in values if v["id"] not in sources]
    return values
