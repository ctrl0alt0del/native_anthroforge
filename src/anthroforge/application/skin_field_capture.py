"""FIELD-specific collagen and source-gap capture from an owned document."""

from typing import Any

import numpy as np

from anthroforge.core.skin_field import FieldContributor, decode, effective_collagen

from . import skin_capture, skin_collagen


def capture(engine: Any, document: Any, resources: Any, cancel: int = 0) -> Any:
    config = decode(document.skin.draft_settings.configuration("FIELD"))
    rows = skin_capture.sources(engine, document, resources, cancel)
    lookup = {row.owner: row for row in config.contributors}
    settings = [lookup.get(r.identity.owner) or FieldContributor(r.identity.owner) for r in rows]
    policies = [policy(config, row, setting) for row, setting in zip(rows, settings, strict=True)]
    geometry = skin_capture.geometry(engine, rows, policies, cancel)
    warnings: list[str] = []
    collagen = [
        weights(document, resources, row, warnings, setting)
        for row, setting in zip(rows, settings, strict=True)
    ]
    return skin_capture.Capture(geometry, rows, np.concatenate(collagen), tuple(warnings))


def policy(config: Any, row: Any, setting: Any) -> tuple[float, float, bool]:
    gap = setting if setting.gap_mode == "OVERRIDE" else config.settings
    return gap.gap_limit_ratio, gap.gap_strength, row.identity.kind == "SCP"


def weights(document: Any, resources: Any, row: Any, warnings: list[str], setting: Any) -> Any:
    if row.identity.kind != "SCP":
        return np.ones(row.mesh.counts[0])
    item = document.object(row.identity.owner)
    if setting.collagen_mode == "PAINTED":
        asset = resources.skin.get(setting.painted)
        if skin_collagen.matching(asset, row.mesh):
            return asset.arrays["collagen"]
        warnings.append(
            "Painted collagen does not match " + item.name + "; using its uniform value."
        )
    return np.full(row.mesh.counts[0], effective_collagen(setting, item.name))
