"""Document-owned stage provenance and dispatch-time contributor observations."""

from typing import Any

from anthroforge.core import anatomical_surfaces, skin_sources
from anthroforge.core.results import Port, ReadRevision
from anthroforge.core.surface_references import SurfaceReference

from . import dependencies

ENVELOPE_FIELDS = (
    "owner",
    "collagen_mode",
    "collagen",
    "painted",
    "gap_mode",
    "gap_limit_ratio",
    "gap_strength",
)


def reference(source: skin_sources.Source) -> SurfaceReference:
    role = "SCP_GEOMETRY" if source.kind == "SCP" else "TISSUE_FINAL"
    return SurfaceReference(source.owner, role, source.instance)


def source_ports(source: skin_sources.Source) -> set[Port]:
    if source.kind != "FIBER":
        return anatomical_surfaces.inputs(reference(source))
    ports = {Port(source.owner, "path"), Port(source.owner, "pose")}
    if source.instance:
        ports.add(Port(source.instance, "mirror"))
    return ports


def envelope(document: Any) -> set[Port]:
    candidates = skin_sources.contributors(document)
    ports = set().union(*(source_ports(source) for source in candidates))
    ports |= {Port(str(document.id), name) for name in ("skin_scope", "skin_envelope_settings")}
    return dependencies.closure(dependencies.graph(document), ports)


def construction(document: Any) -> set[Port]:
    ports = envelope(document) | {Port(str(document.id), "skin_topology_settings")}
    ports.add(Port(str(document.id), "skin_guide_scope"))
    ports.update(set().union(*(source_ports(source) for source in skin_sources.guides(document))))
    ports.update(Port(row.id, "pose") for row in document.entities if not row.parent)
    for source in skin_sources.candidates(document):
        if source.kind == "TISSUE":
            ports.update(Port(source.owner, name) for name in ("base", "rest", "intrinsic"))
    return dependencies.closure(dependencies.graph(document), ports)


def topology(document: Any) -> set[Port]:
    return construction(document) | {Port(str(document.id), "skin_envelope")}


def reference_build(document: Any) -> set[Port]:
    ports = complete_build(document)
    ports.update(
        Port(str(document.id), name) for name in ("skin_topology", "skin_pending_topology")
    )
    return ports


def complete_build(document: Any) -> set[Port]:
    return construction(document) | {Port(str(document.id), "skin_deformation_settings")}


def revision(document: Any, port: Port) -> ReadRevision | None:
    if port.owner != str(document.id):
        return None
    if port.output == "skin_reference":
        return ReadRevision(port.owner, port.output, 0, 0, (document.skin.reference,))
    if port.output in ("skin_scope", "skin_guide_scope"):
        select = skin_sources.contributors if port.output == "skin_scope" else skin_sources.guides
        values = tuple(repr(source) for source in select(document))
        return ReadRevision(port.owner, port.output, 0, 0, values)
    if port.output.endswith("_settings") and port.output.startswith("skin_"):
        return settings_revision(document, port)
    if port.output in ("skin_envelope", "skin_topology", "skin_pending_topology", "skin_final"):
        result = getattr(document.skin, port.output.removeprefix("skin_"))
        return ReadRevision(port.owner, port.output, result.authored_revision, result.revision)
    raise ValueError("Unknown document skin output: " + port.output)


def settings_revision(document: Any, port: Port) -> ReadRevision:
    settings = getattr(document.skin, port.output.removeprefix("skin_"))
    if port.output == "skin_envelope_settings":
        owners = {source.owner for source in skin_sources.contributors(document)}
        rows = tuple(
            tuple(getattr(row, key) for key in ENVELOPE_FIELDS)
            for row in document.skin.contributors
            if row.owner in owners
        )
    else:
        rows = document.skin.contributors
    return ReadRevision(port.owner, port.output, 0, 0, (repr(settings), repr(rows)))
