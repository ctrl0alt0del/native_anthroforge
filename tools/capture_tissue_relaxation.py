"""Run in background Blender to capture actual addon relaxation and source-goal behavior."""

import hashlib
import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np

SHAPE = dict(
    inflation_amount=0.12,
    minimum_amount=0.006,
    field_power=0.8,
    profile_width=0.08,
    profile_power=0.65,
    profile_segments=9,
    endpoint_taper=0.16,
)
RELAXATION = dict(
    sagginess=0.4,
    gravity=(1.0, 0.0, -1.0),
    sag_limit=0.08,
    shape_retention=0.5,
    volume_retention=0.9,
    surface_slack=0.1,
    iterations=24,
    constraint_passes=2,
    tolerance=1e-7,
)


def settings(kind, mode, regions):
    return NS(
        base_domain=kind,
        relaxation_mode=mode,
        attachments=[NS(**r) for r in regions],
        **SHAPE,
        **RELAXATION,
    )


def region(mask, mode="FIXED", feather=0.0, strength=1.0, offset=0.0):
    return dict(
        mask_attribute=mask, mode=mode, feather=feather, strength=strength, normal_offset=offset
    )


def sample(row, fields, normals):
    if row["kind"] == "PROFILE":
        return NS(points=row["points"], normals=row["normals"], cyclic=False)
    points, faces = row["points"], row["faces"]
    edges = list({tuple(sorted((f[i], f[(i + 1) % len(f)]))) for f in faces for i in range(len(f))})
    weights = fields.boundary_falloff_weights(len(points), edges, faces, points)
    return NS(
        points=points,
        normals=normals.normals(points, faces),
        faces=faces,
        boundary_edges=fields.boundary_edges(edges, faces),
        weights=weights,
        groups={"PATCH": tuple(0.35 if 0.15 < p[0] < 0.35 else 0 for p in points)},
    )


def capture(row, mode, regions):
    build = importlib.import_module("core.visualization.soft_tissue_build")
    goals = importlib.import_module("core.vcp.soft_tissue_source_goals")
    fields = importlib.import_module("core.vcp.soft_tissue_surface_field")
    normals = importlib.import_module("core.vcp.source_surface_normals")
    source = sample(row, fields, normals)
    config = settings("CURVE" if row["kind"] == "PROFILE" else "SURFACE", mode, regions)
    rest = build.build_rest_shape(config, source)
    result = build.relax_shape(config, rest, anchors=goals.source_goals(config, rest, source))
    owned = build.relax_shape(config, rest, anchors=precise_goals(config, rest, source, build))
    return record(row, config, rest, result, owned, source)


def record(row, config, rest, result, owned, source):
    return dict(
        source=row,
        settings=vars(config),
        rest=rest.vertices,
        output=result.vertices,
        owned_output=owned.vertices,
        report=result.report,
        fields=getattr(source, "groups", {}),
    )


def precise_goals(config, rest, source, build):
    if config.base_domain != "SURFACE":
        return importlib.import_module("core.vcp.soft_tissue_source_goals").source_goals(
            config, rest, source
        )
    rows = []
    for constraint in config.attachments:
        for index, mode, influence in build._attachment_influences(rest, constraint):
            normal = np.array(source.normals[index % len(source.points)])
            goal = (
                np.array(rest.vertices[index])
                + normal / np.linalg.norm(normal) * constraint.normal_offset
            )
            rows.append((mode, index, tuple(goal), constraint.strength * influence))
    return tuple(rows)


def serialize(value):
    return vars(value)


def sources(addon):
    names = [
        "visualization/soft_tissue_build.py",
        "vcp/soft_tissue_source_goals.py",
        "vcp/soft_tissue_attachment_feather.py",
        "vcp/soft_tissue_native.py",
        "vcp/soft_tissue_curve_inflation.py",
        "vcp/soft_tissue_static_envelope.py",
    ]
    return {
        "core/" + name: hashlib.sha256((addon / "core" / name).read_bytes()).hexdigest()
        for name in names
    }


def cases(rows):
    for mode in ("GEOMETRIC", "STATIC_PBD"):
        for extra in ([], [region("BOUNDARY")], [region("PATCH", "SOFT", 0.4, 0.55, 0.01)]):
            yield capture(rows[0], mode, [region("BACKING"), *extra])
    yield capture(rows[3], "GEOMETRIC", [region("BACKING"), region("ENDPOINTS")])


def main(addon, fixtures):
    sys.path.insert(0, str(addon))
    rows = json.loads((fixtures / "shapes.json").read_text())["cases"]
    data = dict(sources=sources(addon), cases=list(cases(rows)))
    (fixtures / "relaxation.json").write_text(
        json.dumps(data, default=serialize, allow_nan=False) + "\n"
    )


if __name__ == "__main__":
    main(*(Path(value) for value in sys.argv[sys.argv.index("--") + 1 :]))
