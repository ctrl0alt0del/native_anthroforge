"""Describe captured attachment coordinates; native queries resolve world anchors."""

from dataclasses import asdict, replace
from typing import TYPE_CHECKING, Any

from anthroforge.core.entities import SCP
from anthroforge.core.objects import ConstructionObject
from anthroforge.core.results import geometry_asset
from anthroforge.native.attachments import anchor_points

from .control_frames import display_frame
from .inspection_context import InspectionContext

if TYPE_CHECKING:
    from .session import Session


def frame(session: "Session | InspectionContext", item: Any) -> dict[str, Any]:
    try:
        matrix = item.matrix if isinstance(item, SCP) else display_frame(session, item)
        return dict(matrix=matrix, available=True, error="")
    except ValueError as error:
        return dict(matrix=(), available=False, error=str(error))


def describe(session: "Session | InspectionContext", item: Any) -> dict[str, Any]:
    if isinstance(item, ConstructionObject):
        from .construction_inspection import attachment

        return attachment(session, item)
    return anatomical(session, item)


def anatomical(session: "Session | InspectionContext", item: Any) -> dict[str, Any]:
    support = getattr(item, "support", "") or getattr(item, "parent", "")
    binding = getattr(item.result, "binding", ()) or item.attachment.binding
    result = dict(settings=asdict(item.attachment), support=support, captured=bool(binding))
    result.update(follow=getattr(item, "follow", ""), owner_frame=frame(session, item))
    result["binding"] = decoded(binding)
    parent = session.document.index.entities.get(support) or session.document.index.controls.get(
        support
    )
    result["support_frame"] = frame(session, parent) if parent else None
    result["support_name"] = parent.name if parent else ""
    result["surface"] = surface(session, parent)
    result["anchors"] = anchors(session, item, parent, binding)
    return result


def decoded(binding: tuple[float, ...]) -> dict[str, Any]:
    if not binding:
        return {}
    return dict(
        surface_vertices=list(binding[:3]),
        barycentric=list(binding[3:6]),
        flow_vertices=list(binding[6:9]),
        flow_barycentric=list(binding[9:12]),
        parent_local_tangent=list(binding[12:15]),
        frame_offset_metres=list(binding[15:18]),
        owner_local_anchor_metres=list(binding[18:21]),
        owner_local_tangent=list(binding[21:24]),
        owner_local_normal=list(binding[24:27]),
        owner_anchor_index=binding[27],
    )


def surface(session: "Session | InspectionContext", parent: Any) -> dict[str, Any]:
    key = geometry_asset(parent) if isinstance(parent, SCP) else ""
    return dict(owner=parent.id if parent else "", asset=key, available=bool(key))


def anchors(
    session: "Session | InspectionContext", item: Any, parent: Any, binding: tuple[float, ...]
) -> dict[str, Any]:
    if not binding or not isinstance(parent, SCP):
        return dict(available=False, reason="No captured SCP surface/origin binding.")
    try:
        child = proxy(session, item, binding)
        key = geometry_asset(parent)
        handle = session.assets[key].mesh.handle if key else 0
        points = anchor_points(session.engine, child, parent, handle)
        return dict(available=True, owner_world_metres=points[:3], support_world_metres=points[3:])
    except ValueError as error:
        return dict(available=False, reason=str(error))


def proxy(session: "Session | InspectionContext", item: Any, binding: tuple[float, ...]) -> SCP:
    if isinstance(item, SCP):
        return replace(item, attachment=replace(item.attachment, binding=binding))
    return SCP(
        item.name,
        matrix=display_frame(session, item),
        attachment=replace(item.attachment, binding=binding),
    )
