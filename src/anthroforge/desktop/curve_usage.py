"""Source usage and consumer-owned settings projected from the shared document index."""

from dataclasses import asdict

from anthroforge.application import curve_sources


def users(document, target):
    return [
        dict(id=key, name=document.object(key).name)
        for key in sorted(curve_sources.consumers(document, {target}))
    ]


def uses(session, entity):
    item = session.document.index.entities.get(entity.id) if entity else None
    if item is None or item.primitive is None:
        return []
    return [
        dict(asdict(use), users=users(session.document, use.curve)) for use in item.primitive.curves
    ]
