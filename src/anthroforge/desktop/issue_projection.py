"""Diagnostic presentation adds current labels, never geometry work or authored edits."""

import json

from anthroforge.application.issues.commands import available


def target_label(controller, target):
    index = controller.session.document.index
    item = index.entities.get(target) or index.controls.get(target)
    return item.name if item else "Document" if not target else "Removed target"


def rows(panel):
    view = panel.controller.session.issues.presentation
    values = view.filtered(panel.filters, "", panel.show_dismissed)
    for row in values:
        row["targetLabel"] = target_label(panel.controller, row["target"])
        row["issueId"] = row["id"]
    return [row for row in values if panel.search.casefold() in json.dumps(row).casefold()]


def detail(panel):
    system = panel.controller.session.issues
    repair = system.resolution.running.get(panel.selected)
    source = system.repository.records.get(panel.selected) or (repair.issue if repair else None)
    if source is None:
        return {}
    value = system.presentation.serialize(source)
    value["exists"] = panel.selected in system.repository.records
    value["targetLabel"] = target_label(panel.controller, value["target"])
    value["fixes"] = available(panel.controller.session, panel.selected)
    value["evidenceText"] = json.dumps(value["evidence"], indent=2)
    value["relatedTargets"] = related_targets(panel.controller, value["related"])
    value.update(repair_state(repair))
    return value


def related_targets(controller, targets):
    return [dict(id=key, label=target_label(controller, key)) for key in targets]


def repair_state(repair):
    return dict(
        repair=""
        if repair is None
        else repair.state + (": " + repair.error if repair.error else ""),
        repairActive=repair is not None and repair.state in ("REQUESTED", "VERIFYING"),
    )


def status_text(status):
    failed = [c for c in status["checks"] if c["status"] == "FAILED"]
    if failed:
        return "Check failed: " + failed[0]["provider"] + " · " + failed[0]["error"]
    if not status["complete"]:
        return "Checks pending, cancelled or not yet complete · retained findings may be stale"
    return (
        "Available checks complete" if status["issue_count"] else "No findings in available checks"
    )
