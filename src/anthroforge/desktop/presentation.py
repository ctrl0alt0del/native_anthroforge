"""Desktop projections of shared presentation policy; no geometry evaluation."""

from anthroforge.core import presentation
from anthroforge.core.units import factor

PARTS = {
    "position": "points",
    "left": "handles",
    "right": "handles",
    "lattice": "cages",
    "control": "hooks",
    "vertex": "points",
    "base": "points",
    "tissue_control": "points",
    "field": "points",
}


def state(controller):
    view = controller.session.workspace
    return dict(
        members=view.members,
        focused=view.focused,
        display_units=view.display_units,
        unit_factor=factor(view.display_units),
        hidden_categories=view.hidden_categories,
        unpickable_categories=view.unpickable_categories,
        editing=controller.session.history.before is not None,
        object_count=len(controller.session.document.registry.records),
        cursor=view.cursor,
    )


def allows(editor, category, picking=False):
    policy = presentation.pickable if picking else presentation.visible
    return policy(editor.controller.session.workspace, category)


def component(editor, reference, picking=False):
    return allows(editor, PARTS[reference["part"]], picking)


def geometry_flags(workspace, flags):
    return dict(
        surface_visible=flags["visible"] and presentation.visible(workspace, "geometry"),
        surface_pickable=flags["pickable"] and presentation.pickable(workspace, "geometry"),
    )
