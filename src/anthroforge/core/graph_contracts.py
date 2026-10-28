"""Explicit identity/reference fields for copying editable graphs and retained metadata."""

from dataclasses import dataclass
from typing import Any

from . import construction as c
from . import (
    fibers,
    junctions,
    mirroring,
    parametric,
    results,
    shortcuts,
    surfaces,
    tissue_base,
    tissue_constraints,
    tissue_material,
    tissue_settings,
    tissue_stacking,
)
from .curve_engines import RoutingSettings
from .curve_uses import CurveUse
from .entities import SCP, Attachment, AttachmentReceipt
from .numeric_properties import PropertyRef
from .objects import ObjectRecord
from .reference_images import ReferenceImage
from .surface_branches import SurfaceBranch
from .surface_references import CapturedSurface, SurfaceBinding, SurfaceReference
from .tissues import TissueVCP


@dataclass(frozen=True)
class Field:
    mode: str = "mapped"
    relationship: str = ""
    required: bool = False
    output: str = ""


ID, MAPPED, RESOURCE = Field("id"), Field(), Field("resource")
PARENT = Field("reference", "parent", output="pose")
OWNER = Field("reference", "association")
SOURCE = Field("reference", "construction", True)
SUPPORT = Field("reference", "support")
RULE = Field("reference", "mirror")
PROPERTY = Field("reference", "property")

SCHEMAS: dict[type, dict[str, Field]] = {
    ObjectRecord: dict(id=ID, parent=PARENT, owners=OWNER),
    SCP: dict(id=ID, parent=PARENT, asset=RESOURCE),
    c.Control: dict(id=ID, follow=PARENT, owners=OWNER),
    c.CurvePoint: dict(id=ID, junction=SOURCE),
    c.BodyPiece: dict(id=ID, curve=SOURCE),
    c.PrimitiveParameters: dict(source=RESOURCE),
    c.Target: dict(owner=MAPPED, component=MAPPED),
    c.Deformer: dict(
        id=ID, control=SOURCE, members=Field("members"), weighted_members=Field("weights")
    ),
    CurveUse: dict(curve=SOURCE, reference_frame=PARENT),
    RoutingSettings: dict(obstacles=SUPPORT, excluded_obstacles=SUPPORT),
    parametric.Variable: dict(id=ID),
    fibers.Fiber: dict(attachment_asset=RESOURCE),
    fibers.FiberBinding: dict(point=MAPPED, target=SUPPORT, material_asset=RESOURCE, instance=RULE),
    fibers.FiberEdit: dict(baseline=RESOURCE, rebind=MAPPED, offsets=MAPPED),
    SurfaceReference: dict(target=SUPPORT, instance=RULE),
    SurfaceBinding: dict(material_asset=RESOURCE),
    CapturedSurface: dict(material_asset=RESOURCE),
    Attachment: dict(material_asset=RESOURCE, parent_instance=RULE),
    AttachmentReceipt: dict(parent=MAPPED, parent_asset=RESOURCE),
    junctions.Junction: dict(id=ID),
    junctions.PointRef: dict(curve=SOURCE, point=MAPPED),
    surfaces.SurfaceAlignment: dict(point=MAPPED, stations=Field("pairs")),
    surfaces.Surface: dict(main=MAPPED, accepted_parts=MAPPED),
    SurfaceBranch: dict(id=ID, boundary=SOURCE, curves=SOURCE, junctions=SOURCE),
    ReferenceImage: dict(source=RESOURCE),
    TissueVCP: dict(source=SOURCE),
    tissue_constraints.TissueConstraint: dict(
        id=ID, binding_asset=RESOURCE, material_asset=RESOURCE
    ),
    tissue_settings.TissuePart: dict(id=MAPPED),
    tissue_base.TissueBaseState: dict(parts=MAPPED),
    tissue_material.TissueMaterialState: dict(
        base=RESOURCE, rest=RESOURCE, own=RESOURCE, final=RESOURCE, crop_base=RESOURCE
    ),
    tissue_stacking.StackRelationship: dict(
        other=Field("reference", "stacking", output="final"), regions=Field("pairs")
    ),
    tissue_stacking.StackPlan: dict(providers=MAPPED),
    tissue_stacking.StackOrder: dict(
        first=MAPPED, second=MAPPED, underlying=MAPPED, covering=MAPPED
    ),
    results.EvaluationResult: dict(asset=RESOURCE, pending=MAPPED),
    results.ReadRevision: dict(owner=MAPPED, output=Field("port"), membership=MAPPED),
    PropertyRef: dict(target=PROPERTY, path=Field("property_path")),
    shortcuts.DrivingShortcut: dict(id=ID),
    shortcuts.DrivingFormula: dict(id=ID),
    shortcuts.FormulaInput: dict(driver=Field("reference", "driver", True)),
    shortcuts.AttachmentPolicy: dict(scope=Field("reference", "policy")),
    shortcuts.DescendantOverride: dict(target=Field("reference", "policy")),
    shortcuts.FormulaResult: dict(formula=MAPPED, pending=MAPPED),
    mirroring.MirrorRule: dict(target=MAPPED),
    mirroring.SharedMirrorTarget: dict(source=MAPPED, binding=MAPPED),
    mirroring.SymmetricHalf: dict(rule=RULE),
}


def schema(value: Any) -> dict[str, Field]:
    result = {}
    for cls in reversed(type(value).__mro__):
        result.update(SCHEMAS.get(cls, {}))
    return result
