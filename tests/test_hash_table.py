import unittest

from src.hash_table import HashTable


class HashTableTests(unittest.TestCase):
    def test_empty_table_and_missing_key(self):
        table = HashTable()

        self.assertEqual(len(table), 0)
        self.assertEqual(table.get("missing", "fallback"), "fallback")
        self.assertFalse(table.contains("missing"))
        self.assertFalse(table.delete("missing"))

    def test_colliding_keys_update_and_delete_independently(self):
        table = HashTable(initial_capacity=8)

        # "g" and "o" both map to bucket 7 with the specified Horner hash.
        self.assertEqual(table.hash_index("g"), 7)
        self.assertEqual(table.hash_index("o"), 7)
        table.put("g", "first")
        table.put("o", "second")
        table.put("g", "updated")

        self.assertEqual(len(table), 2)
        self.assertEqual(table.get("g"), "updated")
        self.assertEqual(table.get("o"), "second")
        self.assertTrue(table.delete("g"))
        self.assertFalse(table.contains("g"))
        self.assertEqual(table.get("o"), "second")
        self.assertFalse(table.delete("g"))

    def test_key_in_last_bucket_is_retrievable(self):
        table = HashTable(initial_capacity=8)
        table.put("g", "last bucket")

        self.assertEqual(table.get("g"), "last bucket")
        self.assertEqual(table.bucket_entries(7), (("g", "last bucket"),))

    def test_horner_hash_uses_each_character_in_order(self):
        table = HashTable(initial_capacity=8)

        self.assertEqual(table.hash_index("ab"), 1)
        self.assertEqual(table.hash_index("ba"), 7)

    def test_resize_preserves_entries_after_load_factor_exceeds_point_75(self):
        table = HashTable()
        entries = [(f"key-{number}", number) for number in range(7)]

        for key, value in entries[:6]:
            table.put(key, value)
        self.assertEqual(table.capacity, 8)

        table.put(*entries[6])
        self.assertEqual(table.capacity, 16)
        self.assertEqual(len(table), 7)
        for key, value in entries:
            with self.subTest(key=key):
                self.assertEqual(table.get(key), value)

    def test_empty_string_key_uses_zero_hash(self):
        table = HashTable()
        table.put("", "empty key")

        self.assertEqual(table.hash_index(""), 0)
        self.assertEqual(table.get(""), "empty key")


if __name__ == "__main__":
    unittest.main()
