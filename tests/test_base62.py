import unittest

from src.base62 import decode, encode


class Base62Tests(unittest.TestCase):
    def test_zero_round_trip(self):
        self.assertEqual(encode(0), "0")
        self.assertEqual(decode("0"), 0)

    def test_alphabet_boundaries(self):
        for number, code in ((9, "9"), (10, "a"), (35, "z"), (36, "A"), (61, "Z"), (62, "10")):
            with self.subTest(number=number):
                self.assertEqual(encode(number), code)
                self.assertEqual(decode(code), number)

    def test_large_integer_round_trip(self):
        number = 2**256
        self.assertEqual(decode(encode(number)), number)

    def test_invalid_inputs(self):
        for code in ("", "!", "a-"):
            with self.subTest(code=code), self.assertRaises(ValueError):
                decode(code)
        for number in (-1,):
            with self.subTest(number=number), self.assertRaises(ValueError):
                encode(number)
        with self.assertRaises(TypeError):
            encode(True)
        with self.assertRaises(TypeError):
            decode(1)


if __name__ == "__main__":
    unittest.main()
