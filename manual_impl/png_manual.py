import sys
from random import Random
from typing import Any, Optional, Literal
import zlib


UTF8_CODEPOINT_MIN_RANGE = 0
# https://en.wikipedia.org/wiki/UTF-8#Encoding
UTF8_CODEPOINT_MAX_RANGE = 0x10FFFF
# https://unicodebook.readthedocs.io/unicode_encodings.html#utf-16-surrogate-pairs
UTF8_CODEPOINT_SURROGATE_MIN_RANGE = 0xD800
UTF8_CODEPOINT_SURROGATE_MAX_RANGE = 0xDFFF
# https://unicodebook.readthedocs.io/unicode.html#bmp
UTF8_CODEPOINT_BMP_MAX_RANGE = 0xFFFF
UTF8_CODEPOINT_ONE_BYTE_MAX_RANGE = 0x007F
UTF8_CODEPOINT_TWO_BYTE_MAX_RANGE = 0x07FF
UTF8_CODEPOINT_THREE_BYTE_MAX_RANGE = 0xFFFF
UTF8_CODEPOINT_FOUR_BYTE_MAX_RANGE = UTF8_CODEPOINT_MAX_RANGE
ENABLE_UTF8_SURROGATE = False  # Must be False since Python cannot encode surrogate


class KsHelper:
    def __init__(self, seed: Any = None) -> None:
        self.rng = Random(seed)

    @staticmethod
    def _utf8_byte_size(codepoint: int) -> int:
        if codepoint < UTF8_CODEPOINT_MIN_RANGE or codepoint > UTF8_CODEPOINT_MAX_RANGE:
            raise ValueError("UTF-8 codepoint out of range")
        if codepoint <= UTF8_CODEPOINT_ONE_BYTE_MAX_RANGE:
            return 1
        elif codepoint <= UTF8_CODEPOINT_TWO_BYTE_MAX_RANGE:
            return 2
        elif codepoint <= UTF8_CODEPOINT_THREE_BYTE_MAX_RANGE:
            return 3
        elif codepoint <= UTF8_CODEPOINT_FOUR_BYTE_MAX_RANGE:
            return 4
        raise ValueError("UTF-8 codepoint out of range")

    def rand_bytes(self, n_bytes: int) -> bytes:
        result = bytes()
        C_INT_MAX = 65536
        remaining_bytes = n_bytes
        # Workaround for n_bytes that is larger than C int
        while remaining_bytes > 0:
            result += self.rng.randbytes(C_INT_MAX if remaining_bytes > C_INT_MAX else remaining_bytes)
            remaining_bytes -= C_INT_MAX
        return result

    def rand_utf8(self, n_bytes: int, terminator: Optional[str] = None) -> bytes:
        if n_bytes <= 0:
            raise ValueError("Number of bytes must be at least 1.")
        ret = ""
        bytes_remaining = n_bytes
        if terminator is not None:
            bytes_remaining -= len(terminator.encode(encoding="utf-8"))
            if bytes_remaining < 0:
                raise ValueError("Terminator cannot fit into specified number of bytes.")
        while bytes_remaining > 0:
            if bytes_remaining == 1:
                code_point = self.rng.randint(
                    UTF8_CODEPOINT_MIN_RANGE, UTF8_CODEPOINT_ONE_BYTE_MAX_RANGE)
            elif bytes_remaining == 2:
                code_point = self.rng.randint(
                    UTF8_CODEPOINT_MIN_RANGE, UTF8_CODEPOINT_TWO_BYTE_MAX_RANGE)
            elif bytes_remaining == 3:
                code_point = self.rng.randint(
                    UTF8_CODEPOINT_MIN_RANGE, UTF8_CODEPOINT_THREE_BYTE_MAX_RANGE)
            else:
                code_point = self.rng.randint(
                    UTF8_CODEPOINT_MIN_RANGE, UTF8_CODEPOINT_MAX_RANGE)

            if (not ENABLE_UTF8_SURROGATE
                    and code_point >= UTF8_CODEPOINT_SURROGATE_MIN_RANGE
                    and code_point <= UTF8_CODEPOINT_SURROGATE_MAX_RANGE):
                continue

            ret += chr(code_point)
            bytes_remaining -= KsHelper._utf8_byte_size(code_point)
        if terminator is not None:
            ret += terminator
        return ret.encode(encoding="utf-8")

    def rand_ascii(self, n_bytes: int, terminator: Optional[str] = None) -> bytes:
        encoding = "ascii"
        if n_bytes <= 0:
            raise ValueError("Number of bytes must be at least 1.")
        ret = b""
        bytes_remaining = n_bytes
        if terminator is not None:
            bytes_remaining -= len(terminator.encode(encoding=encoding))
            if bytes_remaining < 0:
                raise ValueError("Terminator cannot fit into specified number of bytes.")
        b_length = 1
        while bytes_remaining > 0:
            code_point = self.rng.randint(0, 127)
            ret += int.to_bytes(code_point, length=b_length)
            bytes_remaining -= b_length
        if terminator is not None:
            ret += terminator.encode(encoding=encoding)
        return ret

    def rand_iso8859(self, n_bytes: int, encoding: Literal["iso8859-1", "iso8859-2", "iso8859-3", "iso8859-4", "iso8859-5", "iso8859-6", "iso8859-7", "iso8859-8", "iso8859-9", "iso8859-10", "iso8859-11", "iso8859-13", "iso8859-14", "iso8859-15", "iso8859-16"], terminator: Optional[str] = None):
        if n_bytes <= 0:
            raise ValueError("Number of bytes must be at least 1.")
        if not encoding.lower().startswith("iso8859"):
            raise ValueError("Invalid ISO 8859 encoding type.")
        bytes_remaining = n_bytes
        if terminator is not None:
            bytes_remaining -= len(terminator.encode(encoding=encoding))
            if bytes_remaining < 0:
                raise ValueError("Terminator cannot fit into specified number of bytes.")
        ret = self.rand_bytes(bytes_remaining)
        if terminator is not None:
            ret += terminator.encode(encoding=encoding)
        return ret

    def rand_choice(self, seq):
        return self.rng.choice(seq)

    @staticmethod
    def bytes_to_uint(b: bytes, endian: Literal["big", "little"]) -> int:
        return int.from_bytes(b, endian, signed=False)

    @staticmethod
    def bytes_to_int(b: bytes, endian: Literal["big", "little"]) -> int:
        return int.from_bytes(b, endian, signed=True)

    @staticmethod
    def replace_bytes(b_new: bytes, b_original: bytes, start_loc: int) -> bytes:
        """
        Replace the bytes at `start_loc` of `b_original` with `b_new`.

        If `start_loc` is larger than or equal to the length of `b_original`, 
        it will append `b_new` at the end of `b_original`.

        If `b_new` has a length that is longer than the remaining length of
        `b_original` at `start_loc`, it will replace and then extend `b_original`.
        """
        if start_loc < 0:
            raise ValueError("Byte start location cannot be negative.")
        first_half = b_original[:start_loc]
        last_half = b_original[start_loc + len(b_new):]
        return first_half + b_new + last_half

    @staticmethod
    def extract_bytes(b: bytes | bytearray, start_end_pos: tuple[int, int]):
        start_pos, end_pos = start_end_pos
        if start_pos == -1 and end_pos == -1:
            return b[:]
        if start_pos == -1:
            return b[:end_pos]
        if end_pos == -1:
            return b[:start_pos]
        return b[start_pos:end_pos]


# TODO REMOVE ME
gen_order = ["IDAT", "IEND"]
HEIGHT = 256
WIDTH = 256
BITDEPTH = 8
COLORTYPE = 6  # Truecolor alpha
CHANNEL = 4 * int(BITDEPTH / 8)  # RGBA


class Png_:
    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_magic_()
        self.gen_ihdr_len_()
        self.gen_ihdr_type_()
        self.gen_ihdr_()
        self.gen_ihdr_crc_()
        self.gen_chunk_()

        self.execute_instances()
        return bytes(self.result)

    def _get_range(self, b_length: int):
        curr_len = len(self.result)
        return (curr_len, curr_len + b_length)

    def _append_result(self, var_name: str, b: bytes):
        self.var_range[var_name] = self._get_range(len(b))
        self.result += b

    def gen_magic_(self):
        val = b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"
        self._append_result("magic_", val)

    def gen_ihdr_len_(self):
        val = b'\x00\x00\x00\x0d'
        self._append_result("ihdr_len_", val)

    def gen_ihdr_type_(self):
        val = b"IHDR"
        self._append_result("ihdr_type_", val)

    def gen_ihdr_(self):
        custom_type = IhdrChunk_(self.result)
        initial_len = len(self.result)
        custom_type.generate()
        self.var_range["ihdr_"] = (initial_len, len(self.result))

    def gen_ihdr_crc_(self):
        checksum_data = (self.ks_helper.extract_bytes(self.result, self.var_range["ihdr_type_"])
                         + self.ks_helper.extract_bytes(self.result, self.var_range["ihdr_"]))
        crc32 = zlib.crc32(checksum_data)
        val = int.to_bytes(crc32, length=4, byteorder="big")
        self._append_result("ihdr_crc_", val)

    def gen_chunk_(self):
        while len(gen_order) > 0:
            custom_type = Chunk_(self.result)
            initial_len = len(self.result)
            # TODO repeat until IEND or EOF
            custom_type.generate()
            self.var_range["chunk_"] = (initial_len, len(self.result))

    def execute_instances(self):
        pass


class IhdrChunk_():

    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_width_()
        self.gen_height_()
        self.gen_bit_depth_()
        self.gen_color_type_()
        self.gen_compression_method_()
        self.gen_filter_method_()
        self.gen_interlace_method_()

        self.execute_instances()
        return bytes(self.result)

    def _get_range(self, b_length: int):
        curr_len = len(self.result)
        return (curr_len, curr_len + b_length)

    def _append_result(self, var_name: str, b: bytes):
        self.var_range[var_name] = self._get_range(len(b))
        self.result += b

    def gen_width_(self):
        val = self.ks_helper.rand_bytes(4)
        # FIXME
        val = int.to_bytes(WIDTH, 4, "big", signed=False)
        self._append_result("width_", val)

    def gen_height_(self):
        val = self.ks_helper.rand_bytes(4)
        # FIXME
        val = int.to_bytes(HEIGHT, 4, "big", signed=False)
        self._append_result("height_", val)

    def gen_bit_depth_(self):
        val = self.ks_helper.rand_bytes(1)
        # FIXME
        val = int.to_bytes(BITDEPTH, 1, "big", signed=False)
        self._append_result("bit_depth_", val)

    def gen_color_type_(self):
        val = EnumColorType_().generate().to_bytes(1, "big", signed=False)
        # FIXME hardcoded for now
        val = int.to_bytes(COLORTYPE, 1, "big", signed=False)
        self._append_result("color_type_", val)

    def gen_compression_method_(self):
        # FIXME
        val = self.ks_helper.rand_bytes(1)
        val = int.to_bytes(0, 1, "big", signed=False)
        self._append_result("compression_method_", val)

    def gen_filter_method_(self):
        # FIXME
        val = self.ks_helper.rand_bytes(1)
        val = int.to_bytes(0, 1, "big", signed=False)
        self._append_result("filter_method_", val)

    def gen_interlace_method_(self):
        # FIXME
        val = self.ks_helper.rand_bytes(1)
        val = int.to_bytes(0, 1, "big", signed=False)
        self._append_result("interlace_method_", val)

    def execute_instances(self):
        pass


class Chunk_():

    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_len_()
        self.gen_type_()
        self.gen_body_()
        self.gen_crc_()

        self.execute_instances()
        return bytes(self.result)

    def _get_range(self, b_length: int):
        curr_len = len(self.result)
        return (curr_len, curr_len + b_length)

    def _append_result(self, var_name: str, b: bytes):
        self.var_range[var_name] = self._get_range(len(b))
        self.result += b

    def gen_len_(self):
        # val = self.ks_helper.rand_bytes(4)
        # self._append_result("len_", val)
        # TODO workaround in gen_type, need to know type to know appropriate size
        pass

    def gen_type_(self):
        # val = self.ks_helper.rand_utf8(4)
        type_str = gen_order.pop(0)
        val = type_str.encode("utf-8")
        len_val = b""
        if type_str == "pHYs":
            len_val = int.to_bytes(9, 4, "big", signed=False)
        elif type_str == "IDAT":
            # FIXME limit to 2 byte for now for smaller number
            # len_val = self.ks_helper.rand_bytes(2)
            # len_val = b'\x00\x00' + len_val
            len_val = int.to_bytes(((WIDTH*HEIGHT)*CHANNEL), 4, "big", signed=False)

        elif type_str == "IEND":
            len_val = int.to_bytes(0, 4, "big", signed=False)
        # TODO Randomly pick a type while respecting order in png spec
        self._append_result("len_", len_val)
        self._append_result("type_", val)

    def gen_body_(self):
        # TODO TLV, create a substream because size is specified
        type_b_range = self.var_range["type_"]
        type_str = self.result[type_b_range[0]:type_b_range[1]].decode("utf-8")
        initial_len = len(self.result)
        if type_str == "pHYs":
            PhysChunk_(self.result).generate()
        elif type_str == "IDAT":
            len_range = self.var_range["len_"]
            gen_len = int.from_bytes(self.result[len_range[0]:len_range[1]], "big", signed=False)
            scanline_len = int(gen_len / HEIGHT)  # without filter byte
            val = b""
            for _i in range(0, HEIGHT):
                val += b"\x00"  # No filter
                val += self.ks_helper.rand_bytes(scanline_len)
            val = zlib.compress(val)
            self.result += val
            # Update len
            self.result[len_range[0]:len_range[1]] = len(val).to_bytes(4, "big", signed=False)
        elif type_str == "IEND":
            pass  # No body
        self.var_range["body_"] = (initial_len, len(self.result))

    def gen_crc_(self):
        checksum_data = (self.ks_helper.extract_bytes(self.result, self.var_range["type_"])
                         + self.ks_helper.extract_bytes(self.result, self.var_range["body_"]))
        crc32 = zlib.crc32(checksum_data)
        val = int.to_bytes(crc32, length=4, byteorder="big")
        self._append_result("crc_", val)

    def execute_instances(self):
        pass


class Plte_Chunk_():

    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_entries_()

        self.execute_instances()
        return bytes(self.result)

    def gen_entries_(self):
        custom_type = Rgb_(self.result)
        initial_len = len(self.result)
        # TODO repeat until EOS
        custom_type.generate()
        self.var_range["rgb_"] = (initial_len, len(self.result))

    def execute_instances(self):
        pass


class Rgb_():

    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_r_()
        self.gen_g_()
        self.gen_b_()

        self.execute_instances()
        return bytes(self.result)

    def gen_r_(self):
        val = self.ks_helper.rand_bytes(1)
        self._append_result("r_", val)

    def gen_g_(self):
        val = self.ks_helper.rand_bytes(1)
        self._append_result("g_", val)

    def gen_b_(self):
        val = self.ks_helper.rand_bytes(1)
        self._append_result("b_", val)

    def execute_instances(self):
        pass


class Chrm_Chunk_():

    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_white_point_()
        self.gen_red_()
        self.gen_green_()
        self.gen_blue_()

        self.execute_instances()
        return bytes(self.result)

    def gen_white_point_(self):
        custom_type = Point_(self.result)
        initial_len = len(self.result)
        custom_type.generate()
        self.var_range["white_point_"] = (initial_len, len(self.result))

    def gen_red_(self):
        custom_type = Point_(self.result)
        initial_len = len(self.result)
        custom_type.generate()
        self.var_range["red_"] = (initial_len, len(self.result))

    def gen_green_(self):
        custom_type = Point_(self.result)
        initial_len = len(self.result)
        custom_type.generate()
        self.var_range["green_"] = (initial_len, len(self.result))

    def gen_blue_(self):
        custom_type = Point_(self.result)
        initial_len = len(self.result)
        custom_type.generate()
        self.var_range["blue_"] = (initial_len, len(self.result))

    def execute_instances(self):
        pass


class Point_():

    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_x_int_()
        self.gen_y_int_()

        self.execute_instances()
        return bytes(self.result)

    def gen_x_int_(self):
        val = self.ks_helper.rand_bytes(4)
        self._append_result("x_int_", val)

    def gen_y_int_(self):
        val = self.ks_helper.rand_bytes(4)
        self._append_result("y_int_", val)

    def execute_instances(self):
        # TODO something about dividing 100000.0?
        pass


class GamaChunk_():

    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_gamma_int_()

        self.execute_instances()
        return bytes(self.result)

    def gen_gamma_int_(self):
        val = self.ks_helper.rand_bytes(4)
        self._append_result("gamma_int_", val)

    def execute_instances(self):
        # TODO something about dividing 100000.0?
        pass


class SrgbChunk_():

    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_render_intent_()

        self.execute_instances()
        return bytes(self.result)

    def gen_render_intent_(self):
        # TODO enum
        pass

    def execute_instances(self):
        # TODO something about dividing 100000.0?
        pass


class BkgdChunk_():
    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_bkgd_()

        self.execute_instances()
        return bytes(self.result)

    def gen_bkgd_(self):
        # TODO switch case
        pass

    def execute_instances(self):
        pass


class BkgdGreyscale_():
    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_value_()

        self.execute_instances()
        return bytes(self.result)

    def gen_value_(self):
        val = self.ks_helper.rand_bytes(2)
        self._append_result("value_", val)

    def execute_instances(self):
        pass


class BkgdTruecolor_():
    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_red_()
        self.gen_green_()
        self.gen_blue_()

        self.execute_instances()
        return bytes(self.result)
    
    def gen_red_(self):
        val = self.ks_helper.rand_bytes(2)
        self._append_result("red_", val)

    def gen_green_(self):
        val = self.ks_helper.rand_bytes(2)
        self._append_result("green_", val)

    def gen_blue_(self):
        val = self.ks_helper.rand_bytes(2)
        self._append_result("blue_", val)

    def execute_instances(self):
        pass


class BkgdIndexed_():
    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_palette_index_()

        self.execute_instances()
        return bytes(self.result)

    def gen_palette_index_(self):
        val = self.ks_helper.rand_bytes(1)
        self._append_result("palette_index_", val)

    def execute_instances(self):
        pass


class PhysChunk_():
    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_pixels_per_unit_x_()
        self.gen_pixels_per_unit_y_()
        self.gen_unit_()

        self.execute_instances()
        return bytes(self.result)

    def _get_range(self, b_length: int):
        curr_len = len(self.result)
        return (curr_len, curr_len + b_length)

    def _append_result(self, var_name: str, b: bytes):
        self.var_range[var_name] = self._get_range(len(b))
        self.result += b

    def gen_pixels_per_unit_x_(self):
        val = self.ks_helper.rand_bytes(4)
        self._append_result("pixels_per_unit_x_", val)

    def gen_pixels_per_unit_y_(self):
        val = self.ks_helper.rand_bytes(4)
        self._append_result("pixels_per_unit_y_", val)

    def gen_unit_(self):
        val = EnumPhysUnit_().generate().to_bytes(1, "big", signed=False)
        self._append_result("unit", val)

    def execute_instances(self):
        pass


class TimeChunk_():
    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_year_()
        self.gen_month_()
        self.gen_day_()
        self.gen_hour_()
        self.gen_minute_()
        self.gen_second_()

        self.execute_instances()
        return bytes(self.result)

    def gen_year_(self):
        val = self.ks_helper.rand_bytes(2)
        self._append_result("year_", val)

    def gen_month_(self):
        val = self.ks_helper.rand_bytes(1)
        self._append_result("month_", val)

    def gen_day_(self):
        val = self.ks_helper.rand_bytes(1)
        self._append_result("day_", val)

    def gen_hour_(self):
        val = self.ks_helper.rand_bytes(1)
        self._append_result("hour_", val)

    def gen_minute_(self):
        val = self.ks_helper.rand_bytes(1)
        self._append_result("minute_", val)

    def gen_second_(self):
        val = self.ks_helper.rand_bytes(1)
        self._append_result("second_", val)

    def execute_instances(self):
        pass


class InternationalTextChunk_():
    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_keyword_()
        self.gen_compression_flag_()
        self.gen_compression_method_()
        self.gen_language_tag_()
        self.gen_translated_keyword_()
        self.gen_text_()

        self.execute_instances()
        return bytes(self.result)

    def gen_keyword_(self):
        # TODO no bytes specified
        val = self.ks_helper.rand_utf8(4, terminator="\0")
        self._append_result("keyword_", val)

    def gen_compression_flag_(self):
        val = self.ks_helper.rand_bytes(1)
        self._append_result("compression_flag_", val)

    def gen_compression_method_(self):
        # val = self.ks_helper.rand_bytes(1)
        # TODO enum
        # self._append_result("unit", val)
        pass

    def gen_language_tag_(self):
        # TODO no bytes specified
        val = self.ks_helper.rand_ascii(4, terminator="\0")
        self._append_result("language_tag_", val)

    def gen_translated_keyword_(self):
        # TODO no bytes specified
        val = self.ks_helper.rand_utf8(4, terminator="\0")
        self._append_result("translated_keyword_", val)

    def gen_text_(self):
        # TODO no bytes specified
        val = self.ks_helper.rand_utf8(4)
        self._append_result("text_", val)

    def execute_instances(self):
        pass


class TextChunk_():
    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_keyword_()
        self.gen_text_()

        self.execute_instances()
        return bytes(self.result)

    def gen_keyword_(self):
        # TODO no bytes specified, iso8859-1 encoding
        val = self.ks_helper.rand_iso8859(4, "iso8859-1", terminator="\0")
        self._append_result("keyword_", val)

    def gen_text_(self):
        # TODO no bytes specified
        val = self.ks_helper.rand_iso8859(4, "iso8859-1")
        self._append_result("text_", val)

    def execute_instances(self):
        pass


class CompressedTextChunk_():
    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_keyword_()
        self.gen_compression_method_()
        self.gen_text_datastream_()

        self.execute_instances()
        return bytes(self.result)

    def gen_keyword_(self):
        # TODO no bytes specified, iso8859-1 encoding
        val = self.ks_helper.rand_iso8859(4, "iso8859-1", terminator="\0")
        self._append_result("keyword_", val)

    def gen_compression_methods_(self):
        val = self.ks_helper.rand_bytes(1)
        self._append_result("compression_methods_", val)

    def gen_text_datastream_(self):
        # TODO no bytes specified, use zlib
        val = self.ks_helper.rand_bytes(4)
        self._append_result("text_datastream_", val)

    def execute_instances(self):
        pass


class AnimationControlChunk_():
    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_num_frames_()
        self.gen_num_plays_()

        self.execute_instances()
        return bytes(self.result)

    def gen_num_frames_(self):
        val = self.ks_helper.rand_bytes(4)
        self._append_result("num_frames_", val)

    def gen_num_plays_(self):
        val = self.ks_helper.rand_bytes(4)
        self._append_result("num_plays_", val)

    def execute_instances(self):
        pass


# TODO
class FrameControlChunk_():
    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_sequence_number_()
        self.gen_width_()
        self.gen_height_()
        self.gen_x_offset_()
        self.gen_y_offset_()
        self.gen_delay_num_()
        self.gen_delay_den_()
        self.gen_dispose_op_()
        self.gen_blend_op_()


        self.execute_instances()
        return bytes(self.result)

    def gen_keyword_(self):
        # TODO no bytes specified, iso8859-1 encoding
        val = self.ks_helper.rand_iso8859(4, "iso8859-1", terminator="\0")
        self._append_result("keyword_", val)

    def gen_text_(self):
        # TODO no bytes specified
        val = self.ks_helper.rand_iso8859(4, "iso8859-1")
        self._append_result("text_", val)

    def execute_instances(self):
        #TODO stuff in here
        pass


class FrameDataChunk_():
    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.var_range = dict()
        self.result = result

    def generate(self):
        self.gen_sequence_number_()
        self.gen_frame_data_()

        self.execute_instances()
        return bytes(self.result)

    def gen_sequence_number_(self):
        val = self.ks_helper.rand_bytes(4)
        self._append_result("sequence_number_", val)

    def gen_frame_data_(self):
        # TODO till eof
        val = self.ks_helper.rand_bytes(4)
        self._append_result("frame_data_", val)

    def execute_instances(self):
        pass


class EnumColorType_():
    def __init__(self):
        self.ks_helper = KsHelper()
        self.choices = [0, 2, 3, 4, 6]

    def generate(self) -> int:
        return self.ks_helper.rand_choice(self.choices)


class EnumPhysUnit_():
    def __init__(self):
        self.ks_helper = KsHelper()
        self.choices = [0, 1]

    def generate(self) -> int:
        return self.ks_helper.rand_choice(self.choices)


class EnumCompressionMethods_():
    def __init__(self):
        self.ks_helper = KsHelper()
        self.choices = [0]

    def generate(self) -> int:
        return self.ks_helper.rand_choice(self.choices)


class EnumDisposeOpValues_():
    def __init__(self):
        self.ks_helper = KsHelper()
        self.choices = [0, 1, 2]

    def generate(self) -> int:
        return self.ks_helper.rand_choice(self.choices)


class EnumBlendOpValues_():
    def __init__(self):
        self.ks_helper = KsHelper()
        self.choices = [0, 1]

    def generate(self) -> int:
        return self.ks_helper.rand_choice(self.choices)


if "__main__" == __name__:
    entry_point = Png_(bytearray())
    sys.stdout.buffer.write(entry_point.generate())
    sys.stdout.flush()
