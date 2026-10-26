"""Document-owned stage provenance and dispatch-time contributor observations."""

from typing import Any

from anthroforge.core import anatomical_surfaces, skin_sources
from anthroforge.core.results import Port, ReadRevision
from anthroforge.core.surface_references import SurfaceReference

from . import dependencies


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
    candidates = skin_sources.candidates(document)
    ports = set().union(*(source_ports(source) for source in candidates))
    ports |= {Port(str(document.id), name) for name in ("skin_scope", "skin_envelope_settings")}
    return dependencies.closure(dependencies.graph(document), ports)


def construction(document: Any) -> set[Port]:
    ports = envelope(document) | {Port(str(document.id), "skin_topology_settings")}
    ports.update(Port(row.id, "pose") for row in document.entities if not row.parent)
    for source in skin_sources.candidates(document):
        if source.kind == "TISSUE":
            ports.update(Port(source.owner, name) for name in ("base", "rest", "intrinsic"))
    return dependencies.closure(dependencies.graph(document), ports)


def topology(document: Any) -> set[Port]:
    return construction(document) | {Port(str(document.id), "skin_envelope")}


def revision(document: Any, port: Port) -> ReadRevision | None:
    if port.owner != str(document.id):
        return None
    if port.output == "skin_scope":
        values = tuple(repr(source) for source in skin_sources.candidates(document))
        return ReadRevision(port.owner, port.output, 0, 0, values)
    if port.output.endswith("_settings") and port.output.startswith("skin_"):
        settings = getattr(document.skin, port.output.removeprefix("skin_"))
        return ReadRevision(
            port.owner, port.output, 0, 0, (repr(settings), repr(document.skin.contributors))
        )
    if port.output in ("skin_envelope", "skin_topology", "skin_final"):
        result = getattr(document.skin, port.output.removeprefix("skin_"))
        return ReadRevision(port.owner, port.output, result.authored_revision, result.revision)
    raise ValueError("Unknown document skin output: " + port.output)
