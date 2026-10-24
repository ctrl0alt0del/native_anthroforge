"""Historical image tiles reuse normal presentation and per-layer resource ownership."""

from dataclasses import asdict

from anthroforge.application.object_frames import Frames
from anthroforge.application.workspace_policy import included
from anthroforge.core.image_presentation import settings
from anthroforge.core.presentation import visible
from anthroforge.core.reference_images import ReferenceImage


def rows(baseline, workspace):
    context = baseline.source
    frames, records, leases = Frames(context.engine, context.document), [], []
    for item in context.document.objects:
        if not isinstance(item, ReferenceImage) or item.id in workspace.hidden:
            continue
        asset = context.resources.images[item.source]
        row = metadata(context, item, frames, workspace)
        records.extend(
            dict(row, handle=asset.handle, chunk=i, key=f"{item.id}:{item.source}:{i}")
            for i in range(asset.chunks)
        )
        leases.append(asset)
    return records, leases


def metadata(context, item, frames, workspace):
    style = asdict(settings(workspace, item.id))
    return dict(
        id=item.id,
        matrix=frames.world(item.id),
        image_style=style,
        visible=visible(workspace, "images"),
        readonly=not included(context.document, workspace, item.id),
        content=dict(dimensions=[item.width, item.height], layer=style["depth"]),
    )
