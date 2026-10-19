"""One read-only relationship and presentation contract for desktop and API."""

import json

import pytest

from anthroforge.core.cycle_analysis import cycles
from anthroforge.core.jobs import Job
from anthroforge.core.results import Port
from tests.test_construction_contracts import create, hook
from tests.test_issue_integration import records


def test_cycles_exclude_downstream_and_handle_long_chains():
    nodes = [Port(str(i), "geometry") for i in range(3000)]
    edges = {p: {nodes[i - 1]} if i else set() for i, p in enumerate(nodes)}
    edges[nodes[0]] = {nodes[1]}
    reverse = {p: set() for p in nodes}
    for p, inputs in edges.items():
        for source in inputs:
            reverse[source].add(p)
    assert cycles(edges, reverse) == (frozenset(nodes[:2]),)


def test_cycle_inspection_distinguishes_cause_and_consequence(session):
    entity = create(session)
    control = hook(session, entity)
    session.command("control.follow", control=control, entity=control)
    session.wait(5)
    cyclic = records(session, code="DEPENDENCY_CYCLE")
    blocked = records(session, code="DEPENDENCY_BLOCKED")
    assert {r["target"] for r in cyclic} == {control}
    assert all(r["evidence"]["participant"] for r in cyclic)
    assert blocked and all(not r["evidence"]["participant"] for r in blocked)
    assert all(r["evidence"]["cycles"] for r in blocked)


def test_inspection_is_json_readonly_and_describes_actual_attachment(session, assembly):
    root, child = assembly
    before, cursor = session.document, session.history.cursor
    row = session.command("inspect.target", entity=child)
    assert row["attachment"]["support"] == root
    assert row["attachment"]["anchors"]["available"]
    assert row["geometry"]["triangles"] == 12
    assert session.command("inspect.target", entity=root)["topology_locks"][0]["id"] == child
    json.dumps(session.command("inspect.snapshot"))
    assert session.document is before and session.history.cursor == cursor


def test_control_inspection_has_no_fake_surface(session):
    entity = create(session)
    control = hook(session, entity)
    row = session.command("inspect.target", entity=control)
    assert not row["geometry"]["available"]
    assert row["attachment"]["follow"] == entity
    assert any(r["consumers"] for r in row["relationships"])


def test_anatomical_workspace_includes_associated_control_and_settings_roundtrip(session, tmp_path):
    entity = create(session)
    control = hook(session, entity)
    index = session.command("workspace.create", name="Details", members=[entity])
    session.command("workspace.update", name="Control", display_units="mm")
    session.command("control.update", control=control, name="Included control")
    session.command("workspace.preset", name="attachments")
    workspace = session.workspace
    path = str(tmp_path / "views.anthroforge")
    session.command("save", path=path, blocked_policy="wait")
    session.command("open", path=path)
    session.command("workspace.select", index=index)
    assert session.workspace == workspace
    session.command("workspace.remove", index=index)
    assert session.active_workspace == 0 and len(session.document.workspaces) == 1


def test_workspace_guards_and_units_preserve_anatomy(session, assembly):
    root, _ = assembly
    entities, cursor = session.document.entities, session.history.cursor
    session.command("workspace.update", display_units="cm", hidden_categories=["handles"])
    assert session.document.entities is entities and session.history.cursor == cursor
    assert session.command("units.convert", value=0.25, target="mm") == 250
    assert session.command("units.convert", value=250, source="mm") == 0.25
    with pytest.raises(ValueError):
        session.command("workspace.update", members=[root])
    with pytest.raises(ValueError):
        session.command("workspace.update", hidden_categories=["invalid"])
    session.begin()
    with pytest.raises(ValueError, match="Finish"):
        session.command("workspace.create", name="During edit", members=[root])
    session.cancel()


def test_workspace_preserves_deleted_members_for_undo_without_blocking_settings(session):
    entity = create(session)
    session.command("workspace.create", name="Detail", members=[entity])
    session.command("workspace.update", hidden=[entity], unpickable=[entity])
    session.command("scp.delete", entity=entity)
    session.command("workspace.update", display_units="mm")
    session.command("undo")
    assert entity in session.workspace.members and entity in session.workspace.hidden
    assert session.workspace.display_units == "mm"
    with pytest.raises(ValueError, match="unknown"):
        session.command("workspace.update", members=["invented"])


def test_membership_changes_reprioritize_queued_writers_only(session, assembly):
    root, child = assembly
    writer, reader = queued_job(child), queued_job(child, writes=False)
    session.scheduler.submit(writer)
    session.scheduler.submit(reader)
    session.command("workspace.create", name="Root", members=[root])
    assert writer.priority == 0 and reader.priority == -1
    session.command("workspace.update", members=[root, child])
    assert writer.priority == 10 and reader.priority == -1


def queued_job(target, writes=True):
    return Job(
        "Fixture",
        frozenset([target]),
        lambda _: None,
        lambda *_: None,
        lambda _: None,
        writes=writes,
        priority=10 if writes else -1,
    )
