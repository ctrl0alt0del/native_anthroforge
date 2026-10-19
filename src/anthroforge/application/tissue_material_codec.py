"""Schema-four accepted material provenance has no runtime native handles."""

from typing import Any

from anthroforge.core.tissue_base import TissueBaseState
from anthroforge.core.tissue_constraints import TissueField
from anthroforge.core.tissue_material import TissueMaterialState
from anthroforge.core.tissue_settings import TissueCrop, TissueRelaxation

from .construction_codec import tuples
from .tissue_codec import constraint, part


def decode(data: Any) -> TissueMaterialState | None:
    if data is None:
        return None
    state = tuples(data)
    state["base_state"] = TissueBaseState(**tuples(state["base_state"]))
    state["parts"] = tuple(part(row) for row in state["parts"])
    state["constraints"] = tuple(constraint(row) for row in state["constraints"])
    state["fields"] = tuple(TissueField(**tuples(row)) for row in state["fields"])
    state["crop"] = TissueCrop(**tuples(state["crop"]))
    state["relaxation"] = TissueRelaxation(**tuples(state["relaxation"]))
    return TissueMaterialState(**state)
