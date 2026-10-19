"""Role-aware anatomical surface capability and accepted output selection."""

from collections.abc import Mapping

from .entities import SCP
from .membranes import Membrane
from .results import EvaluationResult, Port
from .surface_references import SurfaceReference
from .tissues import TissueVCP


def anatomical(item: object) -> bool:
    return isinstance(item, (SCP, TissueVCP))


def roles(item: object, records: Mapping[str, object]) -> tuple[str, ...]:
    if isinstance(item, SCP):
        return ("SCP_GEOMETRY",)
    if isinstance(item, TissueVCP):
        base = ("TISSUE_BASE",) if isinstance(records.get(item.source), Membrane) else ()
        return (*base, "TISSUE_FINAL")
    return ()


def reference(target: str, records: Mapping[str, object], role: str = "") -> SurfaceReference:
    item = records.get(target)
    selected = role or ("SCP_GEOMETRY" if isinstance(item, SCP) else "TISSUE_FINAL")
    result = SurfaceReference(target, selected)
    if selected not in roles(item, records):
        raise ValueError(f"Object {target} does not provide the requested {selected} surface.")
    return result


def result(item: SCP | TissueVCP, role: str) -> EvaluationResult:
    if isinstance(item, SCP) and role == "SCP_GEOMETRY":
        return item.result
    if isinstance(item, TissueVCP) and role == "TISSUE_BASE":
        return item.base_result
    if isinstance(item, TissueVCP) and role == "TISSUE_FINAL":
        return item.final_result
    raise ValueError("Anatomical surface role does not match its provider.")


def port(reference: SurfaceReference) -> Port:
    names = {"SCP_GEOMETRY": "geometry", "TISSUE_BASE": "base", "TISSUE_FINAL": "final"}
    return Port(reference.target, names[reference.role])


def usable(result: EvaluationResult) -> bool:
    return bool(
        result.asset
        and not result.error
        and result.status not in ("failed", "invalid", "cancelled")
    )


def defaults(
    entities: tuple[SCP, ...], objects: tuple[object, ...]
) -> tuple[SurfaceReference, ...]:
    bones = (SurfaceReference(e.id) for e in entities if e.primitive or e.asset)
    tissues = (SurfaceReference(o.id, "TISSUE_FINAL") for o in objects if isinstance(o, TissueVCP))
    return (*bones, *tissues)


def from_port(value: Port) -> SurfaceReference:
    roles = {"geometry": "SCP_GEOMETRY", "base": "TISSUE_BASE", "final": "TISSUE_FINAL"}
    return SurfaceReference(value.owner, roles[value.output])
