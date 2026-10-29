"""Shared staged mesh/path view records; no anatomical ownership or mutation."""

from anthroforge.native import scene


def placement(session, frame):
    return dict(
        matrix=list(frame),
        trs=session.engine.decompose(frame),
        quaternion=scene.quaternion(session.engine, frame),
        geometry_offset=[0, 0, 0],
        visible=True,
        surface_pickable=True,
        surface_visible=True,
        readonly=True,
    )


def chunks(metadata, resource):
    count = resource.counts[4] if metadata["kind"] == "MESH" else resource.chunks if resource else 1
    handle = resource.handle if resource else 0
    return [
        dict(
            metadata,
            handle=handle,
            key=f"{metadata['id']}:{metadata['stage']}:{handle}:{i}",
            chunk=i,
            mesh_handle=handle if metadata["kind"] == "MESH" else 0,
            content=content(metadata, handle if metadata["kind"] == "MESH" else 0),
        )
        for i in range(count)
    ]


def content(row, mesh_handle):
    keys = ("stage", "kind", "matrix", "trs", "quaternion", "color")
    return dict({key: row[key] for key in keys}, mesh_handle=mesh_handle)
