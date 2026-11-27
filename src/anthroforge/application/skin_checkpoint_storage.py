"""Project format selection precedes atomic temporary-file creation."""

from dataclasses import replace
from pathlib import Path
from typing import Any

from .skin_checkpoint_assets import validate


def project(document: Any, extended: bool) -> Any:
    retained = tuple(row for row in document.skin.checkpoints if extended and row.durable)
    skin = replace(document.skin, checkpoints=retained)
    snapshots = tuple(
        replace(row, scene=project(row.scene, extended))
        for row in document.reconstruction.snapshots
    )
    reconstruction = replace(document.reconstruction, snapshots=snapshots)
    return replace(document, skin=skin, reconstruction=reconstruction)


def extended(path: Path) -> bool:
    return path.suffix.lower() == ".anthroforgex"


def require(document: Any, resources: Any) -> None:
    for row in document.skin.checkpoints:
        validate(resources.skin[row.resource])
    for snapshot in document.reconstruction.snapshots:
        require(snapshot.scene, resources)
