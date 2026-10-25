"""Identical existing consumer stages, using isolated resource dictionaries."""

from fixture import TISSUE

from anthroforge.application import surface_evaluation, tissue_evaluation
from anthroforge.application.assets import Asset


def install(resources, key, mesh):
    resources.meshes[key] = Asset(mesh, "experimental SCM comparison", "", 1.0, False)


def pipeline(context, surface, paths):
    resources = context.resources.snapshot()
    doc = context.document
    engine = context.engine
    for use, path in zip(surface.curves, paths, strict=True):
        item = doc.object(use.curve)
        resources.paths[item.result.asset] = path
    mesh = surface_evaluation.evaluate(engine, doc, resources, surface, 0)
    install(resources, surface.result.asset, mesh)
    return tissue(context, resources, mesh)


def tissue(context, resources, surface):
    doc = context.document
    item = doc.object(TISSUE)
    engine = context.engine
    outputs = dict(surface=surface)
    for stage in ("base", "rest", "intrinsic", "final"):
        result = tissue_evaluation.evaluate(engine, doc, resources, TISSUE, stage, 0)
        mesh = result.mesh or resources.meshes[result.asset].mesh
        install(resources, getattr(item, stage + "_result").asset, mesh)
        outputs[stage] = mesh
    return outputs
