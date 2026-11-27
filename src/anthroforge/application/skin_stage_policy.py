"""Translate document-owned SCP declarations into ordered physical build stages."""

from collections import defaultdict
from typing import Any

from anthroforge.core.skin_avbd_settings import decode
from anthroforge.core.skin_tree import preorder

from . import skin_limb_geometry


def ordered_sources(document: Any, table: Any) -> tuple[list[Any], list[str]]:
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for key, (source, *_) in table.items():
        groups[source.kind, source.owner].append(key)
    bones = [
        (key, policy)
        for owner, policy in preorder(document)
        for key in sorted(groups["SCP", owner], key=lambda k: table[k][0].instance)
    ]
    tissues = [
        key
        for obj in document.objects
        for key in sorted(groups["TISSUE", obj.id], key=lambda k: table[k][0].instance)
    ]
    return bones, tissues


def compile_steps(request: Any, rows: Any, table: Any) -> list[dict[str, Any]]:
    config = decode(request.document.skin.draft_settings.configuration("AVBD"))
    declarations = {r.owner: r for r in config.contributors}
    bases: dict[tuple[str, str], Any] = {}
    return [compile_step(request, row, table[row["id"]][0], declarations, bases) for row in rows]


def compile_step(request: Any, row: Any, src: Any, declarations: Any, bases: Any) -> dict[str, Any]:
    if row.get("mode") == "FILL":
        raise ValueError(
            f"Fill Region {row['mode_owner']} at {row['id']}: "
            "the qualified regional worker still requires explicit compartment inputs."
        )
    step = dict(id=row["id"], route="follow")
    if row.get("limb_owner"):
        step.update(limb_step(request, src, declarations[row["limb_owner"]], bases))
    return step


def limb_step(request: Any, src: Any, decl: Any, bases: Any) -> dict[str, Any]:
    key = (decl.owner, src.instance)
    if key not in bases and decl.owner != src.owner:
        raise ValueError(
            f"{src.owner}: limb base {decl.owner} has no preceding physical attachment."
        )
    base = bases.get(key)
    values = skin_limb_geometry.settings(request, src, decl, base)
    if base is None:
        bases[key] = values | {"material": len(bases) + 1}
    else:
        values["continue_id"] = base["material"]
    return dict(route="limb", settings=values)
