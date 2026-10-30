"""Explicitly composed feature catalogues; no runtime plugin discovery."""

from . import (
    anatomy,
    assembly,
    construction,
    curves,
    deformation,
    inspection,
    issues,
    mirroring,
    painting,
    profiling,
    reconstruction,
    session,
    shortcuts,
    skin,
    surfaces,
    tissue,
)

GROUPS = (
    anatomy.COMMANDS,
    assembly.COMMANDS,
    construction.COMMANDS,
    curves.COMMANDS,
    deformation.COMMANDS,
    inspection.COMMANDS,
    issues.COMMANDS,
    mirroring.COMMANDS,
    painting.COMMANDS,
    profiling.COMMANDS,
    reconstruction.COMMANDS,
    session.COMMANDS,
    shortcuts.COMMANDS,
    skin.COMMANDS,
    surfaces.COMMANDS,
    tissue.COMMANDS,
)
