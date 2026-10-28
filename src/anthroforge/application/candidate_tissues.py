"""Preserve the production coupled stacking bundle in isolated evaluation."""

from dataclasses import replace
from typing import Any

from anthroforge.core import tissue_groups
from anthroforge.core.results import Port

from . import tissue_group_evaluation, tissue_group_tasks, tissue_results


def grouped(context: Any, port: Port) -> bool:
    if port.output != "final":
        return False
    members = tissue_groups.members(context.document.registry.authored, port.owner)
    if len(members) <= 1:
        return False
    evaluate(context, members)
    return True


def evaluate(context: Any, members: Any) -> None:
    outputs = tissue_group_evaluation.evaluate(
        context.engine, context.document, context.resources, members, context.cancel.handle
    )
    reads = tissue_group_tasks.observed(context.document, members)
    changed = {key: accepted(context, key, output, reads) for key, output in outputs.items()}
    context.document = replace(
        context.document, objects=tuple(changed.get(o.id, o) for o in context.document.objects)
    )
    context.completed_batch.update(Port(key, "final") for key in members)
    context.prepared.update(context.completed_batch)


def accepted(context: Any, key: str, output: Any, reads: Any) -> Any:
    item = context.document.object(key)
    asset = tissue_results.register(context, output, "final")
    result = tissue_results.accept(context.document, item, "final", reads, asset, output)
    return replace(item, **tissue_results.publication(item, "final", result, output))
