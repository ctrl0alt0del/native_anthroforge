"""Contextual queries reproduce desktop policies without creating state or jobs."""

from types import SimpleNamespace

import pytest

from anthroforge.application import mapping_queries
from anthroforge.desktop import assembly_projection, skin_contributor, surface_choices
from tests.test_assembly_mapping import captured
from tests.test_skeleton_update_commands import prepare
from tests.test_skeleton_update_controls import conflicting_source


def assembly_preparation(session, tmp_path):
    bone, fiber, source = captured(session, tmp_path)
    session.command("assembly.inspect", path=source.original)
    session.wait()
    token = session.command("assembly.status")["source"]
    session.command("assembly.prepare", source=token, selected=[fiber.id])
    session.wait()
    return bone, session.command("assembly.status")


def test_assembly_targets_use_real_reference_and_match_desktop(session, tmp_path):
    bone, state = assembly_preparation(session, tmp_path)
    key = state["mappings"][0]["key"]
    panel = SimpleNamespace(
        controller=SimpleNamespace(session=session), _state=state, focus=key, repair=False
    )
    before, cursor = session.document, session.history.cursor
    result = session.command("assembly.mapping.targets", token=state["token"], reference=key)
    assert {r["key"] for r in result["items"]} == {
        r["key"] for r in assembly_projection.targets(panel)
    }
    assert bone in {r["target"] for r in result["items"]}
    assert session.document is before and session.history.cursor == cursor
    with pytest.raises(ValueError, match="Unknown mapping"):
        session.command("assembly.mapping.targets", token=state["token"], reference="invented")


def test_choices_are_searchable_paged_and_revision_qualified(session, tmp_path):
    _, state = assembly_preparation(session, tmp_path)
    arguments = dict(token=state["token"], reference=state["mappings"][0]["key"])
    first = session.command("assembly.mapping.targets", **arguments, limit=1)
    assert len(first["items"]) == 1
    matched = session.command(
        "assembly.mapping.targets", **arguments, search=first["items"][0]["name"]
    )
    assert matched["items"][0] == first["items"][0]
    session.replace_document(name="Unrelated rename")
    with pytest.raises(ValueError, match="inputs changed"):
        session.command(
            "assembly.mapping.targets", **arguments, expected_revision=first["revision"]
        )


def test_persisted_missing_references_use_same_mapping_policy(session, tmp_path):
    _, state = assembly_preparation(session, tmp_path)
    session.command("assembly.import", token=state["token"])
    reference = session.document.external_references[0].id
    rows = session.command("assembly.mapping.targets", token="", reference=reference)["items"]
    assert rows and all(r["compatible"] for r in rows)
    with pytest.raises(ValueError, match="completed preparation"):
        session.command("assembly.mapping.targets", token=state["token"], reference=reference)


def test_skeleton_destination_control_remapping_is_public(session, assembly, tmp_path):
    _, bone = assembly
    path, _, _ = conflicting_source(session, bone, tmp_path)
    state = prepare(session, path, {bone: bone})
    key = state["controls"][0]["key"]
    args = dict(token=state["token"], reference=key, target=bone, controls=True)
    result = session.command("skeleton_update.mapping.properties", **args)
    expected = mapping_queries.property_rows(session, "skeleton_update", **args)
    assert result["items"] and result["items"] == sorted(
        expected, key=lambda r: r["name"].casefold()
    )


def test_skin_effective_values_match_ui_without_creating_override(session, assembly):
    bone, _ = assembly
    session.command("scp.rename", entity=bone, name="Nasal cartilage")
    session.command("skin.configure", section="envelope_settings", values={"gap_strength": 0.4})
    before = session.document
    result = session.command("skin.contributor.inspect", owner=bone)
    assert result == skin_contributor.describe(session, bone)
    assert not result["authored_override"] and not before.skin.contributors
    assert result["effective"]["collagen"] == 0 and result["effective"]["gap_strength"] == 0.4
    assert session.document is before


def test_surface_role_choices_match_desktop_and_include_mirrors(session):
    from tests.test_mesh_replacement import mirrored_scene

    mirrored_scene(session)
    expected = surface_choices.rows(SimpleNamespace(session=session))
    result = session.command("surface.options")["items"]
    assert {r["key"] for r in result} == {r["key"] for r in expected}
    assert any(r["id"].startswith("mirror/") for r in result)


def test_refit_eligibility_uses_existing_policy_without_new_jobs(session):
    jobs = len(session.scheduler.jobs)
    result = session.command("skin.fit.refit.eligibility", identity="missing")
    assert not result["available"] and "Unknown" in result["reason"]
    assert len(session.scheduler.jobs) == jobs
