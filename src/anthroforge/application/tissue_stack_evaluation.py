"""Native order planning and selected final evaluation consume owned accepted material."""

from contextlib import contextmanager
from typing import Any

import numpy as np

from anthroforge.core.anatomical_surfaces import usable
from anthroforge.core.tissue_stacking import StackOrder, StackPlan
from anthroforge.native.stacking import StackSession, dependencies, surface
from anthroforge.native.stacking_leases import acquire
from anthroforge.native.tissue_stacking import assemble

from . import mirror_stacking
from . import tissue_stack_policy as policy
from . import tissue_stack_scene as scene_inputs
from .tissue_output import TissueOutput


def captured(document: Any, resources: Any, item: Any, cancel: int) -> Any:
    scene = scene_inputs.StackScene(document, resources, item.id, cancel)
    if item.id in scene.failures:
        raise ValueError(scene.failures[item.id])
    if not any(key[0] == item.id for key in scene.leases):
        raise ValueError(
            "Stacking requires accepted surface material; evaluate intrinsic tissue first."
        )
    return scene


@contextmanager
def prepared(engine: Any, document: Any, resources: Any, item: Any, cancel: int) -> Any:
    scene = captured(document, resources, item, cancel)
    with acquire(engine, item.id) as native:
        output, orders = detect(scene, native, item)
        yield scene, native, output, orders


def detect(scene: Any, native: StackSession, item: Any) -> Any:
    policies, regions = policy.policies(scene)
    bones, _buffers = scene_inputs.obstacles(native.engine, scene.document, scene.resources)
    output, orders = native.plan(
        list(scene.domains.values()),
        policy.settings(item.stack_settings),
        policies=policies,
        regions=regions,
        obstacles=bones,
        cancel=scene.cancel,
        metadata_only=True,
    )
    return output, orders


def plan(engine: Any, document: Any, resources: Any, item: Any, cancel: int) -> TissueOutput:
    if not item.stacking:
        return TissueOutput(plan=StackPlan())
    with prepared(engine, document, resources, item, cancel) as (scene, native, output, orders):
        providers = {
            scene.identities[b][0]
            for a, b in dependencies(native)
            if scene.identities[a][0] == item.id
        }
        return TissueOutput(plan=description(scene, providers, output, orders))


def description(scene: Any, providers: Any, output: Any, orders: Any) -> StackPlan:
    errors = [
        row["message"]
        for key, row in output.items()
        if scene.identities[key][0] == scene.target and row["status"] > 1
    ]
    values = tuple(
        order(scene, row)
        for row in orders
        if scene.target in (scene.identities[row.first][0], scene.identities[row.second][0])
    )
    return StackPlan(tuple(sorted(providers)), values, "; ".join(errors))


def order(scene: Any, row: Any) -> StackOrder:
    first, side = scene.identities[row.first]
    second, other = scene.identities[row.second]
    return StackOrder(
        first,
        second,
        side,
        other,
        scene.identities.get(row.underlying, ("", ""))[0],
        scene.identities.get(row.covering, ("", ""))[0],
        row.status,
        row.diagnostic.decode(),
        row.fragments,
    )


def frozen(scene: Any) -> tuple[dict[int, Any], list[Any]]:
    rows, leases = {}, []
    for key, (owner, side) in scene.identities.items():
        if owner == scene.target:
            continue
        item = mirror_stacking.item(scene.document, owner)
        if not usable_final(item):
            continue
        state = mirror_stacking.material(scene, owner, True)
        value = scene_inputs.lease(scene.resources, state, side, scene.cancel, True)
        domain = value.domain(key)
        rows[key] = frozen_points(domain)
        leases.append(value)
    return rows, leases


def frozen_points(domain: Any) -> dict[str, Any]:
    return dict(
        status=0, points=np.ctypeslib.as_array(domain.own, (3 * domain.vertices,)).reshape(-1, 3)
    )


def usable_final(item: Any) -> bool:
    return bool(
        item.final_material is not None
        and usable(item.final_result)
        and item.final_material.own == item.intrinsic_material.own
    )


def evaluate(engine: Any, document: Any, resources: Any, item: Any, cancel: int) -> TissueOutput:
    if item.stack_plan.error:
        raise ValueError(item.stack_plan.error)
    with prepared(engine, document, resources, item, cancel) as (scene, native, _, _):
        return resolve(scene, native, item, cancel)


def resolve(scene: Any, native: StackSession, item: Any, cancel: int) -> TissueOutput:
    require_order(scene, native, item)
    accepted, _leases = frozen(scene)
    targets = tuple(key for key, row in scene.identities.items() if row[0] == item.id)
    if not targets:
        return TissueOutput(asset=item.intrinsic_result.asset)
    output, _ = native.resolve(accepted, targets, cancel)
    result = assembled(scene, item, output, targets)
    native.validate_surfaces(complete_surfaces(scene, item, result.mesh), cancel)
    return result


def require_order(scene: Any, native: StackSession, item: Any) -> None:
    providers = {
        scene.identities[b][0] for a, b in dependencies(native) if scene.identities[a][0] == item.id
    }
    if providers != set(item.stack_plan.providers):
        raise ValueError("Stacking order changed; reevaluate its plan before the final surface.")


def assembled(scene: Any, item: Any, output: Any, targets: Any) -> TissueOutput:
    for key in targets:
        if output[key]["status"] > 1:
            raise ValueError(output[key]["message"])
    first, second = scene.leases[item.id, "a"], scene.leases.get((item.id, "b"))
    a = output_points(output, item.id, "a")
    b = output_points(output, item.id, "b") if second else ()
    return TissueOutput(mesh=assemble(first, a, second, b, scene.cancel))


def output_points(output: Any, target: str, side: str) -> Any:
    row = output.get(scene_inputs.identity(target, side))
    return row["points"] if row else np.empty((0, 3))


def complete_surfaces(scene: Any, item: Any, final: Any) -> list[Any]:
    meshes, state = scene.resources.meshes, item.intrinsic_material
    rows = [surface(meshes[state.own].mesh, final, state.frame)]
    for owner in {key[0] for key in scene.leases}:
        if owner == item.id or not usable_final(mirror_stacking.item(scene.document, owner)):
            continue
        accepted = mirror_stacking.material(scene, owner, True)
        rows.append(
            surface(meshes[accepted.own].mesh, meshes[accepted.final].mesh, accepted.frame, False)
        )
    return rows
