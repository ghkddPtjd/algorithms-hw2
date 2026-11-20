import unittest

from src.hash_table import HashTable
from src.linear_probing import LinearProbingHashTable


class LinearProbingHashTableTests(unittest.TestCase):
    def test_is_independent_from_chaining_implementation(self):
        self.assertFalse(issubclass(LinearProbingHashTable, HashTable))

    def test_wraparound_delete_and_tombstone_reuse(self):
        table = LinearProbingHashTable(initial_capacity=8, max_load_factor=None)

        self.assertEqual(table.hash_index("g"), 7)
        self.assertEqual(table.hash_index("o"), 7)
        table.put("g", "first")
        table.put("o", "second")

        self.assertEqual(table.lookup_trace("o"), (7, 0))
        self.assertEqual(table.bucket_entries(7), (("g", "first"),))
        self.assertEqual(table.bucket_entries(0), (("o", "second"),))
        self.assertEqual(table.get("o"), "second")
        self.assertEqual(table.last_probes, 2)

        self.assertTrue(table.delete("g"))
        self.assertEqual(table.get("o"), "second")
        table.put("w", "reused tombstone")

        self.assertEqual(len(table), 2)
        self.assertEqual(table.bucket_entries(7), (("w", "reused tombstone"),))
        self.assertEqual(table.get("o"), "second")
        self.assertFalse(table.delete("missing"))

    def test_full_table_fails_insertion_after_one_complete_probe(self):
        table = LinearProbingHashTable(initial_capacity=2, max_load_factor=None)
        table.put("", "first")
        table.put("b", "second")

        with self.assertRaises(OverflowError):
            table.put("d", "third")

        self.assertEqual(len(table), 2)
        self.assertEqual(table.get(""), "first")
        self.assertEqual(table.get("b"), "second")
        self.assertEqual(table.last_probes, 2)

    def test_resize_preserves_entries_and_comparison_counters(self):
        table = LinearProbingHashTable()
        entries = [(f"key-{number}", number) for number in range(7)]

        for key, value in entries:
            table.put(key, value)

        self.assertEqual(table.capacity, 16)
        self.assertEqual(len(table), 7)
        for key, value in entries:
            with self.subTest(key=key):
                self.assertEqual(table.get(key), value)

        self.assertGreater(table.comparisons, 0)
        table.reset_comparisons()
        self.assertEqual(table.comparisons, 0)
        self.assertEqual(table.last_comparisons, 0)


if __name__ == "__main__":
    unittest.main()
