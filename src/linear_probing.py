"""A string-keyed hash table using linear probing and tombstones."""

import math
from collections.abc import Iterator

from src.hash_table import HashTable


_TOMBSTONE = object()


class _Entry:
    __slots__ = ("key", "value")

    def __init__(self, key: str, value: object) -> None:
        self.key = key
        self.value = value


class LinearProbingHashTable(HashTable):
    def __init__(
        self,
        initial_capacity: int = 8,
        max_load_factor: float | None = 0.75,
    ) -> None:
        if not isinstance(initial_capacity, int) or isinstance(initial_capacity, bool):
            raise TypeError("initial_capacity must be an integer")
        if initial_capacity < 1:
            raise ValueError("initial_capacity must be positive")
        if max_load_factor is not None:
            if isinstance(max_load_factor, bool) or not isinstance(max_load_factor, (int, float)):
                raise TypeError("max_load_factor must be a positive number or None")
            if not math.isfinite(max_load_factor) or max_load_factor <= 0:
                raise ValueError("max_load_factor must be a positive finite number or None")

        self._slots: list[_Entry | object | None] = [None] * initial_capacity
        self._size = 0
        self._max_load_factor = max_load_factor
        self._comparisons = 0
        self._last_comparisons = 0

    @property
    def capacity(self) -> int:
        return len(self._slots)

    @property
    def last_probes(self) -> int:
        return self._last_comparisons

    def bucket_entries(self, index: int) -> tuple[tuple[str, object], ...]:
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError("bucket index must be an integer")
        if index < 0 or index >= self.capacity:
            raise IndexError("bucket index out of range")
        entry = self._slots[index]
        if isinstance(entry, _Entry):
            return ((entry.key, entry.value),)
        return ()

    def lookup_trace(self, key: str) -> tuple[int, ...]:
        start = self.hash_index(key)
        inspected = []
        for offset in range(self.capacity):
            index = (start + offset) % self.capacity
            inspected.append(index)
            entry = self._slots[index]
            if entry is None:
                break
            if isinstance(entry, _Entry) and entry.key == key:
                break
        return tuple(inspected)

    def put(self, key: str, value: object) -> None:
        start = self.hash_index(key)
        first_tombstone = None
        probes = 0
        for offset in range(self.capacity):
            index = (start + offset) % self.capacity
            probes += 1
            entry = self._slots[index]
            if entry is None:
                target = first_tombstone if first_tombstone is not None else index
                self._slots[target] = _Entry(key, value)
                self._size += 1
                self._record_comparisons(probes)
                self._resize_if_needed()
                return
            if entry is _TOMBSTONE:
                if first_tombstone is None:
                    first_tombstone = index
                continue
            if entry.key == key:
                entry.value = value
                self._record_comparisons(probes)
                return

        if first_tombstone is not None:
            self._slots[first_tombstone] = _Entry(key, value)
            self._size += 1
            self._record_comparisons(probes)
            self._resize_if_needed()
            return
        self._record_comparisons(probes)
        raise OverflowError("hash table is full")

    def get(self, key: str, default: object = None) -> object:
        index = self._find_index(key)
        if index is None:
            return default
        entry = self._slots[index]
        return entry.value

    def contains(self, key: str) -> bool:
        return self._find_index(key) is not None

    def delete(self, key: str) -> bool:
        index = self._find_index(key)
        if index is None:
            return False
        self._slots[index] = _TOMBSTONE
        self._size -= 1
        return True

    def items(self) -> Iterator[tuple[str, object]]:
        for entry in self._slots:
            if isinstance(entry, _Entry):
                yield entry.key, entry.value

    def _find_index(self, key: str) -> int | None:
        start = self.hash_index(key)
        probes = 0
        for offset in range(self.capacity):
            index = (start + offset) % self.capacity
            probes += 1
            entry = self._slots[index]
            if entry is None:
                self._record_comparisons(probes)
                return None
            if isinstance(entry, _Entry) and entry.key == key:
                self._record_comparisons(probes)
                return index
        self._record_comparisons(probes)
        return None

    def _resize_if_needed(self) -> None:
        if self._max_load_factor is not None and self.load_factor > self._max_load_factor:
            self._resize(self.capacity * 2)

    def _resize(self, new_capacity: int) -> None:
        old_slots = self._slots
        old_comparisons = self._comparisons
        old_last_comparisons = self._last_comparisons
        self._slots = [None] * new_capacity
        self._size = 0
        for entry in old_slots:
            if isinstance(entry, _Entry):
                self.put(entry.key, entry.value)
        self._comparisons = old_comparisons
        self._last_comparisons = old_last_comparisons
