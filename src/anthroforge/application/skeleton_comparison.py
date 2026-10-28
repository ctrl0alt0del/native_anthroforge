"""Worker-prepared review evidence; geometric distance is separate from material motion."""

from typing import Any

from anthroforge.native import comparison, measurement

from . import comparison_geometry, skeleton_bindings, skeleton_checks
from .inspection_context import InspectionContext


def describe(context: Any, changes: Any) -> dict[str, Any]:
    before = InspectionContext(
        context.baseline, context.resources, context.engine, context.baseline.workspaces[0]
    )
    after = InspectionContext(
        context.document, context.resources, context.engine, context.document.workspaces[0]
    )
    result = comparison_geometry.compare(before, after, context.cancel.handle)
    verified = {r.target for r in changes if r.correspondence == "verified"}
    affected = {p.owner for p in context.prepared} | {r.target for r in changes}
    result["rows"] = [row(context, r, verified) for r in result["rows"] if r["id"] in affected]
    result["changed"] = sum(bool(r["changes"]) for r in result["rows"])
    result["correspondence"] = "Material displacement only for verified bone correspondence"
    result["checks"] = skeleton_checks.inspect(context)
    return result


def row(context: Any, value: Any, verified: Any) -> Any:
    context.check_cancelled()
    old, new = value["before"], value["after"]
    value["distance"] = distances(context, old, new, value["id"] in verified)
    for record in (old, new):
        if record and record["result"]:
            record["result"].pop("inputs", None)
    return value


def distances(context: Any, old: Any, new: Any, verified: bool) -> Any:
    if not old or not new or any(r["geometry"]["kind"] != "MESH" for r in (old, new)):
        return None
    if old["frame_error"] or new["frame_error"]:
        return None
    first, second = (context.assets[r["result"]["asset"]].mesh for r in (old, new))
    try:
        return comparison.distances(
            first, old["frame"], second, new["frame"], verified, context.cancel.handle
        )
    except ValueError as error:
        context.check_cancelled()
        return dict(unavailable=str(error))


def attachments(context: Any, previous: Any) -> list[dict[str, Any]]:
    found = {row["owner"]: row for row in previous}
    owners = {p.owner for p in context.prepared} & context.baseline.registry.records.keys()
    for key in sorted(owners):
        context.check_cancelled()
        original = context.baseline.object(key)
        before = skeleton_bindings.locations(context, context.baseline, original)
        if before:
            found[key] = attachment_row(context, original, before)
    return list(found.values())


def attachment_row(context: Any, original: Any, before: Any) -> dict[str, Any]:
    item = context.document.object(original.id)
    after = skeleton_bindings.locations(context, context.document, item)
    return dict(
        owner=item.id,
        name=original.name,
        before=before,
        after=after,
        displacement=anchor_distances(context, before, after),
    )


def anchor_distances(context: Any, before: Any, after: Any) -> list[dict[str, Any]]:
    old = {r["point"]: r for r in before}
    return [
        dict(
            point=r["point"],
            delta=measurement.distance(context.engine, old[r["point"]]["position"], r["position"]),
            units="m",
        )
        for r in after
        if r["point"] in old
    ]
