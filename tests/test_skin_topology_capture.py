"""FLOW capture uses owned accepted tissue charts and optional open fibers."""

from dataclasses import replace

from anthroforge.application import skin_topology_capture as capture
from anthroforge.native.mesh import NativeCancellation
from tests.test_tissue_workflow import assembly


def test_accepted_chart_capture_does_not_recompute_or_edit(session):
    _, _, target = assembly(session)
    before = session.document
    result = capture.capture(
        session.engine, before, session.resources, NativeCancellation(session.engine)
    )
    assert session.document is before
    assert not result.warnings, result.warnings
    assert any(row.identity.owner == target for row in result.sources)
    item = before.object(target)
    row = next(row for row in result.sources if row.identity.owner == target)
    assert row.assets == (item.rest_material.base, item.rest_material.rest)


def test_instant_does_not_capture_quadwild_flow_inputs(session):
    _, _, _ = assembly(session)
    settings = replace(session.document.skin.topology_settings, backend="INSTANT")
    document = replace(
        session.document, skin=replace(session.document.skin, topology_settings=settings)
    )
    result = capture.capture(
        session.engine, document, session.resources, NativeCancellation(session.engine)
    )
    assert not result.sources and not result.warnings


def test_pending_construction_kind_does_not_replace_accepted_chart(session):
    from types import SimpleNamespace

    from anthroforge.core.skin_sources import Source

    _, _, target = assembly(session)
    item = session.document.object(target)
    pending = replace(item, base_state=replace(item.base_state, kind="POINT"))
    document = SimpleNamespace(object=lambda _: pending)
    assert capture.selected(document, Source(target, "TISSUE"))
