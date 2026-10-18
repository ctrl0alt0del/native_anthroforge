"""Typed resource persistence and reachability, independent of the desktop."""

import io
import zipfile
from dataclasses import replace

import numpy as np
import pytest
from PIL import Image

from anthroforge.application import geometry_ownership, image_assets, path_assets, storage
from anthroforge.application.history import History
from anthroforge.application.primitive_operations import straight_curve
from anthroforge.core.document import Document
from anthroforge.core.reference_images import ReferenceImage
from anthroforge.core.results import EvaluationResult


def image(format="PNG", orientation=1):
    source = Image.new("RGB", (4, 2), "red")
    exif = source.getexif()
    exif[274] = orientation
    stream = io.BytesIO()
    source.save(stream, format=format, exif=exif)
    return image_assets.decode(stream.getvalue())


def populated(session):
    curve = replace(straight_curve(), result=EvaluationResult("path"))
    session.resources.paths["path"] = path_assets.evaluate(session.engine, curve)
    session.resources.images["image"] = image()
    references = (ReferenceImage(source="image"), ReferenceImage(source="image"))
    session.replace_document(objects=(curve, *references))
    return curve


def test_paths_and_shared_images_round_trip_without_native_handles(session, tmp_path):
    curve = populated(session)
    target = tmp_path / "construction.anthroforge"
    storage.atomic_save(target, session.document, session.resources)
    restored, resources = storage.read_package(target, session.engine)
    assert restored == session.document
    np.testing.assert_array_equal(
        resources.paths["path"].path.array(), session.resources.paths["path"].path.array()
    )
    assert resources.images["image"].encoded == session.resources.images["image"].encoded
    with zipfile.ZipFile(target) as archive:
        assert sum(name.endswith("/source") for name in archive.namelist()) == 1
        assert b'"handle"' not in archive.read("manifest.json")
    assert restored.object(curve.id).result.asset == "path"


def test_resource_snapshot_retains_paths_and_images_after_catalogue_collection(session):
    populated(session)
    snapshot = session.resources.snapshot()
    session.document = Document()
    session.history = History(session.document)
    geometry_ownership.collect(session)
    assert not session.resources.paths and not session.resources.images
    assert np.isfinite(snapshot.paths["path"].path.array()).all()
    assert len(snapshot.images["image"].rgba) == 32


def test_undo_history_retains_construction_resources(session):
    session.begin()
    populated(session)
    session.commit()
    session.navigate(-1)
    geometry_ownership.collect(session)
    assert session.resources.paths and session.resources.images
    session.navigate(1)
    session.resources.require(session.document)


def test_missing_resource_is_reported_before_package_adoption(session, tmp_path):
    populated(session)
    target = tmp_path / "broken.anthroforge"
    session.resources.paths.clear()
    with pytest.raises(ValueError, match="missing required paths"):
        storage.atomic_save(target, session.document, session.resources)
    assert not target.exists()


def test_jpeg_exif_orientation_applied_once_in_portable_source():
    original = image("JPEG", orientation=6)
    restored = image_assets.decode(original.encoded)
    assert (original.width, original.height) == (2, 4)
    assert original.rgba == restored.rgba and original.digest == restored.digest
