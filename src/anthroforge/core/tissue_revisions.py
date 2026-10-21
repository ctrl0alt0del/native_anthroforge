"""Tissue setting ownership determines the first invalidated phase, independently of results."""

from .results import Port

PHASES = ("base", "rest", "intrinsic", "plan", "final")
SETTINGS = {
    "base": frozenset(("source", "resolution")),
    "rest": frozenset(("parts", "both_sides", "reverse", "fields")),
    "intrinsic": frozenset(("relaxation", "constraints", "crop")),
    "plan": frozenset(("stacking", "stack_settings", "stack_relationships", "group")),
    "final": frozenset(),
}


def ports(identity: str, fields: set[str]) -> set[Port]:
    return {Port(identity, phase) for phase, settings in SETTINGS.items() if fields & settings}


def changes(before: object, ports: set[Port]) -> dict[str, int]:
    return {
        phase + "_revision": getattr(before, phase + "_revision") + 1
        for phase in PHASES
        if any(port.output == phase for port in ports)
    }
