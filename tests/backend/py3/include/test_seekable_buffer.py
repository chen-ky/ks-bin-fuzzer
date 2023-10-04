import unittest
from backend.py3.include import SeekableBuffer

# IntelliSense
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), "src"))  # Include src dir to sys.path


class TestSeekableBuffer(unittest.TestCase):
    def test_init_custom_data(self):
        custom_data = bytearray(b"uewrhew\n\0")
        buf = SeekableBuffer(custom_data)
        self.assertEqual(custom_data, buf.get_data())
        self.assertEqual(len(custom_data), len(buf))

    def test_init_sub_buffer_start_pos(self):
        custom_data = bytearray(b"uewrhew\n\0")
        start_pos = 1
        buf = SeekableBuffer(custom_data, start_pos=start_pos)
        self.assertEqual(custom_data[start_pos:], buf.get_data())
        self.assertEqual(len(custom_data) - start_pos, len(buf))

    def test_init_sub_buffer_start_pos_too_large(self):
        custom_data = bytearray(b"uewrhew\n\0")
        start_pos = len(custom_data)
        self.assertRaises(ValueError, SeekableBuffer, custom_data, start_pos=start_pos)

    def test_init_sub_buffer_end_pos(self):
        custom_data = bytearray(b"uewrhew\n\0")
        end_pos = len(custom_data) - 1
        expected_data = custom_data[:end_pos]
        expected_len = len(expected_data)
        buf = SeekableBuffer(custom_data, end_pos=end_pos)
        self.assertEqual(expected_data, buf.get_data())
        self.assertEqual(expected_len, len(buf))

    def test_init_sub_buffer_start_end_pos(self):
        custom_data = bytearray(b"uewrhew\n\0")
        start_pos = 1
        end_pos = len(custom_data) - 1
        expected_data = custom_data[start_pos:end_pos]
        expected_len = len(expected_data)
        buf = SeekableBuffer(custom_data, start_pos=start_pos, end_pos=end_pos)
        self.assertEqual(expected_data, buf.get_data())
        self.assertEqual(expected_len, len(buf))

    def test_init_sub_buffer_end_pos_smaller_than_start_pos(self):
        custom_data = bytearray(b"uewrhew\n\0")
        start_pos = 2
        end_pos = start_pos - 1
        self.assertRaises(ValueError, SeekableBuffer, custom_data, start_pos=start_pos, end_pos=end_pos)

    def test_init_sub_buffer_end_pos_equal_start_pos(self):
        custom_data = bytearray(b"uewrhew\n\0")
        start_pos = 2
        end_pos = start_pos
        expected_data = b""
        expected_len = 0
        buf = SeekableBuffer(custom_data, start_pos=start_pos, end_pos=end_pos)
        self.assertEqual(expected_data, buf.get_data())
        self.assertEqual(expected_len, len(buf))
        self.assertTrue(buf.is_eos())

    def test_empty(self):
        expected_len = 0
        buf = SeekableBuffer()
        self.assertEqual(expected_len, len(buf))

    def test_append_data(self):
        data = b"asdfsd\0"
        expected_len = len(data)
        buf = SeekableBuffer()
        buf.append(data)
        self.assertEqual(expected_len, len(buf))
        self.assertEqual(data, buf.get_full_data())

    def test_append_multiple_data(self):
        data = [b"asdfsd\0", bytearray("234nioer", encoding="utf-8")]
        expected_len = sum([len(d) for d in data])
        expected_data = bytes()
        buf = SeekableBuffer()
        for d in data:
            expected_data += d
            buf.append(d)
        self.assertEqual(expected_len, len(buf))
        self.assertEqual(expected_data, buf.get_full_data())

    def test_append_empty_data(self):
        data = b""
        expected_len = 0
        buf = SeekableBuffer()
        buf.append(data)
        self.assertEqual(expected_len, len(buf))
        self.assertEqual(data, buf.get_full_data())

    def test_get_data(self):
        data = b"asdfsd\0"
        buf = SeekableBuffer()
        buf.append(data)
        self.assertEqual(data[:4], buf.get_data(4))
        self.assertEqual(data[4:], buf.get_data())
        self.assertEqual(b"", buf.get_data())

    def test_get_data_too_large_n_bytes(self):
        data = b"asdfsd\0"
        buf = SeekableBuffer()
        buf.append(data)
        self.assertEqual(data, buf.get_data(len(data) + 1))
        self.assertEqual(b"", buf.get_data())
        self.assertTrue(buf.is_eos())

    def test_seek_negative_offset(self):
        data = b"asdfsd\0"
        buf = SeekableBuffer()
        buf.append(data)
        self.assertEqual(data, buf.get_data())
        self.assertRaises(ValueError, buf.seek, -1)

    def test_seek_to_start(self):
        data = b"asdfsd\0"
        buf = SeekableBuffer()
        buf.append(data)
        self.assertEqual(data, buf.get_data())
        buf.seek(0)
        self.assertEqual(data, buf.get_data())

    def test_seek_to_end(self):
        data = b"asdfsd\0"
        buf = SeekableBuffer()
        buf.append(data)
        buf.seek(len(data))
        self.assertTrue(buf.is_eos())
        self.assertEqual(b"", buf.get_data())

    def test_seek_exceed_end(self):
        data = b"asdfsd\0"
        buf = SeekableBuffer()
        buf.append(data)
        buf.seek(len(buf) + 1)
        self.assertTrue(buf.is_eos())
        self.assertEqual(b"", buf.get_data())

    def test_move_data_left(self):
        data = b"0123456789\n"
        expected_data = b"123456789\n\0"
        ptr_pos = 1
        offset = -1
        buf = SeekableBuffer()
        buf.append(data)
        buf.seek(ptr_pos)
        buf._move_data(offset)
        self.assertEqual(ptr_pos, buf.ptr)
        buf.seek(0)
        self.assertEqual(expected_data, buf.get_data())

    def test_move_data_right(self):
        data = b"0123456789\n"
        expected_data = b"0\0\0\0\0\0" + b"12345"
        ptr_pos = 1
        offset = 5
        buf = SeekableBuffer()
        buf.append(data)
        buf.seek(ptr_pos)
        buf._move_data(offset)
        self.assertEqual(ptr_pos, buf.ptr)
        buf.seek(0)
        self.assertEqual(expected_data, buf.get_data())

    def test_move_data_left_no_null(self):
        data = b"0123456789\n"
        expected_data = b"23456789\n9\n"
        ptr_pos = 2
        offset = -2
        buf = SeekableBuffer()
        buf.append(data)
        buf.seek(ptr_pos)
        buf._move_data(offset, write_null_bytes=False)
        self.assertEqual(ptr_pos, buf.ptr)
        buf.seek(0)
        self.assertEqual(expected_data, buf.get_data())

    def test_move_data_right_no_null(self):
        data = b"0123456789\n"
        expected_data = b"01234512345"
        ptr_pos = 1
        offset = 5
        buf = SeekableBuffer()
        buf.append(data)
        buf.seek(ptr_pos)
        buf._move_data(offset, write_null_bytes=False)
        self.assertEqual(ptr_pos, buf.ptr)
        buf.seek(0)
        self.assertEqual(expected_data, buf.get_data())

    def test_move_data_zero_offset(self):
        data = b"0123456789\n"
        expected_data = b"0123456789\n"
        ptr_pos = 1
        offset = 0
        buf = SeekableBuffer()
        buf.append(data)
        buf.seek(ptr_pos)
        buf._move_data(offset)
        self.assertEqual(ptr_pos, buf.ptr)
        buf.seek(0)
        self.assertEqual(expected_data, buf.get_data())
