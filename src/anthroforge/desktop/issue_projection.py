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
    if panel.selected not in system.repository.records:
        return {}
    value = system.presentation.get(panel.selected)
    value["targetLabel"] = target_label(panel.controller, value["target"])
    value["fixes"] = available(panel.controller.session, panel.selected)
    value["evidenceText"] = json.dumps(value["evidence"], indent=2)
    value["relatedTargets"] = [
        dict(id=key, label=target_label(panel.controller, key)) for key in value["related"]
    ]
    value.update(repair_state(system.resolution.running.get(panel.selected)))
    return value


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
