"""Candidate meshes, paths and reflected instances share their accepted resource leases."""

from anthroforge.core.entities import IDENTITY
from anthroforge.native import construction, scene

from . import shortcut_comparison_scene


def mirrors(context, rows):
    sources, output = {}, []
    for row in rows:
        sources.setdefault(row["id"], []).append(row)
    for instance in context.document.mirrors.instances.values():
        rule = context.document.mirrors.plane(instance)
        for row in sources.get(instance.source, ()):
            output.append(reflected(context, row, instance, rule))
    return output


def reflected(context, row, instance, rule):
    frame = construction.matrix(context.engine, rule.frame, row["matrix"])
    metadata = dict(
        row["content"],
        id=instance.id,
        source=instance.source,
        matrix=frame,
        trs=context.engine.decompose(frame),
        quaternion=scene.quaternion(context.engine, frame),
    )
    return dict(row, **metadata, content=metadata, key=f"{instance.id}:{row['key']}")


def skin(context):
    asset = context.resources.meshes.get(context.document.skin.final.asset)
    if asset is None:
        return [], []
    metadata = dict(
        id="skin",
        kind="MESH",
        matrix=IDENTITY,
        color="#c2b1a0",
        trs=context.engine.decompose(IDENTITY),
        quaternion=[1, 0, 0, 0],
    )
    return shortcut_comparison_scene.chunks(metadata, asset.mesh), [asset.mesh]


def anchors(candidate, selection, enabled):
    if candidate is None or not enabled:
        return []
    return [
        dict(row, before=list(row.get("before", ())), after=list(row.get("after", ())))
        for row in candidate.evidence
        if not selection or row["owner"] == selection
    ]
