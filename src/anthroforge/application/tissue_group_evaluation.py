"""One owned native side graph, per-receiver policies, complete shell acceptance."""

from dataclasses import replace
from typing import Any

from anthroforge.native.stacking import resolve_group, surface

from . import tissue_evaluation, tissue_materials
from . import tissue_stack_evaluation as stacks
from . import tissue_stack_scene as inputs


def prepared(
    engine: Any, document: Any, resources: Any, targets: Any, cancel: int
) -> dict[str, Any]:
    result = {}
    for key in targets:
        item = document.object(key)
        tissue_evaluation.accepted(resources, item.intrinsic_result, "Intrinsic tissue")
        if item.stack_plan.error:
            raise ValueError(item.stack_plan.error)
        scene, native, _, _ = stacks.prepared(engine, document, resources, item, cancel)
        stacks.require_order(scene, native, item)
        result[key] = scene, native
    return result


def frozen(scene: Any, targets: Any) -> Any:
    rows, leases = {}, []
    for key, (owner, side) in scene.identities.items():
        if owner in targets:
            continue
        item = scene.document.object(owner)
        if stacks.usable_final(item):
            value = inputs.lease(scene.resources, item.final_material, side, scene.cancel, True)
            rows[key] = stacks.frozen_points(value.domain(key))
            leases.append(value)
    return rows, leases


def evaluate(engine: Any, document: Any, resources: Any, targets: Any, cancel: int) -> Any:
    scenes = prepared(engine, document, resources, targets, cancel)
    scene, native = next(iter(scenes.values()))
    accepted, _leases = frozen(scene, targets)
    owners = {
        key: worker
        for target, (snapshot, worker) in scenes.items()
        for key, row in snapshot.identities.items()
        if row[0] == target
    }
    output = resolve_group(engine, owners, accepted, cancel)
    values = assembled(engine, document, resources, scenes, output, cancel)
    native.validate_surfaces(surfaces(scene, values), cancel)
    return values


def assembled(
    engine: Any, document: Any, resources: Any, scenes: Any, output: Any, cancel: int
) -> Any:
    values = {}
    for key, (scene, _) in scenes.items():
        item = document.object(key)
        targets = [identity for identity, owner in scene.identities.items() if owner[0] == key]
        value = stacks.assembled(scene, item, output, targets)
        value = replace(value, material=tissue_materials.capture(engine, document, item, "final"))
        values[key] = tissue_evaluation.reuse(resources, item, "final", value, cancel)
    return values


def surfaces(scene: Any, values: Any) -> list[Any]:
    meshes, rows = scene.resources.meshes, []
    for item in inputs.participants(scene.document):
        value = values.get(item.id)
        if value is None and not stacks.usable_final(item):
            continue
        state = item.intrinsic_material if value else item.final_material
        assert state is not None
        mesh = (value.mesh or meshes[value.asset].mesh) if value else meshes[state.final].mesh
        rows.append(surface(meshes[state.own].mesh, mesh, state.frame, value is not None))
    return rows
