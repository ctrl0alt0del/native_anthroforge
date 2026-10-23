"""Resolve Auto from owned surface construction capabilities, independent of host objects."""

from .entities import SCP


def supports_deformation_flow(parent: SCP | None) -> bool:
    return bool(parent and parent.primitive and parent.primitive.kind == "BODY")


def uses_deformation_flow(child: SCP, parent: SCP | None) -> bool:
    strategy = child.attachment.strategy
    return strategy == "DEFORMATION_FLOW" or (
        strategy == "AUTO" and supports_deformation_flow(parent)
    )
