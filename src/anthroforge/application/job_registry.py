"""Coordinator-owned active indexes; completed history never participates in scheduling."""

from collections.abc import Hashable, Iterable

from anthroforge.core.jobs import Job


class JobRegistry:
    def __init__(self) -> None:
        self.history: list[Job] = []
        self.by_id: dict[str, Job] = {}
        self.active: dict[str, Job] = {}
        self.indexes: dict[str, dict[Hashable, set[str]]] = {
            key: {} for key in ("key", "owner", "port", "legacy", "output", "provides")
        }

    def add(self, job: Job) -> None:
        if job.id in self.by_id:
            raise ValueError("A job can only be submitted once.")
        self.by_id[job.id] = job
        self.history.append(job)
        if job.active:
            self.active[job.id] = job
            for index, keys in memberships(job).items():
                for key in keys:
                    self.indexes[index].setdefault(key, set()).add(job.id)
        else:
            job.retire()

    def finish(self, job: Job) -> None:
        self.active.pop(job.id, None)
        for index, keys in memberships(job).items():
            for key in keys:
                ids = self.indexes[index].get(key)
                if ids is not None:
                    ids.discard(job.id)
                    if not ids:
                        del self.indexes[index][key]
        job.retire()

    def matching(self, index: str, keys: Iterable[Hashable]) -> list[Job]:
        lookup = self.indexes[index]
        ids = set().union(*(lookup.get(key, ()) for key in keys))
        return sorted((self.active[key] for key in ids), key=lambda job: job.created)


def memberships(job: Job) -> dict[str, Iterable[Hashable]]:
    ports = job.observes | job.prerequisites | job.provides
    owners = job.outputs | job.reads
    return dict(
        key=(job.key,) if job.key else (),
        owner=owners,
        port=ports,
        legacy=() if ports else owners,
        output=job.outputs,
        provides=job.provides,
    )
