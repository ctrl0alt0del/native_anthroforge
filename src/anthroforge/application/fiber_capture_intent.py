"""Resolve endpoint intent against the accepted construction captured at dispatch."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from .consumed_paths import accepted


def resolve(document: Any, resources: Any, spec: Any) -> Any:
    curve = accepted(document, resources.paths, spec.source).authored
    identities = dict(spec.identities)
    for point in curve.points:
        identities.setdefault(point.id, str(uuid4()))
    endpoints = endpoint_mapping(curve, spec)
    bindings = tuple((endpoints.get(p, p), target, scope) for p, target, scope in spec.bindings)
    if {row[0] for row in bindings} - {p.id for p in curve.points}:
        raise ValueError("A chosen binding point is absent from the accepted curve.")
    return replace(spec, identities=identities, bindings=bindings)


def endpoint_mapping(curve: Any, spec: Any) -> dict[str, str]:
    if curve.engine != "PARAMETRIC" or not spec.endpoints or curve.closed:
        return {}
    return dict(zip(spec.endpoints, (curve.points[0].id, curve.points[-1].id), strict=True))
