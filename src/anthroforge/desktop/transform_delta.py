"""World-space gesture deltas; distances in metres, angles in degrees, scale factors."""

from anthroforge.core.entities import IDENTITY
from anthroforge.native import construction


def axis_values(mode, axis, amount):
    values = [0, 0, 0, 0, 0, 0, 1, 1, 1]
    index = axis + {"Move": 0, "Rotate": 3, "Scale": 6}[mode]
    values[index] = max(0.01, 1 + amount) if mode == "Scale" else amount
    if mode == "Rotate":
        values[index] *= 60  # Compatibility with the original desktop adapter.
    return values


def matrix(engine, center, values):
    pivot = engine.transform([*center, 0, 0, 0, 1, 1, 1])
    inverse = construction.matrix(engine, pivot, IDENTITY, relative=True)
    return construction.matrix(
        engine, construction.matrix(engine, pivot, engine.transform(values)), inverse
    )


def object_values(engine, original, values):
    # SCPs store TRS, so non-uniform object scale stays on its local axes (no shear).
    result = list(original)
    result[6:] = [
        old * max(0.01, factor) for old, factor in zip(original[6:], values[6:], strict=True)
    ]
    delta = matrix(engine, original[:3], [*values[:6], 1, 1, 1])
    world = construction.matrix(engine, delta, engine.transform(result))
    return engine.decompose(world)
