"""Observe retained snapshot catalogues once per inventory, without owning them.

Dispatch captures own their catalogues already. Remember weak group references instead
of expanding every shared mesh at every prepare/execute boundary.
"""

from weakref import ref

from .resource_inventory import bounded_unique, owned_resources


class ResourceGroups:
    def __init__(self, profiler):
        self.profiler, self.jobs = profiler, {}

    def clear(self):
        self.jobs.clear()

    def release(self, job):
        self.jobs.pop(job, None)

    def remember(self, job, value):
        if job not in self.jobs and len(self.jobs) >= 256:
            self.profiler.losses["resource_job_limit"] += 1
            return
        group = self.jobs.setdefault(job, {})
        if id(value) not in group and sum(map(len, self.jobs.values())) >= 4096:
            self.profiler.losses["resource_group_limit"] += 1
            return
        group[id(value)] = ref(value)

    def collect(self, output):
        groups = {key: value for group in self.jobs.values() for key, value in group.items()}
        resources = (
            resource
            for reference in groups.values()
            if (catalogue := reference()) is not None
            for resource in owned_resources(catalogue)
        )
        output.update(bounded_unique(resources, 4096, self.profiler))
