"""One membership/editability policy for all workspace clients."""

from typing import TYPE_CHECKING, Any

from anthroforge.core.document import Document
from anthroforge.core.entities import Workspace, descendants
from anthroforge.core.fibers import Fiber
from anthroforge.core.image_presentation import decode as decode_image
from anthroforge.core.inspection_views import decode_bookmark, decode_measurement
from anthroforge.core.points import Anchor
from anthroforge.core.mirroring import source as mirror_source

if TYPE_CHECKING:
    from .session import Session


TUPLES = {
    "members",
    "hidden",
    "unpickable",
    "camera",
    "cursor",
    "hidden_categories",
    "unpickable_categories",
}
RECORDS = {
    "bookmarks": decode_bookmark,
    "measurements": decode_measurement,
    "reference_images": decode_image,
}


def settings(values: dict[str, Any]) -> dict[str, Any]:
    result = {key: tuple(value) if key in TUPLES else value for key, value in values.items()}
    for key, decode in RECORDS.items():
        if key in values:
            result[key] = tuple(decode(v) if isinstance(v, dict) else v for v in values[key])
    return result


def members(document: Document, values: list[str], children: bool = False) -> tuple[str, ...]:
    selected = set(values)
    live = document.registry.anatomy.keys()
    if selected - live:
        raise ValueError("Workspace membership requires anatomical SCP/VCP objects.")
    if children:
        for key in values:
            if key in document.index.entities:
                selected |= descendants(document.entities, key)
    if not selected:
        raise ValueError("A focused workspace needs at least one anatomical object.")
    return tuple(sorted(selected))


def available(session: "Session") -> None:
    if session.waiting_save or session.history.before is not None:
        raise ValueError("Finish the current edit or save before changing workspace membership.")


def validate(session: "Session", workspace: Workspace, index: int) -> None:
    if index == 0 and (workspace.focused or workspace.members):
        raise ValueError("The whole-document workspace cannot restrict membership.")
    if index != 0 and not workspace.focused:
        raise ValueError("Named workspaces must retain explicit membership.")
    validate_references(session, workspace, session.document.workspaces[index])
    validate_images(session, workspace, session.document.workspaces[index])


def validate_images(session: "Session", workspace: Workspace, previous: Workspace) -> None:
    from anthroforge.core.reference_images import ReferenceImage

    existing = {style.target for style in previous.reference_images}
    for style in workspace.reference_images:
        if style.target not in existing and not isinstance(
            session.document.object(style.target), ReferenceImage
        ):
            raise ValueError("Image appearance requires a reference image.")


def validate_references(session: "Session", workspace: Workspace, previous: Workspace) -> None:
    # Retain deleted IDs for undo; validate new references, not historical membership.
    for field in ("members", "hidden", "unpickable"):
        live = set(session.document.registry.records)
        if field == "members":
            live = set(session.document.registry.anatomy)
        added = set(getattr(workspace, field)) - set(getattr(previous, field))
        if added - live:
            raise ValueError("Workspace references an unknown or incompatible object.")


def associations(document: Document, target: str) -> set[str]:
    from .curve_sources import consumers

    pending, seen, anatomy = [mirror_source(target)], set[str](), set[str]()
    while pending:
        key = pending.pop()
        if key in seen:
            continue
        seen.add(key)
        if key in document.registry.construction or key in document.index.controls:
            anatomy.update(object_anatomy(document.object(key)))
            pending.extend(consumers(document, {key}))
        elif key in document.registry.anatomy:
            anatomy.add(key)
    return anatomy


def object_anatomy(item: Any) -> set[str]:
    related = set(item.owners)
    if isinstance(item, Fiber):
        related.update(b.target for b in item.bindings)
    if isinstance(item, Anchor):
        related.add(item.binding.reference.target)
    return related


def included(document: Document, workspace: Workspace, target: str) -> bool:
    if not workspace.focused:
        return True
    related = associations(document, target)
    return not related or bool(related.intersection(workspace.members))
