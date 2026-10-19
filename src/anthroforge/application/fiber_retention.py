"""Unedited structural anchors retain their capture; fresh dense influences use current surfaces."""

from typing import Any

from anthroforge.core.fibers import Fiber
from anthroforge.native import attachment_fields

from . import attachment_assets


def retained(item: Fiber) -> tuple[Any, ...]:
    assert item.edit is not None
    return tuple(
        b for b in item.bindings if b.attachment is not None and b.point not in item.edit.rebind
    )


def retain(item: Fiber, field: Any, captures: Any) -> attachment_assets.AttachmentAsset:
    bindings = retained(item)
    targets = tuple(dict.fromkeys((*captures, *(b.capture for b in bindings))))
    indices = {point.id: index for index, point in enumerate(item.points)}
    pins = [indices[b.point] for b in bindings]
    owners = [targets.index(b.capture) for b in bindings]
    records = [b.attachment.binding for b in bindings]
    updated = attachment_fields.retain(field, pins, owners, records) if bindings else field
    return attachment_assets.compact(updated, targets)
