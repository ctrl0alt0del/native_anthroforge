"""Canonical attachment evidence for the actual assembly, outside timed recording."""

from dataclasses import fields
from hashlib import sha256

ATTRIBUTES = (
    "parent",
    "attachment",
    "bindings",
    "binding",
    "supports",
    "attachment_asset",
    "constraints",
)


def attachments(session):
    result = {}
    for item in session.document.registry.records.values():
        values = tuple((key, getattr(item, key)) for key in ATTRIBUTES if hasattr(item, key))
        if values:
            result[item.id] = sha256(repr(values).encode()).hexdigest()
    for key, asset in session.resources.selected(session.document).attachments.items():
        digest = sha256(repr(asset.targets).encode())
        for attribute in fields(asset.field):
            value = getattr(asset.field, attribute.name)
            digest.update(value.tobytes() if hasattr(value, "tobytes") else repr(value).encode())
        result["field:" + key] = digest.hexdigest()
    return result
