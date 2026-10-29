from anthroforge.application import assembly_source, skeleton_graph
from anthroforge.native.mesh import NativeCancellation


def package(session, tmp_path):
    path = tmp_path / "source.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    return assembly_source.inspect(str(path), NativeCancellation(session.engine))


def prepare(session, source, **options):
    return skeleton_graph.copy(
        source,
        session.document,
        session.resources,
        session.engine,
        NativeCancellation(session.engine),
        options,
    )


def test_replacement_preserves_identity_hierarchy_and_source_curves(session, assembly, tmp_path):
    root, child = assembly
    source = package(session, tmp_path)
    original = session.document
    p = prepare(session, source, matches={child: child})
    updated = skeleton_graph.merge(original, p.values, tuple(p.mapping.references))
    assert len(updated.entities) == len(original.entities)
    assert updated.entity(child).parent == root
    assert updated.entity(child).id == child
    assert updated.entity(root) == original.entity(root)
    assert session.document is original
    assert updated.entity(child).primitive.source != original.entity(child).primitive.source


def test_added_bone_is_independent_at_explicit_parent(session, assembly, tmp_path):
    root, child = assembly
    source = package(session, tmp_path)
    p = prepare(session, source, additions={child: root})
    updated = skeleton_graph.merge(session.document, p.values, tuple(p.mapping.references))
    copied = updated.entity(p.ids[child])
    assert copied.id != child and copied.parent == root
    assert copied.matrix == session.document.entity(child).matrix
    assert len(updated.entities) == len(session.document.entities) + 1
