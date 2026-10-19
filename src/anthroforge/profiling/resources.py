"""Recording-only observation of weak resource references and owner-thread snapshots."""

from collections import defaultdict
from threading import RLock, local
from time import perf_counter_ns
from weakref import WeakKeyDictionary, WeakSet

from .resource_inventory import inventory, payload_resources, session_owners


class Resources:
    def __init__(self, profiler):
        self.profiler, self.sessions = profiler, WeakSet()
        self.views, self.jobs = WeakKeyDictionary(), {}
        self.local, self.last, self.cost_ns = local(), 0, 0
        self.lock = RLock()
        self.reference_cost_ns = 0
        self.observing = False

    def start(self):
        self.reset(True)
        self.last, self.cost_ns = 0, 0
        self.reference_cost_ns = 0
        for engine in self.profiler.native.engines:
            self.attach(engine)
        self.sample(force=True)

    def attach(self, engine):
        engine.resource_observer = self.created
        for cache in engine.caches():
            cache.observer = self.cache

    def stop(self):
        self.sample(force=True)
        for engine in self.profiler.native.engines:
            engine.resource_observer = None
            for cache in engine.caches():
                cache.observer = None
        self.reset(False)

    def reset(self, observing):
        with self.lock:
            self.observing = observing
            self.jobs.clear()

    def created(self, mesh):
        job = getattr(self.local, "job", "")
        if job and self.profiler.active:
            start = perf_counter_ns()
            try:
                self.remember(job, (mesh,))
            finally:
                self.reference_cost_ns += perf_counter_ns() - start

    def remember(self, job, meshes):
        with self.lock:
            if self.observing:
                self.retain(job, meshes)

    def retain(self, job, meshes):
        if job not in self.jobs and len(self.jobs) >= 256:
            self.profiler.losses["resource_job_limit"] += 1
            return
        owned = self.jobs.setdefault(job, WeakSet())
        count = sum(len(value) for value in self.jobs.values())
        for mesh in meshes:
            if count >= 4096:
                self.profiler.losses["resource_reference_limit"] += 1
                break
            owned.add(mesh)
            count += 1

    def release(self, job):
        with self.lock:
            self.jobs.pop(job, None)

    def call(self, job, stage, function):
        previous, self.local.job = getattr(self.local, "job", ""), job.id
        try:
            result = function()
            if self.profiler.active and stage in ("prepare", "execute"):
                self.profiler.call(
                    "profiler", "resource_references", self.observe_payload, job.id, result
                )
            return result
        finally:
            self.local.job = previous

    def observe_payload(self, job, value):
        self.remember(job, payload_resources(value, self.profiler))

    def cache(self, action, cache="body_base", **metadata):
        self.profiler.event(
            "cache", action, cache=cache, job=getattr(self.local, "job", ""), **metadata
        )

    def owners(self):
        result = defaultdict(set)
        for session in self.sessions:
            session_owners(session, result, self.profiler)
        with self.lock:
            result["jobs"].update(mesh for values in self.jobs.values() for mesh in values)
        for reference in self.views.values():
            view = reference()
            if view is not None:
                view(result)
        for engine in self.profiler.native.engines:
            for cache in engine.caches():
                retain_cache(result["cache"], cache)
        return result

    def sample(self, force=False):
        if not self.profiler.active or not self.profiler.native.engines:
            return
        start = perf_counter_ns()
        if not force and start - self.last < 1_000_000_000:
            return
        self.last = start
        try:
            self.profiler.call("profiler", "geometry_inventory", self.collect)
        except Exception:
            self.profiler.losses["geometry_inventory_failure"] += 1
        finally:
            self.cost_ns += perf_counter_ns() - start

    def collect(self):
        evidence = inventory(self.profiler, self.owners())
        self.profiler.event("memory", "geometry_snapshot", **evidence)
        self.profiler.counter(
            "memory",
            "geometry_bytes",
            unique=evidence["unique_bytes"],
            **{k: v["bytes"] for k, v in evidence["owners"].items()},
        )

    def costs(self):
        return dict(
            inventory_inclusive_ns=self.cost_ns, resource_observation_ns=self.reference_cost_ns
        )


def retain_cache(owner, cache):
    values = cache.retained()
    owner.update(values)
    for value in values:
        owner.update(getattr(value, "resources", ()))
