"""Accepted resource metadata owns references independently of authored object records."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core import graph_records

from .resources import references


def repair(preparation: Any) -> None:
    needed = required(preparation)
    repair_paths(preparation, needed["paths"])
    repair_captures(preparation, needed["attachments"])
    rehome(preparation)


def repair_paths(preparation: Any, keys: set[str]) -> None:
    for key in keys:
        path = preparation.available.paths[key]
        authored = preparation.mapping.patch(path.authored, path.authored)
        if authored != path.authored:
            target = preparation.assets.setdefault(key, str(uuid4()))
            preparation.resources.paths[target] = replace(path, authored=authored)


def repair_captures(preparation: Any, keys: set[str]) -> None:
    mapping = preparation.mapping
    for key in keys:
        asset = preparation.available.attachments[key]
        targets = tuple(replace(v, reference=mapping.surface(v.reference)) for v in asset.targets)
        if targets != asset.targets:
            target = preparation.assets.setdefault(key, str(uuid4()))
            preparation.resources.attachments[target] = replace(asset, targets=targets)


def required(preparation: Any) -> dict[str, set[str]]:
    needed = references(preparation.values["entities"], preparation.values["objects"])
    visited: set[str] = set()
    while paths := needed["paths"] - visited:
        visited |= paths
        for key in paths:
            authored = preparation.available.paths[key].authored
            for group, values in references((), (authored,)).items():
                needed[group] |= values
    return needed


def rehome(preparation: Any) -> None:
    for group, rows in preparation.values.items():
        preparation.values[group] = tuple(
            graph_records.rewritten(row, {}, preparation.assets) for row in rows
        )
    for key, path in preparation.resources.paths.items():
        preparation.resources.paths[key] = replace(
            path, authored=graph_records.rewritten(path.authored, {}, preparation.assets)
        )
