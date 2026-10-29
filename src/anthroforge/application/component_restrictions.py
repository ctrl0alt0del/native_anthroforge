"""Component-specific restrictions project the existing formula/junction/deformer policies."""

from typing import Any

from anthroforge.core.numeric_properties import PropertyRef, overlaps

from . import membership


def curve_reason(session: Any, curve: Any, point: Any, part: str) -> str:
    if curve.engine == "PARAMETRIC":
        return "Generated positions are formula-controlled."
    if part == "position" and point.junction:
        junction = next(j for j in session.document.junctions if j.id == point.junction)
        if session.document.object(junction.source.curve).engine == "PARAMETRIC":
            return "This junction follows a Parametric source; edit its variables."
    return ""


def weight_binding(session: Any, item: Any, context: Any) -> Any:
    key = context.get("deformer")
    if not key:
        return None
    binding = next((b for b in getattr(item, "deformers", ()) if b.id == key), None)
    if binding is None:
        raise ValueError("Choose a deformer assigned to the inspected target.")
    if binding.target.stage == "CURVE":
        curve = session.document.object(binding.target.component)
        return membership.resolve(binding, curve)
    return binding


def weights(ref: Any, binding: Any, reason: str, writers: Any = ()) -> dict[str, Any]:
    reason = reason or driven_reason(writers, weight_property(ref, binding))
    if ref["part"] == "field":
        return dict(weight_editable=not reason, weight_reason=reason, weight=ref["weight"])
    if binding is None or not matches(ref, binding.target):
        return dict(weight_editable=False, weight_reason="Choose a matching context.deformer.")
    index = ref["index"]
    weight = binding.weights[index] if binding.weights else 1.0
    return dict(
        weight_editable=not reason,
        weight_reason=reason,
        weight=weight,
        deformer=binding.id,
        member=not binding.restrict or index in binding.indices,
    )


def weight_property(ref: Any, binding: Any) -> Any:
    if ref["part"] == "field":
        return PropertyRef(ref["owner"], ("fields", "@" + ref["field"], "values"), ref["index"])
    if binding is not None:
        return PropertyRef(ref["owner"], ("deformers", "@" + binding.id, "weights"), ref["index"])
    return None


def position_property(ref: Any) -> Any:
    part = ref["part"]
    if ref.get("curve"):
        return PropertyRef(ref["curve"], ("points", "@" + ref["point"], part))
    if part == "lattice":
        return PropertyRef(ref["owner"], ("points", "#" + str(ref["index"])))
    if part == "control":
        return PropertyRef(ref["owner"], ("transform", "position"))
    if part == "tissue_control":
        path = ("parts", "@" + ref["piece"], ref["side"], "inflation", "control")
        return PropertyRef(ref["owner"], path)
    return None


def driven_reason(writers: Any, reference: Any) -> str:
    if reference is not None:
        for target, identity in writers:
            if overlaps(target, reference):
                return f"This component is driven by formula {identity}; disable it to edit."
    return ""


def reference(group: Any, index: int, writers: Any) -> Any:
    row = group.reference(index)
    reason = row.get("reason", "") or driven_reason(writers, position_property(row))
    return dict(row, readonly=bool(reason), reason=reason)


def writers(document: Any) -> Any:
    return tuple(
        (f.target, f.id) for d in document.driving_shortcuts for f in d.formulas if f.enabled
    )


def matches(ref: Any, target: Any) -> bool:
    if target.stage == "CURVE":
        return bool(ref.get("curve") == target.component)
    if target.stage == "BASE":
        return bool(ref.get("piece") == target.component)
    return bool(ref["part"] == {"LATTICE": "lattice", "GEOMETRY": "vertex"}.get(target.stage))
