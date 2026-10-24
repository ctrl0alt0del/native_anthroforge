"""Half-path expansion is source construction; mirror instances never run this stage."""

from dataclasses import replace
from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.document import Document
from anthroforge.core.mirroring import MirrorRule, SymmetricHalf
from anthroforge.native import construction, paths

from . import construction_policy, curve_sources, object_operations


def plane(document: Document, half: SymmetricHalf) -> MirrorRule:
    if half.rule:
        if half.rule not in document.mirrors.rules:
            raise ValueError("Symmetric construction's plane rule is missing.")
        return document.mirrors.rules[half.rule]
    return MirrorRule("half", axis=half.axis, shift=half.shift)


def local_frame(engine: Any, document: Any, item: Curve) -> Any:
    assert item.symmetric is not None
    world = curve_sources.world(engine, document, item.id)
    reflected = construction.matrix(engine, plane(document, item.symmetric).frame, world)
    return construction.matrix(engine, world, reflected, relative=True)


def create(
    session: Any, curve: str, rule: str = "", axis: str | None = None, shift: float | None = None
) -> None:
    item = object_operations.editable(session, curve)
    if not isinstance(item, Curve) or item.closed or item.symmetric:
        raise ValueError("Select an open Curve or Fiber as the authored half.")
    if len(item.points) < 3:
        raise ValueError("A symmetric loop needs two seam endpoints and an off-plane interior.")
    construction_policy.require_topology_edit(session.document, curve)
    half = definition(session.document, item.id, rule, axis, shift)
    candidate = replace(item, closed=True, symmetric=half)
    validate(session, candidate)
    object_operations.install(session, candidate)


def definition(document: Any, source: str, rule: str, axis: Any, shift: Any) -> SymmetricHalf:
    if rule or axis is not None or shift is not None:
        return SymmetricHalf(rule, axis or "X", shift or 0)
    choices = {v.rule for v in document.mirrors.instances.values() if v.source == source}
    if len(choices) > 1:
        raise ValueError("Choose an explicit plane for construction with multiple mirror rules.")
    return SymmetricHalf(next(iter(choices), ""))


def validate(session: Any, item: Curve) -> None:
    from .consumed_paths import accepted

    source = accepted(session.document, session.resources.paths, item.id)
    paths.symmetric(source.path, local_frame(session.engine, session.document, item))


def expand(engine: Any, document: Any, item: Curve, asset: Any, cancel: int) -> Any:
    if not item.symmetric:
        return asset
    path = paths.symmetric(asset.path, local_frame(engine, document, item), cancel)
    authored = replace(asset.authored, closed=True, symmetric=item.symmetric)
    return replace(asset, path=path, authored=authored)


def constrain(session: Any, before: Any, item: Any) -> Any:
    from anthroforge.native.curve_editing import constrain_seams

    if not isinstance(item, Curve) or not item.symmetric or not before.symmetric:
        return item
    if item.points == before.points:
        return item
    return constrain_seams(
        session.engine, item, local_frame(session.engine, session.document, item)
    )
