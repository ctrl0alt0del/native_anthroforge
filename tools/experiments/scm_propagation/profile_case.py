"""Record final prototype spans separately from unrecorded timing evidence."""

import json
from contextlib import closing

import numpy as np
from fixture import OUT, fixture
from regional_trial import Trial
from run import methods
from timing import sample

from anthroforge.application import surface_providers
from anthroforge.application.session import Session
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.native import path_collisions
from anthroforge.native.mesh import pointer


def weights(trial):
    data = trial.data
    output = np.empty_like(data.weights)
    trial.lib.trial_weights(trial.handle, pointer(output))
    indices = [i for i, r in enumerate(data.targets) if r.target == "SCP_2"]
    before = data.weights[: data.samples, indices].sum(1)
    after = output[: data.samples, indices].sum(1)
    return dict(
        ribs_max_before=float(before.max()),
        ribs_max_after=float(after.max()),
        ribs_integral_before=float(np.trapz(before, trial.arc[: data.samples])),
        ribs_integral_after=float(np.trapz(after, trial.arc[: data.samples])),
    )


def baseline_contact(f):
    ref = SurfaceReference("SCP_1")
    handles, frames = surface_providers.inputs(
        f.before.engine, f.before.document, f.before.assets, [ref]
    )
    rows = []
    for data in f.curves:
        item = f.before.document.object(data.item.id)
        owners = spine_owners(item)
        path = f.before.resources.paths[item.result.asset].path
        rows.append(path_collisions.row(path, item.matrix, owners))
    result, _ = path_collisions.check(f.before.engine, rows, handles, frames)
    return result.tolist()


def spine_owners(item):
    return [
        int(any(b.point == p.id and b.target == "SCP_1" for b in item.bindings))
        for p in item.points
    ]


def record(session, f, trials):
    functions = methods(f, trials, session.preferences.value.routing_backend)
    session.command("profile.start")
    for _ in range(3):
        for name in ("current", "improved"):
            session.profiler.call("scm_experiment", name, sample, f, functions[name])
    session.command(
        "profile.stop", path=str((OUT / "prototype-v2.afprofile.zip").resolve()), wait=True
    )


def run():
    with closing(Session()) as session:
        f = fixture(session.engine)
        trials = [Trial(d) for d in f.curves]
        result = dict(
            weights=[weights(t) for t in trials], baseline_spine_contact=baseline_contact(f)
        )
        (OUT / "support-audit.json").write_text(json.dumps(result, indent=2))
        record(session, f, trials)
        print(json.dumps(result), flush=True)


if __name__ == "__main__":
    run()
