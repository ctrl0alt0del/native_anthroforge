"""Compile captured fixed-topology poses with the maintained native fitter and playback."""

from dataclasses import asdict
from time import perf_counter
from typing import Any

from anthroforge.native import skin_fit, skin_fit_playback, topology

from . import skin_assets, skin_fit_capture
from .skin_results import ComputedStage


def evaluate(engine: Any, payload: Any, cancel: Any) -> ComputedStage:
    document, resources, preferences, identity, settings = payload
    started = perf_counter()
    samples, repeat = skin_fit_capture.capture(
        document, resources, preferences, identity, settings, cancel
    )
    solved = compile_samples(engine, samples, settings, cancel.handle)
    info = metadata(document, identity, settings, repeat, perf_counter() - started)
    info.update(shortcut_description(document, identity))
    info["rows"] = solved.pop("report")
    data = skin_assets.create(solved, info)
    names = "vertices", "corners", "offsets", "triangles", "polygons"
    return ComputedStage(topology.restore(engine, [samples[k] for k in names]), data)


def shortcut_description(document: Any, identity: str) -> Any:
    from anthroforge.core.shortcuts import Shortcut

    from . import property_catalog

    item = next(s for s in (*document.shortcuts, *document.driving_shortcuts) if s.id == identity)
    dimension = (
        item.dimension
        if not isinstance(item, Shortcut)
        else property_catalog.resolve(document, item.reference).dimension
    )
    return dict(label=item.label, dimension=dimension)


def metadata(document: Any, identity: str, settings: Any, repeat: float, seconds: float) -> Any:
    return dict(
        kind="fitted_shortcut",
        shortcut=identity,
        settings=asdict(settings),
        source_revision=document.revision,
        reference=document.skin.reference,
        repeatability_error=repeat,
        seconds=seconds,
        playback="LINEAR_TRS_CHANNELS",
    )


def compile_samples(engine: Any, samples: Any, settings: Any, cancel: int) -> Any:
    training = samples["training"].astype(bool)
    inputs = dict(samples, targets=samples["targets"][training])
    weights, matrices, diagnostics = skin_fit.fit(engine, inputs, asdict(settings), cancel)
    prediction = dict(samples, weights=weights, keys=samples["values"][training], matrices=matrices)
    matrices, predicted = skin_fit.predict(engine, prediction, cancel)
    errors = skin_fit.quality(engine, samples, predicted, cancel)
    output = dict(
        vertices=samples["vertices"], weights=weights, keys=samples["values"], matrices=matrices
    )
    output["bases"], output["channels"] = skin_fit_playback.channels(engine, output, cancel)
    output["training"], output["diagnostics"] = samples["training"], diagnostics
    output["report"] = report(samples, errors)
    return output


def report(samples: Any, errors: Any) -> list[dict[str, Any]]:
    names = "rmse", "p95_percent_height", "maximum", "moving_p95_percent_height"
    return [
        dict(
            value=float(value), training=bool(train), **dict(zip(names, row.tolist(), strict=True))
        )
        for value, train, row in zip(samples["values"], samples["training"], errors, strict=True)
    ]
