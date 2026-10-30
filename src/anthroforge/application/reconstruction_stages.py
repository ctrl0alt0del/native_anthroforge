"""Immutable comparison stages, separate from anatomical providers and construction."""

import zipfile
from dataclasses import asdict, replace
from functools import partial
from pathlib import Path
from typing import Any
from uuid import uuid4

from anthroforge.core.entities import IDENTITY
from anthroforge.core.reconstruction import ReconstructionStage
from anthroforge.core.results import geometry_asset

from . import assembly_source, assets, reconstruction_imports, resource_storage
from . import reconstruction_state as records
from .object_frames import Frames


def stage_record(session: Any, subject: str, stage: str, options: Any) -> Any:
    records.subject(session, subject, options.get("variant", ""))
    if stage not in ("ORIGINAL", "TRANSFERRED"):
        raise ValueError("Choose Original reference or Transferred anatomy.")
    frame = tuple(options.get("frame", IDENTITY))
    session.engine.decompose(frame)
    return ReconstructionStage(
        subject,
        stage,
        str(uuid4()),
        frame=frame,
        variant=options.get("variant", ""),
        name=options.get("name", ""),
    )


def import_mesh(
    session: Any, subject: str, stage: str, path: str, units: float, **options: Any
) -> Any:
    row = stage_record(session, subject, stage, options)
    worker = partial(load_mesh, session.engine, units, bool(options.get("y_up", False)))
    return reconstruction_imports.start(session, path, "stages", row, worker)


def load_mesh(engine: Any, units: float, y_up: bool, path: Path, row: Any, cancel: Any) -> Any:
    asset = assets.imported(engine, path, units, y_up, cancel)
    row = replace(row, source=str(path), fingerprint=asset.digest, name=row.name or path.stem)
    return row, row.asset, asset


def import_project(
    session: Any,
    subject: str,
    stage: str,
    path: str,
    source_entity: str,
    role: str = "final",
    **options: Any,
) -> Any:
    row = stage_record(session, subject, stage, options)
    worker = partial(load_project, session.engine, source_entity, role)
    return reconstruction_imports.start(session, path, "stages", row, worker)


def load_project(engine: Any, entity: str, role: str, path: Path, row: Any, cancel: Any) -> Any:
    source = assembly_source.inspect(str(path), cancel)
    try:
        item = source.document.object(entity)
        key = result_asset(item, role)
        if key not in source.metadata["assets"]:
            raise ValueError("Choose an accepted mesh stage for the reference surface.")
        with zipfile.ZipFile(source.path) as archive:
            asset = resource_storage.read_mesh(archive, key, source.metadata["assets"][key], engine)
        row = project_record(engine, row, source, entity)
        return row, row.asset, asset
    finally:
        source.directory.cleanup()


def project_record(engine: Any, row: Any, source: Any, entity: str) -> Any:
    from anthroforge.native.construction import matrix

    return replace(
        row,
        frame=tuple(matrix(engine, row.frame, source_frame(engine, source.document, entity))),
        source=source.original,
        fingerprint=source.digest,
        source_entity=entity,
        source_revision=source.document.revision,
    )


def source_frame(engine: Any, document: Any, entity: str) -> Any:
    from anthroforge.native.scene import geometry_matrix

    frame = Frames(engine, document).world(entity)
    return geometry_matrix(
        engine, frame, getattr(document.object(entity), "geometry_offset", (0, 0, 0))
    )


def result_asset(item: Any, stage: str) -> str:
    from anthroforge.core.tissues import TissueVCP

    from .tissue_inspection_stages import result

    key = result(item, stage).asset if isinstance(item, TissueVCP) else geometry_asset(item)
    if not key:
        raise ValueError("The selected stage has no accepted surface.")
    return str(key)


def remove(session: Any, stage: str) -> None:
    if any(row.stage == stage for row in records.state(session).reviews):
        raise ValueError("This stage is referenced by review history.")
    records.remove(session, "stages", stage)


def inspect(session: Any, subject: str = "") -> Any:
    rows = records.state(session).stages
    return dict(stages=[asdict(row) for row in rows if not subject or row.subject == subject])
