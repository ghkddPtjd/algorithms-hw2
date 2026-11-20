import unittest

from src.hash_table import HashTable


class HashTableTests(unittest.TestCase):
    def test_empty_table_operations(self):
        table = HashTable()
        self.assertEqual(len(table), 0)
        self.assertEqual(table.get("missing", "fallback"), "fallback")
        self.assertFalse(table.contains("missing"))
        self.assertFalse(table.delete("missing"))

    def test_collisions_updates_and_deletes(self):
        table = HashTable(initial_capacity=4, max_load_factor=None)
        buckets = {}
        for number in range(100):
            key = f"key-{number}"
            bucket = table.hash_index(key)
            if bucket in buckets:
                first = buckets[bucket]
                break
            buckets[bucket] = key
        else:
            self.fail("expected two keys to collide")

        table.put(first, 1)
        table.put(key, 2)
        table.put(first, 3)
        self.assertEqual(len(table), 2)
        self.assertEqual(table.get(first), 3)
        self.assertEqual(table.get(key), 2)
        self.assertTrue(table.delete(first))
        self.assertFalse(table.contains(first))
        self.assertEqual(table.get(key), 2)

    def test_last_bucket_and_comparison_counts(self):
        table = HashTable(initial_capacity=5, max_load_factor=None)
        keys = [f"last-{number}" for number in range(100)]
        keys = [key for key in keys if table.hash_index(key) == 4]
        self.assertGreaterEqual(len(keys), 2)
        table.put(keys[0], "first")
        table.put(keys[1], "second")

        self.assertEqual(table.get(keys[0]), "first")
        self.assertEqual(table.last_comparisons, 2)
        self.assertIsNone(table.get("absent"))
        self.assertEqual(table.last_comparisons, 0)

    def test_resize_preserves_entries(self):
        table = HashTable(initial_capacity=2)
        table.put("one", 1)
        table.put("two", 2)
        self.assertGreater(table.capacity, 2)
        self.assertEqual(table.get("one"), 1)
        self.assertEqual(table.get("two"), 2)

    def test_disabled_resize_supports_high_load(self):
        table = HashTable(initial_capacity=2, max_load_factor=None)
        for number in range(8):
            table.put(f"key-{number}", number)
        self.assertEqual(len(table), 8)
        self.assertEqual(table.capacity, 2)

    def test_items_and_invalid_keys(self):
        table = HashTable()
        table.put("a", 1)
        table.put("b", 2)
        self.assertEqual(set(table.items()), {("a", 1), ("b", 2)})
        for method in (table.get, table.contains, table.delete):
            with self.subTest(method=method.__name__), self.assertRaises(TypeError):
                method(1)
        with self.assertRaises(ValueError):
            HashTable(initial_capacity=0)


if __name__ == "__main__":
    unittest.main()
