import hashlib
from threading import Event

import numpy as np

from anthroforge.application import assembly_copy, assembly_source, storage
from anthroforge.application.assembly_candidate import install
from anthroforge.core.document import Document
from tests.test_construction_resources import populated


def prepare_source(session, tmp_path):
    curve = populated(session)
    path = tmp_path / "source.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    return curve, path, assembly_source.inspect(str(path), Event())


def test_selected_resources_and_retained_authored_ids_are_transferred(session, tmp_path):
    curve, path, source = prepare_source(session, tmp_path)
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    destination = Document()
    value = assembly_copy.copy_closed(source, destination, [curve.id], session.engine, Event())
    copied = value.merge(destination).objects[0]
    accepted = value.resources.paths[copied.result.asset]
    assert copied.id != curve.id and accepted.authored.id == copied.id
    assert not value.resources.images
    np.testing.assert_array_equal(
        accepted.path.array(), session.resources.paths["path"].path.array()
    )
    assert before == hashlib.sha256(path.read_bytes()).hexdigest() == source.digest
    assert copied.points[0].id != curve.points[0].id


def test_snapshot_survives_source_removal_and_import_is_single_undo(session, tmp_path):
    curve, path, source = prepare_source(session, tmp_path)
    path.unlink()
    value = assembly_copy.copy_closed(source, session.document, [curve.id], session.engine, Event())
    session.begin()
    result = install(session, value)
    session.commit()
    identity = result["identities"][curve.id]
    assert session.document.object(identity).id == identity
    session.navigate(-1)
    assert identity not in session.document.registry.records
    session.navigate(1)
    session.resources.require(session.document)


def test_imported_copy_round_trips_without_source_or_undo_history(session, tmp_path):
    curve, _, source = prepare_source(session, tmp_path)
    destination = Document()
    value = assembly_copy.copy_closed(source, destination, [curve.id], session.engine, Event())
    result = value.merge(destination)
    path = tmp_path / "assembled.anthroforge"
    storage.atomic_save(path, result, value.resources)
    restored, resources = storage.read_package(path, session.engine)
    assert restored == result
    resources.require(restored)
    assert restored.imports[0].source_document == str(source.document.id)
