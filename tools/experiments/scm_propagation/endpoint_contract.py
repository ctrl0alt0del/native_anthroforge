"""Current application conversion commands prepare experimental routing inputs."""

from dataclasses import replace
from types import SimpleNamespace as NS

from fixture import TISSUE

from anthroforge.application import curve_evaluation
from anthroforge.application.projects import adopt
from anthroforge.core.entities import IDENTITY


def context(session, source, steps):
    adopt(session, manual(source.document), source.resources.snapshot())
    surface = session.document.object(session.document.object(TISSUE).source)
    convert_curves(session, surface, steps)
    surface = session.document.object(surface.id)
    return NS(
        engine=session.engine,
        document=session.document,
        resources=session.resources.snapshot(),
        assets=session.assets,
        surface=surface,
    )


def convert_curves(session, surface, steps):
    for use in surface.curves:
        session.command("update_mode", entity=use.curve, mode="MANUAL")
        session.command(
            "curve.engine",
            curve=use.curve,
            engine="ROUTED",
            settings=dict(samples=73, accepted_steps=steps),
        )


def manual(document):
    return replace(
        document,
        update_mode="MANUAL",
        entities=tuple(replace(e, update_mode="MANUAL") for e in document.entities),
        objects=tuple(replace(o, update_mode="MANUAL") for o in document.objects),
    )


def prepared(context, key, expected):
    item = context.document.object(key)
    assert len(item.points) == 2 and item.bindings == expected.bindings
    assert item.matrix == IDENTITY
    value = curve_evaluation.resolve(context.engine, context.document, context.resources, item, 0)
    assert value.authored.bindings == expected.bindings
    return value.authored
