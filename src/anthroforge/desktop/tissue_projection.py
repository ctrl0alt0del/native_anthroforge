"""Tissue anatomy records share mesh presentation without becoming Construction entries."""

from dataclasses import asdict

from anthroforge.application.object_frames import Frames
from anthroforge.core.tissues import TissueVCP

from .construction_projection import record as object_record
from .values import qml


def synchronize(projection):
    session = projection.controller.session
    tissues = {o.id: o for o in session.document.objects if isinstance(o, TissueVCP)}
    projection.order = [k for k in projection.order if k in session.document.registry.records]
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
    row.update(
        is_construction=False,
        is_tissue=True,
        depth=0,
        primitive=None,
        source=item.source,
        classification=item.classification,
        color=item.color,
        tissue_settings=asdict(item),
    )
    return qml(row)
