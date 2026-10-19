"""Tissue anatomy records share mesh presentation without becoming Construction entries."""

from dataclasses import asdict

from anthroforge.application.object_frames import Frames
from anthroforge.core import tissue_policy
from anthroforge.core.tissue_parts import active
from anthroforge.core.tissues import TissueVCP

from .construction_projection import record as object_record
from .values import qml


def synchronize(projection):
    session = projection.controller.session
    tissues = {o.id: o for o in session.document.objects if isinstance(o, TissueVCP)}
    for key, item in tissues.items():
        frame = Frames(session.engine, session.document).world(key)
        cache = (item, frame, session.workspace)
        if projection.keys.get(key) != cache:
            projection.records[key] = record(session, item, frame)
            projection.keys[key] = cache
        if key not in projection.order:
            projection.order.append(key)


def record(session, item, frame):
    row = object_record(session, item, frame)
    row.update(metadata(item))
    source = session.document.object(item.source)
    row.update(
        tissue_modes=sorted(tissue_policy.inflation_modes(source)),
        tissue_domain=tissue_policy.domain(source),
        tissue_masks=tissue_policy.region_masks(item),
    )
    return qml(row)


def metadata(item):
    return dict(
        is_construction=False,
        is_tissue=True,
        depth=0,
        primitive=None,
        source=item.source,
        classification=item.classification,
        color=item.color,
        tissue_settings=settings(item),
    )


SCALARS = (
    "id",
    "source",
    "classification",
    "both_sides",
    "reverse",
    "resolution",
    "stacking",
    "update_mode",
)


def settings(item):
    row = {name: getattr(item, name) for name in SCALARS}
    row["parts"] = [asdict(part) for part in active(item)]
    for name in ("relaxation", "crop", "stack_settings", "stack_plan"):
        row[name] = asdict(getattr(item, name))
    for name in ("fields", "constraints", "diagnostics", "stack_relationships"):
        row[name] = [asdict(value) for value in getattr(item, name)]
    return row


def choices(controller):
    return [
        dict(id=item.id, name=item.name, both_sides=item.both_sides, enabled=item.stacking)
        for item in controller.session.document.objects
        if isinstance(item, TissueVCP) and item.base_state.kind == "SURFACE"
    ]
