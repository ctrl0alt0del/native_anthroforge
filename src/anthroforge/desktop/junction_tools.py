"""Concise junction choices over the shared document policies."""

from anthroforge.application.workspace_policy import included
from anthroforge.core.construction import Curve
from anthroforge.core.junctions import members


def choices(controller, curve, point):
    session = controller.session
    result = membership(session.document, curve, point)
    result["curves"] = [
        choice(o)
        for o in session.document.objects
        if isinstance(o, Curve)
        and o.id != curve
        and included(session.document, session.workspace, o.id)
    ]
    return result


def membership(document, curve, point):
    records = document.registry.records
    current = records.get(curve)
    selected = (
        next((p for p in current.points if p.id == point), None)
        if isinstance(current, Curve)
        else None
    )
    shared = selected.junction if selected else ""
    refs = members(document.objects).get(shared, ()) if shared else ()
    return dict(id=shared, members=[records[r.curve].name for r in refs])


def choice(item):
    return dict(
        id=item.id,
        name=item.name,
        points=[
            dict(id=p.id, name="Point " + str(i + 1), junction=p.junction)
            for i, p in enumerate(item.points)
        ],
    )
