from random import Random
from typing import Any, Optional, Literal
import sys

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
    def inplace_replace_bytes(b_new: bytes | bytearray, b_original: bytearray, start_loc: int) -> bytes:
        if len(b_new) <= 0:
            return b_original
        if start_loc > len(b_original):
            start_loc = len(b_original)

        for i, b in enumerate(b_new):
            if start_loc < len(b_original):
                b_original[start_loc] = b
            else:
                # Insert all at once and exit loop
                b_original += b_new[i:]
                break
            start_loc += 1
        return b_original


class Ico_:
    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.values = dict()
        self.result = result

    def generate(self):
        self.result += self.gen_magic_()
        self.result += self.gen_num_images_()
        self.gen_images_()
        return bytes(self.result)

    def gen_magic_(self):
        self.values["magic_"] = b'\x00\x00\x01\x00'
        return self.values["magic_"]

    def gen_num_images_(self):
        # self.values["num_images_"] = self.ks_helper.rand_bytes(2)
        # Hard coded to 1 for now, so there are no multiple images
        self.values["num_images_"] = int.to_bytes(1, 2, "little", signed=False)
        return self.values["num_images_"]

    def gen_images_(self):
        self.values["images_"] = bytes()
        custom_type = IconDirEntry_(self.result)
        for _i in range(self.ks_helper.bytes_to_uint(self.values["num_images_"], "little")):
            self.values["images_"] += custom_type.generate()
        return self.values["images_"]


class IconDirEntry_:
    def __init__(self, result: bytearray):
        self.ks_helper = KsHelper()
        self.values = dict()
        self.result = result

    def generate(self):
        self.result += (self.gen_width_() +
                        self.gen_height_() +
                        self.gen_num_colors_() +
                        self.gen_reserved_() +
                        self.gen_num_planes() +
                        self.gen_bpp_() +
                        self.gen_len_img_() +
                        self.gen_ofs_img_()
                        )
        self.execute_instances()
        return bytes(self.result)

    def gen_width_(self):
        self.values["width_"] = self.ks_helper.rand_bytes(1)
        return self.values["width_"]

    def gen_height_(self):
        self.values["height_"] = self.ks_helper.rand_bytes(1)
        return self.values["height_"]

    def gen_num_colors_(self):
        # ICO files that I have seen have a value of 0 here
        self.values["num_colors_"] = self.ks_helper.rand_bytes(1)
        return self.values["num_colors_"]

    def gen_reserved_(self):
        self.values["reserved_"] = b'\x00'
        return self.values["reserved_"]

    def gen_num_planes(self):
        # ICO files that I have seen have a value of 1 here
        self.values["num_planes_"] = self.ks_helper.rand_bytes(2)
        return self.values["num_planes_"]

    def gen_bpp_(self):
        # ICO files that I have seen have a value of 32 here
        self.values["bpp_"] = self.ks_helper.rand_bytes(2)
        return self.values["bpp_"]

    def gen_len_img_(self):
        # self.values["len_img_"] = self.ks_helper.rand_bytes(4)
        # Hard coded a relatively small arbitrary value, so it doesn't generate a large file
        self.values["len_img_"] = int.to_bytes(200000, 4, "little", signed=False)
        return self.values["len_img_"]

    def gen_ofs_img_(self):
        # self.values["ofs_img_"] = self.ks_helper.rand_bytes(4)
        # Hard coded to 22. There are no information in the ksy file to generate
        # this value. This is the image offset from the start of the file.
        self.values["ofs_img_"] = int.to_bytes(22, 4, "little", signed=False)
        return self.values["ofs_img_"]

    def execute_instances(self):
        # Offset is absolute here (from root), not relative.
        # https://doc.kaitai.io/user_guide.html#stream
        # https://doc.kaitai.io/user_guide.html#_specifying_size_creates_a_substream
        # Because `images` does not contain the `size` key, a substream is not created
        # thus the absolute positioning
        img_ = self.gen_img_()
        self.ks_helper.inplace_replace_bytes(img_, self.result, self.ks_helper.bytes_to_uint(self.values["ofs_img_"], "little"))
        png_header_ = self.gen_png_header_()
        self.ks_helper.inplace_replace_bytes(png_header_, self.result, self.ks_helper.bytes_to_uint(self.values["ofs_img_"], "little"))

    def gen_img_(self):
        # TODO Need to be png or bmp, but the ico.ksy file does not have the
        # details about their generation.
        self.values["img_"] = self.ks_helper.rand_bytes(self.ks_helper.bytes_to_uint(self.values["len_img_"], "little"))
        return self.values["img_"]

    def gen_png_header_(self):
        # self.values["png_header_"] = self.ks_helper.rand_bytes(8)
        # Hard coded to generate png magic. ICO can either contain PNG or
        # DIB bitmap (BMP). No information in ksy file to generate either format.
        self.values["png_header_"] = bytes([137, 80, 78, 71, 13, 10, 26, 10])
        return self.values["png_header_"]


if "__main__" == __name__:
    entry_point = Ico_(bytearray())
    sys.stdout.buffer.write(entry_point.generate())
    sys.stdout.flush()
