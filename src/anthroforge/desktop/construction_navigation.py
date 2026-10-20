"""Explicit navigation composes existing editing capabilities without authored changes."""

from anthroforge.core import tissue_presets
from anthroforge.core.construction import Curve
from anthroforge.core.fibers import Fiber
from anthroforge.core.membranes import Membrane
from anthroforge.core.points import Anchor


def edit(controller, target):
    item = controller.session.document.registry.records.get(target)
    if item is None or controller.session.history.before is not None:
        return
    controller.cancelViewportTools()
    controller.select(target)
    controller.authoring.setEditing(isinstance(item, Curve))


def focus(controller):
    item = controller.session.document.registry.anatomy.get(controller.selection)
    if item is not None:
        controller.run("workspace.create", dict(name=item.name, members=[item.id], children=True))


def tissue_sources(controller):
    return [
        dict(id=o.id, name=o.name, presets=tissue_presets.available(o))
        for o in controller.session.document.objects
        if isinstance(o, (Anchor, Fiber, Membrane))
        and not controller.objectRecord(o.id).get("readonly", True)
    ]
