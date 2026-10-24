"""Mirrored stacking participants are immutable, reflected accepted source providers."""

from dataclasses import replace
from typing import Any

from anthroforge.core.anatomical_surfaces import usable
from anthroforge.core.mirroring import parse, source
from anthroforge.core.results import Port
from anthroforge.core.tissues import TissueVCP
from anthroforge.native.construction import matrix


def item(document: Any, owner: str) -> Any:
    return document.object(source(owner))


def material(scene: Any, owner: str, final: bool = False) -> Any:
    instance = parse(owner)
    tissue = item(scene.document, owner)
    state = tissue.final_material if final or instance else tissue.intrinsic_material
    if state is None or (instance and not usable(tissue.final_result)):
        raise ValueError("Mirrored stacking needs its source's accepted final surface.")
    if not instance:
        return state
    frame = scene.document.mirrors.plane(instance).frame
    engine = scene.resources.meshes[state.base].mesh.engine
    return replace(state, frame=matrix(engine, frame, state.frame))


def participants(document: Any, target: str = "") -> tuple[Any, ...]:
    return tuple(
        v
        for v in document.mirrors.instances.values()
        if v.source != target
        and isinstance(document.object(v.source), TissueVCP)
        and document.object(v.source).stacking
        and document.object(v.source).final_material is not None
    )


def add(scene: Any, families: Any) -> None:
    labels = {t.id: family for t, family in families}
    for instance in participants(scene.document, scene.target):
        if instance.source not in labels:
            continue
        add_instance(scene, instance, labels[instance.source])


def add_instance(scene: Any, instance: Any, family: int) -> None:
    try:
        state = material(scene, instance.id)
        for side in ("a", "b") if state.both_sides else ("a",):
            scene.add_side(instance.id, state, side, family)
    except ValueError as error:
        scene.failures[instance.id] = str(error)
        scene.discard(instance.id)


def ports(document: Any, target: str) -> set[Port]:
    return {
        value
        for instance in participants(document, target)
        for value in (Port(instance.id, "final"), Port(instance.rule, "mirror"))
    }
