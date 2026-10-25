"""Causal ablation: measure retained Ribs response without changing any binding."""

import numpy as np
from fairing_run import write
from fairing_trial import Fairing
from fixture import fixture
from regional_trial import Trial

from anthroforge.native.mesh import GeometryEngine


def frozen_ribs(data):
    points = data.current.copy()
    offset = 0
    for reference, count in zip(data.targets, data.counts, strict=True):
        if reference.target == "SCP_2":
            points[offset:offset + count] = data.before[offset:offset + count]
        offset += count
    return points


def response(data, trial):
    full = trial.evaluate(data.current, data.goals)[:data.samples]
    frozen = trial.evaluate(frozen_ribs(data), data.goals)[:data.samples]
    movement = np.linalg.norm(full - frozen, axis=1)
    return dict(peak_response=float(movement.max()), mean_response=float(movement.mean()))


def run():
    f = fixture(GeometryEngine())
    output = {d.item.id: {"c2": response(d, Trial(d)), "fair20": response(d, Fairing(d, 0.2))}
              for d in f.curves}
    write("ribs-response", output)
    print(output, flush=True)


if __name__ == "__main__":
    run()
