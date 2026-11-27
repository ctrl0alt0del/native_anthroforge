"""Scene cache inputs exclude camera state, which belongs to the viewport rig."""

from dataclasses import fields

from anthroforge.core.entities import Workspace

SCENE_FIELDS = tuple(f.name for f in fields(Workspace) if f.name not in {"camera", "orthographic"})


def scene_key(workspace):
    return tuple(getattr(workspace, name) for name in SCENE_FIELDS) if workspace else None
