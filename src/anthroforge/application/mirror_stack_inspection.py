"""Mirrored stacking evidence reflects an existing source relationship, never a mirror solve."""

from typing import Any

from anthroforge.core.mirroring import MirrorInstance, parse
from anthroforge.native import components, construction


def opposite(document: Any, target: str, rule: str) -> str:
    instance = parse(target)
    if instance:
        if instance.rule != rule:
            raise ValueError("The stacking participant uses another reflection plane.")
        return instance.source
    key = MirrorInstance(target, rule).id
    if key not in document.mirrors.instances:
        raise ValueError("This source relationship has no opposite stacking participant.")
    return key


def reflected(context: Any, target: str, options: Any, cancel: int) -> dict[str, Any]:
    from .stacking_inspection import compute_source

    instance = context.document.mirrors.instances[target]
    mapped = dict(options, other=opposite(context.document, options["other"], instance.rule))
    report = compute_source(context, instance.source, mapped, cancel)["report"]
    identities = {key: opposite(context.document, key, instance.rule) for key in report["names"]}
    plane = context.document.mirrors.plane(instance).frame
    return remap(context.engine, report, identities, plane)


def remap(engine: Any, report: Any, identities: Any, plane: Any) -> dict[str, Any]:
    report = dict(report)
    report["order"] = {
        k: identities.get(v, v) if isinstance(v, str) else v for k, v in report["order"].items()
    }
    for name in ("names", "assets", "stages"):
        report[name] = {identities[k]: v for k, v in report[name].items()}
    report["frames"] = {
        identities[k]: construction.matrix(engine, plane, v) for k, v in report["frames"].items()
    }
    report["lines"] = (
        components.transformed(engine, report["lines"], plane).tolist() if report["lines"] else []
    )
    report["method"] += "; reflected source evidence"
    return dict(report=report, lines=report["lines"])
