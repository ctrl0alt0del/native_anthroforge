from dataclasses import replace
from types import SimpleNamespace

from anthroforge.application.primitive_operations import straight_curve
from anthroforge.core.entities import IDENTITY
from anthroforge.desktop import comparison_picking
from anthroforge.native import paths


def test_comparison_path_picking_uses_displayed_revision_and_mirror_source(session):
    path = paths.evaluate(session.engine, replace(straight_curve(), id="curve"))
    row = dict(
        id="mirror", handle=path.handle, content=dict(kind="PATH", matrix=IDENTITY, source="curve")
    )
    model = SimpleNamespace(active_rows=lambda: [row])
    cache = comparison_picking.capture(model)
    assert comparison_picking.pick(session.engine, cache, [0, 0, 4], [0, 0, -1], 0.01) == "curve"
    model.active_rows = lambda: []
    assert comparison_picking.pick(session.engine, cache, [0, 0, 4], [0, 0, -1], 0.01) == "curve"
    cache = comparison_picking.capture(model)
    assert comparison_picking.pick(session.engine, cache, [0, 0, 4], [0, 0, -1], 0.01) == ""
