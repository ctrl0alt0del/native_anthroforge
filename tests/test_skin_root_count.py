"""Draft initialization is authored independently from later topology reservations."""

import json
from dataclasses import replace
from types import SimpleNamespace

import pytest

from anthroforge.application import skin_avbd_capture, skin_codec, skin_contributor_queries
from anthroforge.application import skin_avbd_identity as identity
from anthroforge.application import skin_builder_configuration as builders
from anthroforge.core.skin import Skin, SkinContributor
from anthroforge.core.skin_avbd_settings import AvbdConfiguration
from anthroforge.core.skin_draft import AppliedDraftConfiguration
from tests.test_skin_avbd_checkpoints import captures
from tests.test_skin_budgets import fixture


def configure(session, count):
    session.command(
        "skin.configure", section="draft_settings", values=dict(backend="AVBD", root_vertices=count)
    )


def test_root_count_authoring_roundtrip_and_undo_leave_topology_unchanged(session, tmp_path):
    before = session.document.skin
    configure(session, 802)
    path = tmp_path / "root-count.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    assert builders.decode(session.document.skin).root_vertices == 802
    assert session.document.skin.topology_settings == before.topology_settings
    session.command("undo")
    assert session.document.skin == before
    session.command("open", path=str(path))
    assert builders.decode(session.document.skin).root_vertices == 802
    assert builders.decode(skin_codec.decode({}), "AVBD").root_vertices == 402


@pytest.mark.parametrize("count", [3, 500001, True, 402.5, "402"])
def test_invalid_root_counts_are_rejected_without_editing(session, count):
    before = session.document
    with pytest.raises(ValueError, match="initial root vertices"):
        configure(session, count)
    assert session.document == before


def test_pending_root_count_capture_uses_applied_configuration(session):
    configure(session, 402)
    skin = session.document.skin
    applied = AppliedDraftConfiguration(skin.draft_settings.configuration(), 1)
    skin = builders.configure(replace(skin, applied_draft=applied), "AVBD", dict(root_vertices=802))
    document = replace(session.document, skin=skin)
    captured = builders.projected(document, builders.automatic(skin))
    assert captured_count(captured) == 402 and captured_count(document) == 802
    other = builders.configure(skin, "FIELD", dict(gap_strength=0.4))
    assert builders.decode(other, "AVBD").root_vertices == 802


def captured_count(document):
    return skin_avbd_capture.recipe_settings(SimpleNamespace(document=document))["root_vertices"]


def test_quad_budgets_do_not_change_draft_configuration_or_root_count():
    skin = Skin(
        contributors=(SkinContributor("bone", density_mode="SUBTREE_BUDGET", target_quads=9000),)
    )
    assert builders.decode(skin, "AVBD") == AvbdConfiguration()


def test_enclosing_budget_resolves_nearest_explicit_ancestor_and_document():
    document = fixture()
    context = skin_contributor_queries.budget_context
    assert context(document, "l") == dict(owner="r", name="Root", target_quads=6000)
    assert context(document, "m") == dict(owner="r", name="Root", target_quads=6000)
    assert context(document, "r") == dict(owner="", name="Document", target_quads=8100)


def test_changed_root_count_invalidates_all_scp_and_vcp_checkpoints(tmp_path):
    folder = tmp_path / "inputs"
    before = captures(folder)
    path = folder / "recipe.json"
    recipe = json.loads(path.read_text())
    path.write_text(json.dumps(recipe | dict(root_vertices=802)))
    after = identity.prefixes(folder, "runtime")
    assert all(
        a != b
        for old, new in zip(before, after, strict=True)
        for a, b in zip(old, new, strict=True)
    )
