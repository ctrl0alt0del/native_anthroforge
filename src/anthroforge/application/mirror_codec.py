"""Persist mirror relationships only; source assets remain the single geometry owner."""

from typing import Any

from anthroforge.core.mirroring import MirrorRule, SharedMirrorTarget


def fields(data: dict[str, Any]) -> dict[str, Any]:
    return dict(
        mirror_rules=tuple(MirrorRule(**v) for v in data.get("mirror_rules", ())),
        shared_mirror_targets=tuple(
            SharedMirrorTarget(**v) for v in data.get("shared_mirror_targets", ())
        ),
    )
