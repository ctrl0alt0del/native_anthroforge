"""Authored SCP construction settings cross history, storage, inspection and worker capture."""

import json
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from anthroforge.application import skin_avbd_capture, skin_capture, storage
from anthroforge.application import skin_builder_configuration as builders
from anthroforge.application.skin_inputs import build_signature
from anthroforge.application.skin_stage_policy import ordered_sources
from anthroforge.core.entities import SCP
from anthroforge.core.skin_avbd_settings import AvbdConfiguration, AvbdContributor, decode
from anthroforge.core.skin_limb import SkinLimb
from anthroforge.core.skin_tree import preorder


def change(session, owner, **values):
    session.command("skin.contributor.configure", owner=owner, values=values)


def tree_nodes():
    return [
        SCP(i, id=i, parent=p)
        for i, p in (
            ("root", ""),
            ("right", "root"),
            ("left", "root"),
            ("arm", "right"),
            ("digit", "arm"),
            ("tip", "digit"),
        )
    ]


def authored_tree(session):
    rows = (
        AvbdContributor("root", build_mode="FILL"),
        AvbdContributor("arm", limb=SkinLimb()),
        AvbdContributor("digit", limb=SkinLimb(), build_mode="FOLLOW"),
    )
    return replace(
        session.document,
        entities=tuple(tree_nodes()),
        skin=builders.store(session.document.skin, "AVBD", AvbdConfiguration(contributors=rows)),
    )


def test_tree_includes_empty_groups_and_nested_limbs(session):
    doc = authored_tree(session)
    found = dict(preorder(doc))
    assert list(found) == ["root", "right", "arm", "digit", "tip", "left"]
    assert (found["arm"].mode_owner, found["arm"].limb_owner) == ("root", "arm")
    assert (found["tip"].mode_owner, found["tip"].limb_owner) == ("digit", "digit")
    assert (found["left"].mode, found["left"].limb_owner) == ("FILL", "")
    config = decode(doc.skin.draft_settings.configuration("AVBD"))
    reduced = builders.store(
        doc.skin,
        "AVBD",
        replace(config, contributors=tuple(r for r in config.contributors if r.owner != "arm")),
    )
    assert dict(preorder(replace(doc, skin=reduced)))["tip"] == found["tip"]


def test_tissue_stages_follow_document_order(session):
    doc = authored_tree(session)
    names = ("z-muscle", "a-muscle")
    snapshot = SimpleNamespace(
        index=doc.index, skin=doc.skin, objects=[SimpleNamespace(id=n) for n in names]
    )
    table = {
        key: (SimpleNamespace(owner=key, kind="TISSUE", instance=""),) for key in reversed(names)
    }
    assert ordered_sources(snapshot, table)[1] == list(names)


def test_reparent_changes_policy_signature(session):
    doc = authored_tree(session)
    moved = tuple(replace(e, parent="left") if e.id == "tip" else e for e in doc.entities)
    new = replace(doc, entities=moved)
    assert dict(preorder(new))["tip"].mode == "FILL"
    assert build_signature(doc) != build_signature(new)


def select_avbd(session):
    skin = session.document.skin
    session.replace_document(
        skin=replace(skin, draft_settings=replace(skin.draft_settings, backend="AVBD"))
    )


def test_authored_limb_persists_edits_and_undo(session, assembly, tmp_path):
    root, child = assembly
    change(session, root, build_mode="FILL")
    change(session, child, limb={"rest_radius": 0.4})
    change(session, child, limb={"boundary_radius": 0.2})
    session.command("undo")
    select_avbd(session)
    report = session.command("skin.contributor.inspect", owner=child)
    assert report["draft"]["mode_source"] == session.document.entity(root).name
    assert report["settings"]["limb"]["boundary_radius"] is None
    path = tmp_path / "limb.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    loaded, _ = storage.read_package(path, session.engine)
    assert loaded.skin.draft_settings == session.document.skin.draft_settings


def capture_recipe(session, path):
    doc = session.document
    capture = skin_capture.capture(session.engine, doc, session.resources)
    req = SimpleNamespace(
        document=doc, capture=capture, resources=session.resources, engine=session.engine
    )
    skin_avbd_capture.stage(path, req)
    return json.loads((path / "recipe.json").read_text())


def test_mirrored_limb_uses_reflected_attachment(session, assembly, tmp_path):
    root, child = assembly
    session.command("mirror.configure", target=root, enabled=True, shift=2)
    session.wait()
    change(session, child, limb={"offset": [0.01, 0, 0]})
    rows = capture_recipe(session, tmp_path)["bones"]
    assert [r["route"] for r in rows] == ["follow", "limb", "limb"]
    left, right = [r["settings"] for r in rows[1:]]
    assert left["material_length_ratio"] == right["material_length_ratio"] == 0.4
    for key in ("parent_point", "child_point"):
        p = np.asarray(left[key]) * [-1, 1, 1] + [4, 0, 0]
        np.testing.assert_allclose(p, right[key])
    assert left["boundary_radius"] == pytest.approx(0.75 * right["rest_radius"])


def test_invalid_limb_settings_leave_state_untouched(session, assembly):
    root, child = assembly
    with pytest.raises(ValueError, match="child SCP"):
        change(session, root, limb={})
    with pytest.raises(ValueError, match="positive finite"):
        change(session, child, limb={"rest_radius": 0})
    assert not session.document.skin.contributors


def test_explicit_fill_starts_new_region_and_follow_leaves_it(session):
    doc = authored_tree(session)
    extra = AvbdContributor("right", build_mode="FILL")
    config = decode(doc.skin.draft_settings.configuration("AVBD"))
    skin = builders.store(
        doc.skin, "AVBD", replace(config, contributors=(*config.contributors, extra))
    )
    policies = dict(preorder(replace(doc, skin=skin)))
    assert policies["arm"].mode_owner == "right"
    assert policies["digit"].mode == "FOLLOW"
    assert policies["left"].mode_owner == "root"


def test_fill_capture_reports_declaring_and_affected_scp(session, assembly, tmp_path):
    root, child = assembly
    change(session, child, build_mode="FILL")
    with pytest.raises(ValueError, match=f"Fill Region {child} at {child}"):
        capture_recipe(session, tmp_path)
    assert (
        decode(session.document.skin.draft_settings.configuration("AVBD"))
        .contributors[-1]
        .build_mode
        == "FILL"
    )


def test_material_radius_only_scales_new_limb_material(session, assembly, tmp_path):
    _, child = assembly
    change(session, child, limb={})
    initial = capture_recipe(session, tmp_path)["bones"][-1]["settings"]
    change(session, child, limb={"rest_radius": 2 * initial["rest_radius"]})
    edited = capture_recipe(session, tmp_path)["bones"][-1]["settings"]
    assert edited["material_length_ratio"] == pytest.approx(0.8)
    assert edited["boundary_radius"] == initial["boundary_radius"]
