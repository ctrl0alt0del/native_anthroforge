"""One API-held immutable inspection; job/viewport leases have independent lifetimes."""

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from anthroforge.core.inspection_layers import Layer

from . import query_pages
from .query_projection import plain

MESH_BUFFERS = dict(positions=0, corners=1, offsets=2, triangles=3, triangle_faces=4)
PATH_BUFFERS = dict(samples=0, parameters=1, positions=0)
LAYER_FIELDS = (
    "subject",
    "kind",
    "frame",
    "side",
    "stage",
    "status",
    "reason",
    "category",
    "color",
    "lineage",
)


@dataclass(frozen=True)
class Snapshot:
    identity: str
    kind: str
    token: str
    document: str
    revision: int
    layers: tuple[Layer, ...]
    camera: tuple[float, ...]
    engine: Any
    provenance: Any


def capture(session: Any, kind: str, token: str) -> dict[str, Any]:
    from . import inspection_candidate_layers, inspection_sources

    state = inspection_sources.ready(session, kind, token)
    layers = inspection_candidate_layers.capture(session, kind, state)
    value = frozen(session, kind, token, state, layers)
    session._editing.values["inspection_snapshot"] = value
    return status(session, value.identity)


def frozen(session: Any, kind: str, token: str, state: Any, layers: Any) -> Snapshot:
    return Snapshot(
        str(uuid4()),
        kind,
        token,
        str(session.document.id),
        session.document.revision,
        layers,
        tuple(session.workspace.camera),
        session.engine,
        tuple(getattr(state, "reads", ())),
    )


def selected(session: Any, snapshot: str) -> Snapshot:
    value = session._editing.values.get("inspection_snapshot")
    if not isinstance(value, Snapshot) or snapshot != value.identity:
        raise ValueError("Unknown or released inspection snapshot.")
    return value


def status(session: Any, snapshot: str) -> dict[str, Any]:
    value = selected(session, snapshot)
    current = source_status(session, value.kind)
    return dict(
        snapshot=value.identity,
        kind=value.kind,
        token=value.token,
        document=value.document,
        revision=value.revision,
        current=str(session.document.id) == value.document
        and current["state"] == "ready"
        and current.get("token") == value.token,
        source_state=current["state"],
        layers=[metadata(layer) for layer in value.layers],
    )


def source_status(session: Any, kind: str) -> Any:
    from . import inspection_sources

    try:
        return inspection_sources.status(session, kind)
    except ValueError as error:
        return dict(state="unavailable", error=str(error), token="")


def release(session: Any, snapshot: str) -> None:
    selected(session, snapshot)
    session._editing.values.pop("inspection_snapshot", None)


def metadata(layer: Layer) -> dict[str, Any]:
    names = MESH_BUFFERS if layer.kind == "MESH" else PATH_BUFFERS if layer.kind == "PATH" else {}
    return dict(
        **layer_metadata(layer),
        closed=layer.resource.closed if layer.kind == "PATH" else None,
        buffers={name: buffer_description(array(layer, name)) for name in names},
        coordinates="right-handed Z-up; local metres; row-major local-to-world frame",
    )


def layer_metadata(layer: Layer) -> dict[str, Any]:
    return dict(
        id=layer.identity,
        provenance=plain(dict(layer.provenance)),
        **{key: plain(getattr(layer, key)) for key in LAYER_FIELDS},
    )


def array(layer: Layer, name: str) -> Any:
    options = MESH_BUFFERS if layer.kind == "MESH" else PATH_BUFFERS if layer.kind == "PATH" else {}
    if name not in options or layer.resource is None:
        raise ValueError("This layer has no buffer named " + name)
    values = layer.resource.array(options[name])
    return values[:, :3] if layer.kind == "PATH" and name == "positions" else values


def buffer_description(values: Any) -> dict[str, Any]:
    return dict(shape=values.shape, dtype=str(values.dtype))


def geometry(
    session: Any, snapshot: str, layer: str, buffer: str, offset: int = 0, limit: int = 4096
) -> dict[str, Any]:
    start, end = query_pages.bounds(offset, limit)
    value = selected(session, snapshot)
    item = next((r for r in value.layers if r.identity == layer), None)
    if item is None:
        raise ValueError("Unknown captured layer.")
    data = array(item, buffer)
    return geometry_page(snapshot, item, buffer, data, start, end)


def geometry_page(
    snapshot: str, item: Layer, buffer: str, data: Any, start: int, end: int
) -> dict[str, Any]:
    return dict(
        snapshot=snapshot,
        layer=item.identity,
        buffer=buffer,
        offset=start,
        total=len(data),
        next_offset=end if end < len(data) else None,
        values=data[start:end].tolist(),
        frame=item.frame,
        **buffer_description(data),
    )
