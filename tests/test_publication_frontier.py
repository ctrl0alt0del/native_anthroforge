"""Accepted outputs notify the next evaluator, preserving intermediate publication barriers."""

from anthroforge.application.dependencies import frontier
from tests.conftest import CUBE
from tests.test_surface_workflow import surface
from tests.test_tissue_stack_workflow import current, fiber, layer


def test_frontier_crosses_aliases_but_not_computation_or_cycles():
    graph = {"plan": {"final"}, "final": {"alias"}, "alias": {"path"}, "path": {"plan"}}
    barriers = {"plan", "final", "path"}
    assert frontier(graph, {"plan"}, barriers) == {"final"}
    assert frontier(graph, {"final"}, barriers) == {"path"}
    assert frontier(graph, {"plan"}, set()) == set()


def test_creating_support_before_next_fibers_settles_without_rebuilding_sources(session):
    bone = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.wait(10)
    first = layer(session, surface(session, [fiber(session, bone, y, 0.7) for y in (0.3, -0.3)]))
    sources = [fiber(session, bone, y, 0.71) for y in (0.3, -0.3)]
    assert any(s.reference.target == first for s in session.document.object(sources[0]).supports)
    before = [session.document.object(key).result.asset for key in sources]
    membrane = surface(session, sources, strips=6)
    second = layer(session, membrane)
    current(session, first)
    current(session, second)
    assert [session.document.object(key).result.asset for key in sources] == before
    assert not session.scheduler.active_jobs
