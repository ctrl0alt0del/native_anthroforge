"""Explicit navigation composes existing editing capabilities without authored changes."""

from anthroforge.core import tissue_presets
from anthroforge.core.construction import Curve
from anthroforge.core.mirroring import source
from anthroforge.core.points import Point
from anthroforge.core.surfaces import Surface


def edit(controller, target):
    item = controller.session.document.registry.records.get(target)
    if item is None or controller.session.history.before is not None:
        return
    controller.viewport_view.cancelViewportTools()
    controller.selection_view.select(target)
    controller.authoring.setEditing(isinstance(item, Curve))


def focus(controller):
    item = controller.session.document.registry.anatomy.get(source(controller.selection))
    if item is not None:
        controller.run("workspace.create", dict(name=item.name, members=[item.id], children=True))


def tissue_sources(controller):
    return [
        dict(id=o.id, name=o.name, presets=tissue_presets.available(o))
        for o in controller.session.document.objects
        if isinstance(o, (Point, Curve, Surface))
        and not controller.selection_view.objectRecord(o.id).get("readonly", True)
    ]
