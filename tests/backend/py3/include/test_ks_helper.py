import unittest
from src.backend.py3.include.ks_helper import KsHelper


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

    def test_bytes_to_uint(self):
        inst = KsHelper()
        expected_val = 65535
        byte_val = b"\xff\xff"
        endian = "little"
        self.assertEqual(expected_val, inst.bytes_to_uint(byte_val, endian))

    def test_bytes_to_int(self):
        inst = KsHelper()
        expected_val = -1
        byte_val = b"\xff\xff"
        endian = "big"
        self.assertEqual(expected_val, inst.bytes_to_int(byte_val, endian))

    def test_replace_bytes_smaller(self):
        inst = KsHelper()
        b_old = b"asdf"
        b_new = b"poi"
        expected_b = b"poif"
        self.assertEqual(inst.replace_bytes(b_new, b_old, 0), expected_b)

    def test_replace_bytes_equal(self):
        inst = KsHelper()
        b_old = b"asdf"
        b_new = b"qwer"
        expected_b = b"qwer"
        self.assertEqual(inst.replace_bytes(b_new, b_old, 0), expected_b)

    def test_replace_bytes_larger(self):
        inst = KsHelper()
        b_old = b"asdf"
        b_new = b"poila"
        expected_b = b"poila"
        self.assertEqual(inst.replace_bytes(b_new, b_old, 0), expected_b)

    def test_replace_bytes_half_replacement(self):
        inst = KsHelper()
        b_old = b"asdf"
        b_new = b"2345"
        expected_b = b"as2345"
        replace_start_pos = 2
        self.assertEqual(inst.replace_bytes(b_new, b_old, replace_start_pos), expected_b)

    def test_replace_bytes_end(self):
        inst = KsHelper()
        b_old = b"asdf"
        b_new = b"2345"
        expected_b = b"asdf2345"
        replace_start_pos = 4
        self.assertEqual(inst.replace_bytes(b_new, b_old, replace_start_pos), expected_b)

    def test_inplace_replace_bytes_smaller(self):
        inst = KsHelper()
        b_old = bytearray(b"asdf")
        b_new = bytearray(b"poi")
        expected_str = "poif"
        output = inst.inplace_replace_bytes(b_new, b_old, 0)
        expected_b_len = 4
        self.assertEqual(len(output), expected_b_len)
        self.assertIs(b_old, output)
        self.assertEqual(output.decode(), expected_str)

    def test_inplace_replace_bytes_equal(self):
        inst = KsHelper()
        b_old = bytearray(b"asdf")
        b_new = bytearray(b"qwer")
        expected_str = "qwer"
        expected_b_len = 4
        output = inst.inplace_replace_bytes(b_new, b_old, 0)
        self.assertEqual(len(output), expected_b_len)
        self.assertIs(b_old, output)
        self.assertEqual(output.decode(), expected_str)

    def test_inplace_replace_bytes_larger(self):
        inst = KsHelper()
        b_old = bytearray(b"asdf")
        b_new = bytearray(b"poila")
        expected_str = "poila"
        expected_b_len = 5
        output = inst.inplace_replace_bytes(b_new, b_old, 0)
        self.assertEqual(len(output), expected_b_len)
        self.assertIs(b_old, output)
        self.assertEqual(output.decode(), expected_str)

    def test_inplace_replace_bytes_half_replacement(self):
        inst = KsHelper()
        b_old = bytearray(b"asdf")
        b_new = bytearray(b"2345")
        expected_str = "as2345"
        replace_start_pos = 2
        expected_b_len = 6
        output = inst.inplace_replace_bytes(b_new, b_old, replace_start_pos)
        self.assertEqual(len(output), expected_b_len)
        self.assertIs(b_old, output)
        self.assertEqual(output.decode(), expected_str)

    def test_inplace_replace_bytes_end(self):
        inst = KsHelper()
        b_old = bytearray(b"asdf")
        b_new = bytearray(b"2345")
        expected_str = "asdf2345"
        replace_start_pos = 4
        expected_b_len = 8
        output = inst.inplace_replace_bytes(b_new, b_old, replace_start_pos)
        self.assertEqual(len(output), expected_b_len)
        self.assertIs(b_old, output)
        self.assertEqual(output.decode(), expected_str)
