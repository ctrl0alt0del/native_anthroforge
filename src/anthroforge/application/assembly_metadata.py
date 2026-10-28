"""Accepted resource metadata owns references independently of authored object records."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core import graph_records


def repair(preparation: Any) -> None:
    mapping = preparation.mapping
    for key, path in preparation.available.paths.items():
        authored = mapping.patch(path.authored, path.authored)
        if authored != path.authored:
            target = preparation.assets.setdefault(key, str(uuid4()))
            preparation.resources.paths[target] = replace(path, authored=authored)
    for key, asset in preparation.available.attachments.items():
        targets = tuple(replace(v, reference=mapping.surface(v.reference)) for v in asset.targets)
        if targets != asset.targets:
            target = preparation.assets.setdefault(key, str(uuid4()))
            preparation.resources.attachments[target] = replace(asset, targets=targets)
    rehome(preparation)


def rehome(preparation: Any) -> None:
    for group, rows in preparation.values.items():
        preparation.values[group] = tuple(
            graph_records.rewritten(row, {}, preparation.assets) for row in rows
        )
    for key, path in preparation.resources.paths.items():
        preparation.resources.paths[key] = replace(
            path, authored=graph_records.rewritten(path.authored, {}, preparation.assets)
        )
