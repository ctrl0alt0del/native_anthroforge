"""Historical geometry owns staged leases and never contributes picking candidates."""

from anthroforge.application.comparison_geometry import display_frame
from anthroforge.application.object_frames import Frames
from anthroforge.application.point_evaluation import position
from anthroforge.application.workspace_policy import included
from anthroforge.core.object_registry import kind as object_kind
from anthroforge.core.points import Point
from anthroforge.core.presentation import visible
from anthroforge.core.results import geometry_asset
from anthroforge.native import scene

from .construction_projection import CATEGORIES


def rows(baseline, workspace):
    context = baseline.source
    frames, records, leases = Frames(context.engine, context.document), [], []
    for item in context.document.registry.records.values():
        if item.id in workspace.hidden or not visible(workspace, category(item)):
            continue
        resource, kind = geometry(context, item)
        if resource is None:
            continue
        frame = display_frame(context, item, frames)
        metadata = placement(context, item, frame, workspace, kind)
        records.extend(chunks(metadata, resource))
        leases.append(resource)
    return records, leases


def category(item):
    return CATEGORIES.get(object_kind(item), "anatomy")


def points(baseline, workspace):
    context = baseline.source
    return [
        dict(id=item.id, position=position(context.engine, context.document, item))
        for item in context.document.objects
        if isinstance(item, Point)
        and item.id not in workspace.hidden
        and visible(workspace, category(item))
    ]


def geometry(context, item):
    key = geometry_asset(item)
    if key in context.resources.meshes:
        return context.resources.meshes[key].mesh, "MESH"
    if key in context.resources.paths:
        return context.resources.paths[key].path, "PATH"
    return None, ""


def placement(context, item, frame, workspace, kind):
    return dict(
        id=item.id,
        kind=kind,
        matrix=frame,
        trs=context.engine.decompose(frame),
        quaternion=scene.quaternion(context.engine, frame),
        color=getattr(item, "color", "#65c9d6"),
        readonly=not included(context.document, workspace, item.id),
    )


def chunks(metadata, resource):
    count = resource.counts[4] if metadata["kind"] == "MESH" else resource.chunks
    return [
        dict(
            metadata,
            handle=resource.handle,
            chunk=i,
            content=metadata,
            key=f"{metadata['id']}:{resource.handle}:{i}",
        )
        for i in range(count)
    ]
