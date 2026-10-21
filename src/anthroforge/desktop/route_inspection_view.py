"""Presentation packing for bounded diagnostic records, no path computation."""

COLORS = {
    "Reference": "#fa86cb",
    "Planner": "#73b5fa",
    "Solver seed": "#f5c56d",
    "Solver trial": "#f5c56d",
    "Final": "#73e5bd",
}


def label(row):
    suffix = " · trial " + str(row["trial"]) if row["stage"] == "Solver trial" else ""
    return row["stage"] + " · span " + str(row["span"] + 1) + suffix


def selected(tool):
    rows = tool.report.get("records", [])
    return rows[tool.index] if 0 <= tool.index < len(rows) else {}


def lines(tool):
    row = selected(tool)
    if not row:
        return [], []
    paths = [dict(points=row["points"][:8192], color=COLORS[row["stage"]])]
    contacts = [p for c in row["contacts"][:512] for p in (c[8:11], c[11:14])]
    return paths, contacts if tool.show_contacts else []


def details(tool):
    row, report = selected(tool), tool.report
    if not report:
        return ""
    outcome = "Usable route" if report["success"] else report["error"]
    mode = "warm continuation" if report["warm"] else "planner run"
    note = viewport_limit(row)
    return "\n".join(
        filter(
            None,
            [report["backend"] + " · " + mode + " · " + outcome, row.get("termination", ""), note],
        )
    )


def viewport_limit(row):
    return (
        "Viewport truncated; report retains captured data."
        if len(row.get("points", [])) > 8192 or len(row.get("contacts", [])) > 512
        else ""
    )
