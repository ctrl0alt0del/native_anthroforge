"""Include dynamic parent-vertex packing in the experimental update measurement."""

from contextlib import closing

import numpy as np
from fixture import fixture, parent_mesh
from regional_trial import Trial
from run import improved, methods
from timing import measure, sample, summarize

from anthroforge.application.session import Session
from anthroforge.native.mesh import doubles


def packed(f, trials):
    for data in f.curves:
        data.current = doubles(
            np.concatenate([parent_mesh(f.after, ref)[0] for ref in data.targets])
        )
    return [improved(f.after, d, t) for d, t in zip(f.curves, trials, strict=True)]


def run():
    with closing(Session()) as session:
        assert not session.profiler.active
        f = fixture(session.engine)
        trials = [Trial(d) for d in f.curves]
        functions = methods(f, trials, session.preferences.value.routing_backend)
        functions["improved"] = lambda: packed(f, trials)
        for function in functions.values():
            sample(f, function)
        summarize(measure(f, functions, 6, "packed"), "packed")


if __name__ == "__main__":
    run()
