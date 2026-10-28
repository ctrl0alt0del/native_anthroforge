"""A spatial issue can only highlight the original, still-current accepted surface."""

from math import dist

from anthroforge.application import spatial_evidence


def show(tool, identity):
    session = tool.controller.session
    if session.history.before is not None or session.waiting_save:
        raise ValueError("Finish the current edit before locating a geometry finding.")
    session.issues.listening.discover_changes()
    row = session.issues.presentation.get(identity)
    witness = row["evidence"].get("witness")
    if not witness:
        return
    locate(tool, identity, row, witness)


def locate(tool, identity, row, witness):
    if row["freshness"] != "current":
        raise ValueError("This finding is stale. Check geometry again before locating it.")
    tool.controller.select(row["target"])
    tool.synchronize()
    tool.set_view(row["stage"], "", "Overlay")
    tool.lines = lines(tool.controller.session, row, witness)
    tool.finding = identity
    tool.notify()
    tool.controller.frameRequested.emit(camera_frame(witness["bounds"]))


def camera_frame(bounds):
    low, high = bounds[:3], bounds[3:]
    center = [(a + b) / 2 for a, b in zip(low, high, strict=True)]
    return [*center, max(0.02, dist(low, high) * 1.25)]


def lines(session, row, witness):
    return spatial_evidence.lines(session, witness)
