"""Component-specific restrictions project the existing formula/junction/deformer policies."""

from typing import Any

from anthroforge.core.numeric_properties import PropertyRef

from . import membership, property_guards


def curve_reason(session: Any, curve: Any, point: Any, part: str) -> str:
    if curve.engine == "PARAMETRIC":
        return "Generated positions are formula-controlled."
    reference = PropertyRef(
        curve.id, ("points", "@" + point.id, "position" if part == "position" else part)
    )
    driven = property_guards.driven(session.document, reference)
    if driven:
        return "This component is driven by formula " + driven + "; disable it to edit."
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


def weights(ref: Any, binding: Any, reason: str) -> dict[str, Any]:
    if ref["part"] == "field":
        return dict(weight_editable=not reason, weight_reason=reason, weight=ref["weight"])
    if binding is None or not matches(ref, binding.target):
        return dict(weight_editable=False, weight_reason="Choose a matching context.deformer.")
    index = ref["index"]
    weight = binding.weights[index] if binding.weights else 1.0
    member = not binding.restrict or index in binding.indices
    return dict(
        weight_editable=not reason,
        weight_reason=reason,
        weight=weight,
        deformer=binding.id,
        member=member,
    )


def matches(ref: Any, target: Any) -> bool:
    if target.stage == "CURVE":
        return bool(ref.get("curve") == target.component)
    if target.stage == "BASE":
        return bool(ref.get("piece") == target.component)
    return bool(ref["part"] == {"LATTICE": "lattice", "GEOMETRY": "vertex"}.get(target.stage))
