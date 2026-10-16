"""Stable authored point identities resolve to native indices only at evaluation."""

from dataclasses import replace

from anthroforge.core.construction import Curve, Deformer


def tokens(curve: Curve) -> tuple[str, ...]:
    return tuple(p.id + ":" + part for p in curve.points for part in ("left", "point", "right"))


def assign(binding: Deformer, curve: Curve) -> Deformer:
    points = tokens(curve)
    if any(i >= len(points) for i in binding.indices):
        raise ValueError("Hook membership is outside the curve point range.")
    return replace(binding, members=tuple(points[i] for i in binding.indices), restrict=True)


def resolve(binding: Deformer, curve: Curve) -> Deformer:
    lookup = {key: i for i, key in enumerate(tokens(curve))}
    indices = (
        tuple(lookup[m] for m in binding.members if m in lookup)
        if binding.members
        else binding.indices
    )
    return replace(
        binding,
        indices=indices,
        weights=resolved_weights(binding, curve),
        restrict=binding.restrict or bool(binding.members),
    )


def resolved_weights(binding: Deformer, curve: Curve) -> tuple[float, ...]:
    weights = dict(binding.weighted_members)
    return tuple(weights.get(key, 0.0) for key in tokens(curve)) if weights else binding.weights


def remap_weights(binding: Deformer, mapping: dict[str, str]) -> tuple[tuple[str, float], ...]:
    return tuple((remap((key,), mapping)[0], weight) for key, weight in binding.weighted_members)


def assign_weights(binding: Deformer, curve: Curve) -> Deformer:
    points = tokens(curve)
    if binding.weights and len(binding.weights) != len(points):
        raise ValueError("Curve influence weights must match the current control/handle count.")
    weights = tuple(zip(points, binding.weights, strict=True)) if binding.weights else ()
    return replace(binding, weighted_members=weights)


def remap(members: tuple[str, ...], mapping: dict[str, str]) -> tuple[str, ...]:
    return tuple(
        mapping.get(member.rsplit(":", 1)[0], member.rsplit(":", 1)[0])
        + ":"
        + member.rsplit(":", 1)[1]
        for member in members
    )
