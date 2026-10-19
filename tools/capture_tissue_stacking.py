"""Pin compact production vector-stacking inputs and outputs from the addon native library."""

import hashlib
import json
import sys
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np


def cases():
    from test_muscle_stacking import inflated

    a, b = inflated("a", 0, 0.3, (-2, 2, -2, 2)), inflated("b", 0.1, 0.2)
    yield "ordinary", [a, b], {}
    yield "chain", [a, b, inflated("c", 0.2, 0.25)], {}
    yield "zero_inflation", [replace(a, own=a.base), b], {}
    yield "fixed_conflict", [a, replace(b, material=replace(b.material, fixed=np.array([4])))], {}
    yield "coincident", [a, inflated("b", 0, 0.3)], {}
    tangent = replace(
        a, own=a.own + (0.2, 0, 0), direction=np.tile((2, 0, 3), (len(a.base), 1)) / np.sqrt(13)
    )
    yield "tangential", [tangent, b], dict(strength=0)
    yield from constraint_cases()
    yield from relationship_cases()


def constraint_cases():
    from core.muscle_stacking.constraints import MaterialConstraint
    from test_muscle_stacking import inflated

    a = inflated("a", 0, 0.2, (-1.4, -0.6, -1.4, -0.6))
    b = inflated("b", 0.1, 0.5)
    row = MaterialConstraint("midpoint", (0, 2), (0.5, 0.5))
    b = replace(b, material=replace(b.material, constraints=(row,)))
    yield "weighted_exact", [a, b], dict(radius=0.2, blend_distance=5)
    a = inflated("a", 0, 0.2, (-2, 2, -2, 2))
    b = inflated("b", 0.1, 0.4, n=2)
    yield "hidden_crop_variable", [a, cropped(b)], dict(strength=0)


def cropped(b):
    from core.muscle_stacking.constraints import MaterialConstraint

    row = MaterialConstraint("crosses_crop", (0, 3), (0.5, 0.5))
    material = replace(
        b.material,
        interpolation=b.material.interpolation[:3],
        weights=np.ones((3, 1)),
        constraints=(row,),
    )
    values = {key: getattr(b, key)[:3] for key in ("base", "own", "direction")}
    values.update(faces=np.array([[0, 1, 2]]), parts=np.array([0]), sources=np.array([0]))
    return replace(b, material=material, **values)


def domain(engine, item):
    data = {
        key: getattr(item, key).tolist()
        for key in ("base", "own", "direction", "faces", "parts", "sources")
    }
    data.update(
        id=engine.code("domain", item.key),
        family=engine.code("group", item.group),
        root=engine.code("root", item.key.root),
        enabled=item.enabled,
        side=int(item.key.side == "B"),
        allowance=item.displacement,
    )
    data["material"] = material_record(item.material)
    return data


def material_record(item):
    values = {
        key: getattr(item, key).tolist()
        for key in ("vertices", "faces", "interpolation", "weights", "fixed")
    }
    indices, weights = (
        np.zeros((len(item.constraints), 4), dtype=np.int64),
        np.zeros((len(item.constraints), 4)),
    )
    for i, row in enumerate(item.constraints):
        indices[i, : len(row.indices)], weights[i, : len(row.weights)] = row.indices, row.weights
    return dict(values, constraints=indices.tolist(), constraint_weights=weights.tolist())


def capture(name, values, settings):
    from core.muscle_stacking.native import NativeStackEngine
    from pair_fixture_adapter import wait

    config = configuration(settings)
    with NativeStackEngine() as engine:
        engine.submit(values, config, 1)
        wait(engine)
        return capture_record(engine, name, values, config)


def capture_record(engine, name, values, config):
    return dict(
        name=name,
        domains=[domain(engine, v) for v in values],
        settings=asdict(config),
        output=outputs(engine),
        **policy_record(engine, values, config),
        obstacles=[
            dict(vertices=b.vertices.tolist(), faces=b.faces.tolist()) for b in values[0].obstacles
        ],
    )


def configuration(settings):
    from core.muscle_pairs.model import DetectionSettings
    from core.muscle_stacking.model import StackingSettings

    if isinstance(settings, dict):
        return DetectionSettings(stacking=StackingSettings(**settings), workers=1)
    return replace(settings, workers=1)


def policy_record(engine, values, config):
    from core.muscle_relationships.native import arrays

    rows, faces = arrays(engine, values, config.relationships)
    names = ("first", "second", "cover", "excluded", "invalid", "offset", "count")
    policies = [dict({k: getattr(row.legacy, k) for k in names}, mode=row.mode) for row in rows]
    return dict(policies=policies, regions=np.asarray(faces).reshape((-1, 2)).tolist())


def relationship_cases():
    from test_explicit_stacking import config, crossing
    from test_muscle_stacking import inflated

    yield "explicit_crossing", crossing(), config()
    yield "requested_crossing", crossing(), config("requested")
    a, b = inflated("a", 0, 0.3), inflated("b", 0.1, 0.2)
    yield from policy_cases(a, b, config)
    yield from multiple_cases()


def policy_cases(a, b, config):
    from core.muscle_relationships.policy import RelationshipPolicy

    policy = RelationshipPolicy(
        (("a", "source", "A"), ("b", "source", "A")), excluded=True, mode="automatic"
    )
    yield "excluded_pair", [a, b], replace(config(), relationships=(policy,))
    policy = replace(
        policy, cover=("b", "source", "A"), excluded=False, mode="explicit", region=((0, 0), (0, 1))
    )
    yield "selected_region", [a, b], replace(config(), relationships=(policy,))


def multiple_cases():
    from stack_multi_fixtures import providers, settings
    from test_muscle_stacking import inflated
    from test_muscle_stacking_material import box

    yield "multiple_providers", providers(n=7), settings()
    a, b = inflated("a", 0, 0.3), inflated("b", 0.1, 0.2)
    bone = box((-0.25, -0.25, 0.45), (0.25, 0.25, 0.55))
    yield "bone_penetration", [replace(a, obstacles=(bone,)), replace(b, obstacles=(bone,))], {}


def outputs(engine):
    surfaces = engine.surfaces()
    return {
        str(row.id): dict(
            status=row.status,
            message=row.message.decode(),
            points=surfaces[engine.domains[row.id].key].tolist(),
        )
        for row in engine.outputs
    }


def main(addon, target):
    sys.path[:0] = [str(addon), str(addon / "tests/unit")]
    from core.muscle_stacking.abi import library

    rows = [capture(*case) for case in cases()]
    binary = Path(library()._name)
    record = dict(
        source=str(binary), sha256=hashlib.sha256(binary.read_bytes()).hexdigest(), cases=rows
    )
    target.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"Captured {len(rows)} production stacking cases.")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
