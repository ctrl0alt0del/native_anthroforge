"""Engine-owned bounded LRU storage of immutable native resources."""

from collections import OrderedDict
from threading import RLock, local
from time import perf_counter
from typing import Any

from .resource_footprint import Allocations, footprint


class ResourceCache[T]:
    def __init__(self, budget: int, capacity: int, name: str) -> None:
        self.budget, self.capacity, self.name = budget, capacity, name
        self.items: OrderedDict[tuple[Any, ...], tuple[T, int]] = OrderedDict()
        self.lock = RLock()
        self.observer: Any = None
        self.epoch = 0
        self.pool: Any = None
        self.allocations, self.local = Allocations(), local()
        self.receipts: dict[Any, tuple[dict[Any, int], float, float]] = {}

    @property
    def bytes(self) -> int:
        return self.allocations.bytes

    def get(self, key: tuple[Any, ...]) -> T | None:
        with self.lock:
            item = self.items.get(key)
            self.observe("hit" if item is not None else "miss", key)
            if item is not None:
                self.items.move_to_end(key)
                self.touch(key)
                return item[0]
            self.local.pending = (hash(key), perf_counter(), self.epoch)
        return None

    def store(self, key: tuple[Any, ...], mesh: T, size: int) -> T:
        with self.lock:
            if key in self.items:
                self.observe("reuse", key)
                return self.items[key][0]
            self.admit(key, mesh, size)
        return mesh

    def admit(self, key: tuple[Any, ...], mesh: T, size: int) -> None:
        receipt = footprint(mesh, size)
        size = sum(receipt.values())
        if size > min(self.budget, self.pool.budget if self.pool else self.budget):
            self.observe("bypass", key, size, "entry_exceeds_budget")
            return
        self.items[key] = (mesh, size)
        self.account(key, receipt, self.cost(key))
        self.observe("insert", key, size)
        self.trim()

    def cost(self, key: tuple[Any, ...]) -> float:
        identity, started, epoch = getattr(self.local, "pending", (None, 0, -1))
        self.local.pending = None, 0, -1
        return (
            max(1e-6, perf_counter() - started)
            if identity == hash(key) and epoch == self.epoch
            else 1e-6
        )

    def account(self, key: Any, receipt: dict[Any, int], cost: float) -> None:
        self.allocations.add(receipt)
        if self.pool:
            self.pool.allocations.add(receipt)
        self.receipts[key] = receipt, cost, 0.0
        self.touch(key)

    def touch(self, key: Any) -> None:
        receipt, cost, _ = self.receipts[key]
        age = self.pool.age if self.pool else 0.0
        self.receipts[key] = receipt, cost, age + cost / max(1, sum(receipt.values()))

    def trim(self) -> None:
        while self.bytes > self.budget or len(self.items) > self.capacity:
            reason = "byte_budget" if self.bytes > self.budget else "entry_capacity"
            self.remove(next(iter(self.items)), reason)
        if self.pool:
            self.pool.trim()

    def detach(self, key: Any) -> tuple[T, int]:
        receipt, _, _ = self.receipts.pop(key)
        self.allocations.remove(receipt)
        if self.pool:
            self.pool.allocations.remove(receipt)
        return self.items.pop(key)

    def remove(self, key: Any, reason: str) -> None:
        _, size = self.detach(key)
        self.observe("evict", key, size, reason)

    def clear(self) -> None:
        with self.lock:
            size = self.bytes
            for key in tuple(self.items):
                self.detach(key)
            self.epoch += 1
            self.observe("clear", (), size, "lifecycle")

    def take(self, key: tuple[Any, ...]) -> tuple[T | None, int]:
        with self.lock:
            item = self.detach(key) if key in self.items else None
            self.observe("lease" if item else "miss", key)
            self.local.pending = (hash(key), perf_counter(), self.epoch)
            return item[0] if item else None, self.epoch

    def restore(self, key: tuple[Any, ...], value: T, size: int, epoch: int) -> None:
        with self.lock:
            if epoch == self.epoch and key not in self.items:
                self.admit(key, value, size)

    def reweigh(self, key: tuple[Any, ...], value: T, size: int) -> None:
        with self.lock:
            if key not in self.items or self.items[key][0] is not value:
                return
            cost = self.receipts[key][1]
            self.detach(key)
            receipt = footprint(value, size)
            self.items[key] = (value, sum(receipt.values()))
            self.account(key, receipt, cost)
            self.trim()

    def observe(self, action: str, key: tuple[Any, ...], size: int = 0, reason: str = "") -> None:
        if self.observer is not None:
            self.observer(
                action,
                cache=self.name,
                key=hex(hash(key)),
                bytes=size,
                reason=reason,
                retained_bytes=self.bytes,
                entries=len(self.items),
                budget=self.budget,
                aggregate_bytes=self.pool.allocations.bytes if self.pool else self.bytes,
            )

    def retained(self) -> tuple[T, ...]:
        with self.lock:
            return tuple(mesh for mesh, _ in self.items.values())
