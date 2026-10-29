import pytest

from anthroforge.application.storage import read_package


def variant(session, target):
    return session.command("variant.create", subjects=[target], name="Alternative")["id"]


def rename_bone(session, target, name):
    session.command("scp.rename", entity=target, name=name)


def test_variant_edits_leave_accepted_unchanged_and_pin_supports(session, assembly):
    root, child = assembly
    before = session.document
    key = variant(session, child)
    rename_bone(session, child, "Variant child")
    assert session.document.entity(child).name == "Variant child"
    with pytest.raises(ValueError, match="pinned"):
        rename_bone(session, root, "External edit")
    session.command("variant.leave")
    assert session.document.entities == before.entities
    session.command("variant.enter", variant=key)
    assert session.document.entity(child).name == "Variant child"


def test_save_from_variant_contains_accepted_and_variant_without_source(
    session, assembly, tmp_path
):
    root, child = assembly
    original = session.document.entity(child).name
    key = variant(session, child)
    rename_bone(session, child, "Variant child")
    target = tmp_path / "variants.anthroforge"
    session.command("save", path=str(target), blocked_policy="wait")
    restored, resources = read_package(target, session.engine)
    assert restored.entity(child).name == original
    row = restored.reconstruction.variant(key)
    assert restored.reconstruction.snapshot(row.current).entity(child).name == "Variant child"
    resources.require(restored)
    assert restored.entity(root) == session.document.entity(root)


def test_checkpoint_is_immutable_and_fork_edits_independently(session, assembly):
    _, child = assembly
    key = variant(session, child)
    checkpoint = session.command("variant.checkpoint")["id"]
    rename_bone(session, child, "Later")
    with pytest.raises(ValueError, match="Fork"):
        session.command("variant.enter", variant=checkpoint)
    fork = session.command("variant.fork", variant=checkpoint)["id"]
    assert session.document.entity(child).name != "Later"
    rename_bone(session, child, "Fork")
    session.command("variant.enter", variant=key)
    assert session.document.entity(child).name == "Later"
    session.command("variant.enter", variant=fork)
    assert session.document.entity(child).name == "Fork"
