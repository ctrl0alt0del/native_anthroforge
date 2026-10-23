"""A branched consumer detaches its connected construction as one independent assembly."""

from dataclasses import replace
from typing import Any

from . import curve_copy, curve_independence, curve_sources, junction_copies, shortcut_copies
from .curve_copy_resources import Copies
from .object_revisions import authored


def independent(session: Any, item: Any, curve: str) -> str:
    sources = required_sources(session.document, {u.curve for u in item.curves})
    mapping = identities(session.document, sources)
    copier = Copies(session.resources, mapping)
    copies = tuple(copier.record(curve_sources.source(session.document, key)) for key in sources)
    changed = authored(item, curve_independence.remapped_surface(item, mapping))
    objects = tuple(changed if o.id == item.id else o for o in session.document.objects)
    junctions = session.document.junctions + junction_copies.records(session.document, mapping)
    session.scheduler.invalidate({item.id})
    session.replace_document(
        objects=(*objects, *copies),
        junctions=junctions,
        **shortcut_copies.state(session.document, mapping, frozenset({item.id})),
    )
    return str(mapping[curve])


def identities(document: Any, sources: set[str]) -> dict[str, str]:
    mapping = {
        key: value
        for source in sources
        for key, value in curve_copy.mapping(curve_sources.source(document, source)).items()
    }
    return junction_copies.identities(document, mapping)


def required_sources(document: Any, selected: set[str]) -> set[str]:
    from anthroforge.core.junctions import members

    links = members(document.objects)
    result = set(selected)
    for joint in document.junctions:
        if sum(p.curve in selected for p in links[joint.id]) >= 2:
            result.add(joint.source.curve)
    return result


def remapped_branch(branch: Any, mapping: dict[str, str]) -> Any:
    return replace(
        branch,
        id=mapping.get(branch.id, branch.id),
        boundary=mapping.get(branch.boundary, branch.boundary),
        curves=tuple(mapping.get(key, key) for key in branch.curves),
        junctions=tuple(mapping.get(key, key) for key in branch.junctions),
    )
