from anthroforge.application.storage import write_package
from anthroforge.native.topology import same_content
from tests.test_skeleton_update_commands import prepare


def test_unchanged_boolean_construction_keeps_saved_connectivity(session, tmp_path, monkeypatch):
    from anthroforge.application import construction_tasks

    key = session.command("primitive.create", kind="SEGMENT_CHAIN")
    session.wait()
    mesh = accepted_mesh(session, key)
    path = tmp_path / "unchanged.anthroforge"
    write_package(path, session.document, session.resources)
    monkeypatch.setattr(construction_tasks, "compute_geometry", unexpected_rebuild)
    state = prepare(session, path, {key: key})
    assert state["ready"], state
    candidate = session.skeleton_update.ready(state["token"])
    assert same_content(mesh, accepted_mesh(candidate, key))
    assert not state["findings"]


def unexpected_rebuild(*args):
    raise AssertionError("An unchanged accepted output must not be rebuilt")


def accepted_mesh(context, key):
    return context.resources.meshes[context.document.entity(key).asset].mesh


def test_unchanged_bone_attachment_is_not_recaptured(session, assembly, tmp_path):
    root, child = assembly
    path = tmp_path / "unchanged.anthroforge"
    before = session.document.entity(child).attachment
    write_package(path, session.document, session.resources)
    state = prepare(session, path, {root: root, child: child})
    candidate = session.skeleton_update.ready(state["token"])
    assert candidate.document.entity(child).attachment == before
    assert not any(r["key"] == "bone_capture:" + child for r in state["findings"])
