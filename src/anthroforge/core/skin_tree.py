"""Resolve authored skin policy in document sibling order, including empty SCP groups."""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .skin_avbd_settings import AvbdContributor, decode

if TYPE_CHECKING:
    from .document import Document


@dataclass(frozen=True, slots=True)
class Policy:
    mode: str = "FOLLOW"
    mode_owner: str = ""
    limb_owner: str = ""


def override(parent: Policy, settings: AvbdContributor | None) -> Policy:
    if settings is None:
        return parent
    explicit = settings.build_mode != "INHERIT"
    return Policy(
        settings.build_mode if explicit else parent.mode,
        settings.owner if explicit else parent.mode_owner,
        settings.owner if settings.limb is not None else parent.limb_owner,
    )


def preorder(document: "Document") -> Iterator[tuple[str, Policy]]:
    children = document.index.structure.children
    config = decode(document.skin.draft_settings.configuration("AVBD"))
    settings = {row.owner: row for row in config.contributors}
    stack = [(owner, Policy()) for owner in reversed(children.get("", ()))]
    while stack:
        owner, parent = stack.pop()
        current = override(parent, settings.get(owner))
        yield owner, current
        stack.extend((child, current) for child in reversed(children.get(owner, ())))
