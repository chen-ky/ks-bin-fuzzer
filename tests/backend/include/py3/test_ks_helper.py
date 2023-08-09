import unittest
from src.backend.include.py3.ks_helper import KsHelper


class TestKsHelper(unittest.TestCase):
    def test_small_rand_bytes(self):
        inst = KsHelper()
        expected_length = 50
        output = inst.rand_bytes(expected_length)
        self.assertEqual(len(output), expected_length)

    def test_zero_rand_bytes(self):
        inst = KsHelper()
        expected_length = 0
        self.assertRaises(ValueError, inst.rand_bytes, expected_length)

    def test_large_rand_bytes(self):
        inst = KsHelper()
        expected_length = 2**20
        output = inst.rand_bytes(expected_length)
        self.assertEqual(len(output), expected_length)

    def test_negative_rand_bytes(self):
        inst = KsHelper()
        self.assertRaises(ValueError, inst.rand_bytes, -1)

    def test_small_rand_utf8(self):
        inst = KsHelper()
        expected_length = 50
        output = inst.rand_utf8(expected_length)
        self.assertEqual(len(output), expected_length)
        self.assertIsNotNone(output.decode())

    def test_small_rand_utf8_with_terminator(self):
        inst = KsHelper()
        expected_length = 50
        expected_terminator = "\n"
        output = inst.rand_utf8(expected_length, expected_terminator)
        self.assertEqual(len(output), expected_length)
        self.assertTrue(output.decode().endswith(expected_terminator))

    def test_small_rand_utf8_with_long_terminator(self):
        inst = KsHelper()
        expected_length = 50
        expected_terminator = "\r\n\t\t"
        output = inst.rand_utf8(expected_length, expected_terminator)
        self.assertEqual(len(output), expected_length)
        self.assertTrue(output.decode().endswith(expected_terminator))

    def test_zero_rand_utf8(self):
        inst = KsHelper()
        expected_length = 0
        self.assertRaises(ValueError, inst.rand_utf8, expected_length)

    def test_zero_rand_utf8_with_terminator(self):
        inst = KsHelper()
        expected_length = 0
        terminator = "\t"
        self.assertRaises(ValueError, inst.rand_utf8, expected_length, terminator)

    def test_rand_utf8_with_terminator_exceeding_size(self):
        inst = KsHelper()
        expected_length = 2
        terminator = "\r\n\t"
        self.assertRaises(ValueError, inst.rand_utf8, expected_length, terminator)

    def test_large_rand_utf8(self):
        inst = KsHelper()
        expected_length = 2**20
        output = inst.rand_utf8(expected_length)
        self.assertEqual(len(output), expected_length)
        self.assertIsNotNone(output.decode())

    def test_negative_rand_utf8(self):
        inst = KsHelper()
        self.assertRaises(ValueError, inst.rand_utf8, -1)

    def test_negative_rand_utf8_with_terminator(self):
        inst = KsHelper()
        terminator = "a"
        self.assertRaises(ValueError, inst.rand_utf8, -1, terminator)
