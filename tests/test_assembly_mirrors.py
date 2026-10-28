from dataclasses import replace
from threading import Event

from anthroforge.application import assembly_source, storage
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.mirroring import MirrorRule
from tests.test_assembly_graph import graph_document
from tests.test_assembly_mapping import prepared


def mirrored_source(session, tmp_path):
    document = replace(
        graph_document(), mirror_rules=(MirrorRule("root", enabled=True, shift=0.2),)
    )
    path = tmp_path / "mirrored.anthroforge"
    storage.atomic_save(path, document, session.resources)
    return assembly_source.inspect(str(path), Event())


def test_imported_boundary_preserves_one_rule_and_shared_instances(session, tmp_path):
    source = mirrored_source(session, tmp_path)
    destination = Document()
    value = prepared(session, source, ["child"], destination=destination)
    result = value.merge(destination)
    assert len(result.entities) == 1
    assert len(result.mirrors.instances) == len(source.document.mirrors.instances)
    assert {i.source for i in result.mirrors.instances.values()} == {
        value.identities[k] for k in ("child", "a", "b")
    }
    assert {result.mirrors.plane(i).shift for i in result.mirrors.instances.values()} == {0.2}


def test_destination_rule_does_not_change_imported_plane(session, tmp_path):
    source = mirrored_source(session, tmp_path)
    root = SCP("Destination")
    destination = Document(
        entities=(root,), mirror_rules=(MirrorRule(root.id, enabled=True, axis="Y"),)
    )
    value = prepared(session, source, ["child"], destination=destination)
    result = value.merge(destination)
    assert {result.mirrors.plane(i).axis for i in result.mirrors.instances.values()} == {"X"}
    path = tmp_path / "retained.anthroforge"
    storage.atomic_save(path, result, value.resources)
    restored, _ = storage.read_package(path, session.engine)
    assert set(restored.mirrors.instances) == set(result.mirrors.instances)


def test_repeated_imports_have_independent_boundary_rules(session, tmp_path):
    source = mirrored_source(session, tmp_path)
    first = prepared(session, source, ["child"])
    destination = first.merge(session.document)
    second = prepared(session, source, ["child"], destination=destination)
    result = second.merge(destination)
    assert len(result.mirrors.instances) == 6
    assert first.identities["root"] != second.identities["root"]
