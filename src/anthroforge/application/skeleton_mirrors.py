"""Construction plane references resolve to destination rules; source rules never replace them."""

from typing import Any

from . import assembly_mirrors, skeleton_matching


def map_rules(preparation: Any) -> None:
    p = preparation
    for key in assembly_mirrors.required(p.source.document, p.selection):
        mapped = p.options.get("mirror_rules", {}).get(key, "")
        options = matching_rules(p.source.document, p.destination, key)
        mapped = mapped or p.ids.get(key, "") or (next(iter(options)) if len(options) == 1 else "")
        if mapped in p.destination.mirrors.rules:
            p.ids[key] = mapped
            p.mapping.reads.add("mirror:" + mapped)
        elif uses_plane(p, key):
            p.mapping.findings.append(
                dict(reference=key, message="Map construction mirror plane to a destination rule.")
            )


def uses_plane(p: Any, key: str) -> bool:
    return bool(assembly_mirrors.plane_consumers(p.selection, key))


def matching_rules(source: Any, destination: Any, key: str) -> set[str]:
    origins = skeleton_matching.origins(source, key)
    return {
        rule
        for rule in destination.mirrors.rules
        if origins & skeleton_matching.origins(destination, rule)
    }
