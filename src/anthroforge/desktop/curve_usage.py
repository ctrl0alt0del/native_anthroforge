"""Source usage and consumer-owned settings projected from the shared document index."""

from dataclasses import asdict

from anthroforge.application import curve_sources
from anthroforge.core.surfaces import Surface


def users(document, target):
    return [
        dict(id=key, name=document.object(key).name)
        for key in sorted(curve_sources.consumers(document, {target}))
    ]


def uses(session, entity):
    item = session.document.registry.records.get(entity.id) if entity else None
    definition = item if isinstance(item, Surface) else getattr(item, "primitive", None)
    return [
        dict(
            asdict(use),
            name=session.document.object(use.curve).name,
            users=users(session.document, use.curve),
        )
        for use in getattr(definition, "curves", ())
    ]
