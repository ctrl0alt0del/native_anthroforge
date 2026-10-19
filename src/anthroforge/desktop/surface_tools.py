"""Surface source choices follow explicit workspace and junction relationships."""

from anthroforge.application.surface_branch_operations import shared_root
from anthroforge.application.workspace_policy import included
from anthroforge.core.construction import Curve
from anthroforge.core.surfaces import Surface


def choices(controller, target, boundary):
    session = controller.session
    item = session.document.registry.records.get(target)
    if not isinstance(item, Surface):
        return dict(boundaries=[], candidates=[])
    main = item.main or tuple(u.curve for u in item.curves)
    available = available_sources(session, item)
    source = session.document.registry.records.get(boundary)
    sources = source_choices(available, session.document.object(main[0]).closed)
    return dict(
        boundaries=[dict(id=k, name=session.document.object(k).name) for k in (main[0], main[-1])],
        candidates=branch_candidates(source, available),
        sources=sources,
    )


def source_choices(available, closed):
    return [dict(id=o.id, name=o.name) for o in available if o.closed == closed]


def available_sources(session, item):
    return [
        o
        for o in session.document.objects
        if isinstance(o, Curve)
        and o.id not in {u.curve for u in item.curves}
        and included(session.document, session.workspace, o.id)
    ]


def branch_candidates(source, available):
    if not isinstance(source, Curve):
        return []
    result = []
    indices = {p.junction: i for i, p in enumerate(source.points) if p.junction}
    for item in available:
        try:
            root = shared_root(source, item)
        except ValueError:
            continue
        if not item.closed:
            result.append(dict(id=item.id, name=item.name, order=indices[root]))
    return sorted(result, key=lambda value: value["order"])
