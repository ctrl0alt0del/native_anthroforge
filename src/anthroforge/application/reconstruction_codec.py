"""Typed schema-9 reconstruction metadata and non-recursive scene snapshots."""

from dataclasses import asdict, fields
from typing import Any

from anthroforge.core import reconstruction as model

RECORDS = dict(
    variants=model.Variant,
    types=model.AnatomicalType,
    assignments=model.AnatomicalAssignment,
    collections=model.ReviewCollection,
    regions=model.SurfaceRegion,
    stages=model.ReconstructionStage,
    reviews=model.Review,
    work=model.ReconstructionWork,
    evidence=model.ReviewEvidence,
)
TUPLES = frozenset(("subjects", "editable", "aliases", "members", "triangles", "frame", "evidence"))


def encode_scope(value: Any) -> Any:
    return dict(editable=sorted(value.editable), pinned=sorted(value.pinned)) if value else None


def decode_scope(value: Any) -> Any:
    return (
        model.EditingScope(frozenset(value["editable"]), frozenset(value["pinned"]))
        if value
        else None
    )


def encode(value: model.Reconstruction) -> dict[str, Any]:
    from .storage import document_state

    result = {key: [asdict(row) for row in getattr(value, key)] for key in RECORDS}
    result["snapshots"] = [
        dict(id=row.id, scene=document_state(row.scene)) for row in value.snapshots
    ]
    return result


def record(kind: Any, value: dict[str, Any]) -> Any:
    data = {key: tuple(row) if key in TUPLES else row for key, row in value.items()}
    if "construction_map" in data:
        data["construction_map"] = tuple(map(tuple, data["construction_map"]))
    return kind(**data)


def decode(value: dict[str, Any] | None) -> model.Reconstruction:
    value = value or {}
    allowed = {field.name for field in fields(model.Reconstruction)}
    if value.keys() - allowed:
        raise ValueError("Unknown reconstruction metadata.")
    result = model.Reconstruction(
        **{
            key: tuple(record(kind, row) for row in value.get(key, ()))
            for key, kind in RECORDS.items()
        },
        snapshots=tuple(snapshot(row) for row in value.get("snapshots", ())),
    )
    validate(result)
    return result


def snapshot(value: dict[str, Any]) -> model.SceneSnapshot:
    from .storage import decode_document

    if any(value["scene"].get("reconstruction", {}).values()):
        raise ValueError("Nested reconstruction projects are not supported.")
    return model.SceneSnapshot(decode_document(value["scene"]), value["id"])


def validate(value: model.Reconstruction) -> None:
    for name in (*RECORDS.keys(), "snapshots"):
        if name == "assignments":
            continue
        rows = getattr(value, name)
        if len({row.id for row in rows}) != len(rows):
            raise ValueError("Duplicate reconstruction identity in " + name)
    snapshots = {row.id for row in value.snapshots}
    for variant in value.variants:
        if {variant.baseline, variant.current} - snapshots:
            raise ValueError("Variant is missing a retained scene snapshot.")
    validate_links(value)


def validate_links(value: model.Reconstruction) -> None:
    types, variants = {t.id for t in value.types}, {v.id for v in value.variants}
    if len({a.target for a in value.assignments}) != len(value.assignments):
        raise ValueError("An anatomical instance has more than one type assignment.")
    if links(value, ("assignments", "work"), "type_id") - types:
        raise ValueError("Reconstruction records refer to an unavailable anatomical type.")
    if links(value, ("regions", "stages", "reviews", "work"), "variant") - variants:
        raise ValueError("Reconstruction record is missing its variant.")
    validate_reviews(value)


def links(value: model.Reconstruction, groups: tuple[str, ...], attribute: str) -> set[str]:
    return {getattr(row, attribute) for group in groups for row in getattr(value, group)} - {""}


def validate_reviews(value: model.Reconstruction) -> None:
    evidence, regions = {e.id for e in value.evidence}, {r.id for r in value.regions}
    for review in value.reviews:
        if set(review.evidence) - evidence or (review.region and review.region not in regions):
            raise ValueError("Review evidence or material region is missing.")
