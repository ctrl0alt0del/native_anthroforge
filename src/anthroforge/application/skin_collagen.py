"""Explicit painted collagen resources belong to the source mesh material domain."""

from dataclasses import replace
from typing import Any

import numpy as np

from anthroforge.core.results import geometry_asset
from anthroforge.core.skin import bounded

from . import field_domains, skin_assets, skin_operations


def mesh(session: Any, owner: str) -> Any:
    item = session.document.index.entities.get(owner)
    if item is None:
        raise ValueError("Collagen weights require an SCP.")
    session.editable(owner)
    asset = geometry_asset(item)
    if not asset or asset not in session.assets:
        raise ValueError("The SCP needs accepted mesh geometry before editing collagen.")
    return session.assets[asset].mesh


def matching(asset: Any, mesh: Any) -> bool:
    if asset is None:
        return False
    import json

    values = asset.arrays.get("collagen")
    count, signature = field_domains.mesh_domain(mesh)
    return (
        values is not None
        and values.shape == (count,)
        and json.loads(asset.metadata).get("topology") == signature
    )


def publish(session: Any, owner: str, **values: Any) -> None:
    skin = session.document.skin
    previous = skin_operations.settings_for(skin, owner)
    changed = replace(previous, **values)
    rows = {row.owner: row for row in skin.contributors} | {owner: changed}
    if changed == previous:
        return
    session.replace_document(
        skin=skin_operations.invalidate(skin, True, contributors=tuple(rows.values()))
    )


def set_weights(session: Any, owner: str, values: Any) -> None:
    target = mesh(session, owner)
    count, signature = field_domains.mesh_domain(target)
    weights = np.asarray(values, dtype=np.float64)
    if (
        weights.shape != (count,)
        or not np.isfinite(weights).all()
        or np.any((weights < 0) | (weights > 1))
    ):
        raise ValueError("Collagen needs one finite weight between 0 and 1 per source vertex.")
    data = skin_assets.create({"collagen": weights}, dict(kind="collagen", topology=signature))
    session.resources.skin[data.digest] = data
    publish(session, owner, painted=data.digest, collagen_mode="PAINTED")


def fill(session: Any, owner: str, value: float | None = None) -> None:
    target = mesh(session, owner)
    setting = skin_operations.settings_for(session.document.skin, owner)
    value = setting.collagen if value is None else value
    bounded("collagen", value, 0, 1)
    set_weights(session, owner, np.full(target.counts[0], value))


def clear(session: Any, owner: str) -> None:
    mesh(session, owner)
    publish(session, owner, painted="", collagen_mode="UNIFORM")
