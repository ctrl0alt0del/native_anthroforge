"""Sample actual shortcut operations in a worker-owned document with fixed skin identities."""

from dataclasses import asdict
from typing import Any

import numpy as np

from anthroforge.core.shortcuts import Shortcut
from anthroforge.native import skin_fit, topology

from . import (
    construction_tasks,
    evaluation,
    isolated_execution,
    output_tasks,
    property_catalog,
    shortcut_effects,
    skin_reference_evaluation,
)


def eligible(session: Any, identity: str) -> Any:
    session.skin_status.require("fit")
    item = shortcut_effects.selected(session, identity)
    kind = property_kind(session, item) if isinstance(item, Shortcut) else item.numeric_type
    if kind != "REAL":
        raise ValueError("Fitting requires a continuous real-valued shortcut.")
    return item


def property_kind(session: Any, item: Any) -> str:
    descriptor = property_catalog.resolve(session.document, item.reference)
    scalar = descriptor.components == 1 or item.reference.component is not None
    if not descriptor.writable or not scalar:
        raise ValueError(descriptor.reason or "Fitting requires one editable scalar shortcut.")
    return str(descriptor.numeric_type)


def capture(
    document: Any, resources: Any, preferences: Any, identity: str, settings: Any, cancel: Any
) -> Any:
    session = isolated_execution.create(document, resources, preferences, cancel)
    try:
        eligible(session, identity)
        return collect(session, identity, settings, cancel)
    finally:
        session.close()


def collect(session: Any, identity: str, settings: Any, cancel: Any) -> Any:
    initial = session.assets[session.document.skin.final.asset].mesh
    values, training = skin_fit.sampling(session.engine, settings)
    positions = [sample(session, identity, float(v), initial, cancel) for v in values]
    replay = sample(session, identity, float(values[0]), initial, cancel)
    error = skin_fit.repeatability(session.engine, positions[0], replay)
    arrays = skin_reference_evaluation.geometry(initial)
    arrays.update(
        vertices=positions[0], targets=np.array(positions), values=values, training=training
    )
    if not np.all(np.diff(arrays["offsets"]) == 4):
        raise ValueError("Bone fitting requires quad topology.")
    arrays["quads"] = arrays["corners"].reshape(-1, 4)
    return arrays, error


def apply(session: Any, identity: str, value: float) -> Any:
    item = shortcut_effects.selected(session, identity)
    if isinstance(item, Shortcut):
        session.command("shortcut.set", reference=asdict(item.reference), value=value)
    else:
        session.command("driver.value", driver=item.id, value=value)
    return item


def update_affected(session: Any, item: Any) -> None:
    ports = shortcut_effects.ports(session.document, item)
    owners = {port.owner for port in ports}
    output_tasks.schedule(session, owners, explicit=True)
    construction_tasks.evaluate(session, list(owners))
    bones = owners & session.document.index.entities.keys()
    if bones:
        evaluation.request(session, bones)


def sample(session: Any, identity: str, value: float, initial: Any, cancel: Any) -> Any:
    if cancel.is_set():
        raise ValueError("Calculation cancelled.")
    item = apply(session, identity, value)
    update_affected(session, item)
    isolated_execution.settle(session, cancel)
    session.command("skin.evaluate")
    isolated_execution.settle(session, cancel)
    session.skin_status.require("fit")
    current = session.assets[session.document.skin.final.asset].mesh
    if not topology.same_topology(initial, current, cancel.handle):
        raise ValueError("Fitting sample changed skin vertex identity or connectivity.")
    return current.array(0)
