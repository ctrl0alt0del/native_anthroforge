"""Owned stage selections for comparison; references never enter the anatomy registry."""

from dataclasses import asdict, dataclass
from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.results import geometry_asset
from anthroforge.core.tissues import TissueVCP

from . import dependencies
from . import reconstruction_state as records
from . import tissue_inspection_stages as stages
from .inspection_context import InspectionContext
from .object_frames import Frames


@dataclass(frozen=True)
class Layer:
    identity: str
    resource: Any
    frame: tuple[float, ...]
    kind: str = "MESH"
    color: str = "#b87d72"
    lineage: Any = None


@dataclass(frozen=True)
class View:
    source: InspectionContext
    subject: str
    stage: str
    variant: str
    layers: tuple[Layer, ...]
    provenance: Any


def capture(session: Any, subject: str, stage: str = "final", variant: str = "") -> View:
    document = records.scene(session, variant)
    item = records.subject(session, subject, variant)
    imported = next((s for s in records.state(session).stages if s.id == stage), None)
    context = InspectionContext(
        document, session.resources.snapshot(), session.engine, document.workspaces[0]
    )
    if imported:
        if imported.subject != subject:
            raise ValueError("Reference belongs to another anatomical instance.")
        asset = session.resources.meshes[imported.asset]
        layers: tuple[Layer, ...] = (Layer(imported.id, asset.mesh, imported.frame),)
        return View(context, subject, stage, variant, layers, asdict(imported))
    layers = fibers(context, item) if stage == "fibers" else (accepted(context, item, stage),)
    return View(context, subject, stage, variant, layers, provenance(session, document, variant))


def provenance(session: Any, document: Any, variant: str) -> dict[str, Any]:
    mapping = records.state(session).variant(variant).construction_map if variant else ()
    return dict(revision=document.revision, construction_map=mapping)


def accepted(context: Any, item: Any, stage: str) -> Layer:
    if isinstance(item, TissueVCP):
        result, frame = stages.result(item, stage), stages.frame(context, item, stage)
        key, lineage = result.asset, stages.material(item, stage)
        if stage == "base" and item.base_state.kind == "POINT":
            return Layer(item.id, None, tuple(frame), "POINT", item.color)
    else:
        if stage not in ("geometry", "final"):
            raise ValueError("This object exposes only its accepted geometry.")
        key, frame = geometry_asset(item), Frames(context.engine, context.document).world(item.id)
        lineage = (item.id, key)
    return layer(context, item.id, key, frame, lineage, item.color)


def layer(context: Any, identity: str, key: str, frame: Any, lineage: Any, color: str) -> Layer:
    if key in context.resources.meshes:
        return Layer(
            identity, context.resources.meshes[key].mesh, tuple(frame), lineage=lineage, color=color
        )
    if key in context.resources.paths:
        return Layer(
            identity, context.resources.paths[key].path, tuple(frame), "PATH", color, lineage
        )
    raise ValueError("The selected stage has no accepted geometry.")


def fibers(context: Any, item: Any) -> tuple[Layer, ...]:
    from anthroforge.core.results import Port

    ports = dependencies.ports(context.document, Port(item.id, "geometry"))
    curves = [context.document.object(p.owner) for p in ports if p.output == "path"]
    frames = Frames(context.engine, context.document)
    return tuple(
        layer(context, c.id, c.result.asset, frames.world(c.id), None, "#b996cc")
        for c in curves
        if isinstance(c, Curve) and c.result.asset
    )


def options(session: Any, subject: str) -> dict[str, Any]:
    value = records.state(session)
    variants = [
        ("", "Accepted anatomy"),
        *((v.id, v.name) for v in value.variants if subject in v.subjects),
    ]
    rows = [option(session, subject, key, name) for key, name in variants]
    imported = [
        dict(id=s.id, name=s.name or s.stage.title(), variant=s.variant, stage=s.id)
        for s in value.stages
        if s.subject == subject
    ]
    return dict(views=[item for group in rows for item in group] + imported)


def option(session: Any, subject: str, key: str, name: str) -> Any:
    item = records.subject(session, subject, key)
    roles = (*stages.STAGES, "fibers") if isinstance(item, TissueVCP) else ("final",)
    return [
        dict(id=key + ":" + role, name=name + " · " + role, variant=key, stage=role)
        for role in roles
        if available(session, subject, role, key)
    ]


def available(session: Any, subject: str, stage: str, variant: str) -> bool:
    try:
        return bool(capture(session, subject, stage, variant).layers)
    except ValueError:
        return False


def report(view: View) -> dict[str, Any]:
    return dict(
        subject=view.subject,
        stage=view.stage,
        variant=view.variant,
        provenance=view.provenance,
        revision=view.source.document.revision,
        layers=[
            dict(id=entry.identity, frame=entry.frame, kind=entry.kind) for entry in view.layers
        ],
    )
