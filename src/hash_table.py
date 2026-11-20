"""A string-keyed hash table using separate chaining."""

import math
from collections.abc import Iterator


class _Node:
    __slots__ = ("key", "value", "next")

    def __init__(self, key: str, value: object, next_node: "_Node | None" = None) -> None:
        self.key = key
        self.value = value
        self.next = next_node


class HashTable:
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

        self._buckets: list[_Node | None] = [None] * initial_capacity
        self._size = 0
        self._max_load_factor = max_load_factor
        self._comparisons = 0
        self._last_comparisons = 0

    @property
    def capacity(self) -> int:
        return len(self._buckets)

    @property
    def load_factor(self) -> float:
        return self._size / self.capacity

    @property
    def comparisons(self) -> int:
        return self._comparisons

    @property
    def last_comparisons(self) -> int:
        return self._last_comparisons

    def reset_comparisons(self) -> None:
        self._comparisons = 0
        self._last_comparisons = 0

    def hash_calculation(self, key: str) -> tuple[int, tuple[tuple[str, int, int, int], ...]]:
        self._validate_key(key)
        value = 0
        steps = []
        for character in key:
            previous = value
            codepoint = ord(character)
            value = (31 * value + codepoint) % self.capacity
            steps.append((character, codepoint, previous, value))
        return value, tuple(steps)

    def hash_index(self, key: str) -> int:
        return self.hash_calculation(key)[0]

    def bucket_entries(self, index: int) -> tuple[tuple[str, object], ...]:
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError("bucket index must be an integer")
        if index < 0 or index >= self.capacity:
            raise IndexError("bucket index out of range")
        entries = []
        node = self._buckets[index]
        while node is not None:
            entries.append((node.key, node.value))
            node = node.next
        return tuple(entries)

    def put(self, key: str, value: object) -> None:
        index = self.hash_index(key)
        node = self._buckets[index]
        comparisons = 0
        while node is not None:
            comparisons += 1
            if node.key == key:
                node.value = value
                self._record_comparisons(comparisons)
                return
            node = node.next

        self._buckets[index] = _Node(key, value, self._buckets[index])
        self._size += 1
        self._record_comparisons(comparisons)
        if self._max_load_factor is not None and self.load_factor > self._max_load_factor:
            self._resize(self.capacity * 2)

    def get(self, key: str, default: object = None) -> object:
        node = self._find(key)
        return default if node is None else node.value

    def contains(self, key: str) -> bool:
        return self._find(key) is not None

    def delete(self, key: str) -> bool:
        index = self.hash_index(key)
        node = self._buckets[index]
        previous = None
        comparisons = 0
        while node is not None:
            comparisons += 1
            if node.key == key:
                if previous is None:
                    self._buckets[index] = node.next
                else:
                    previous.next = node.next
                self._size -= 1
                self._record_comparisons(comparisons)
                return True
            previous, node = node, node.next
        self._record_comparisons(comparisons)
        return False

    def items(self) -> Iterator[tuple[str, object]]:
        for bucket in self._buckets:
            node = bucket
            while node is not None:
                yield node.key, node.value
                node = node.next

    def __len__(self) -> int:
        return self._size

    def _find(self, key: str) -> _Node | None:
        index = self.hash_index(key)
        node = self._buckets[index]
        comparisons = 0
        while node is not None:
            comparisons += 1
            if node.key == key:
                self._record_comparisons(comparisons)
                return node
            node = node.next
        self._record_comparisons(comparisons)
        return None

    def _record_comparisons(self, comparisons: int) -> None:
        self._last_comparisons = comparisons
        self._comparisons += comparisons

    def _resize(self, new_capacity: int) -> None:
        old_buckets = self._buckets
        self._buckets = [None] * new_capacity
        for bucket in old_buckets:
            node = bucket
            while node is not None:
                next_node = node.next
                index = self.hash_index(node.key)
                node.next = self._buckets[index]
                self._buckets[index] = node
                node = next_node

    @staticmethod
    def _validate_key(key: str) -> None:
        if not isinstance(key, str):
            raise TypeError("key must be a string")
