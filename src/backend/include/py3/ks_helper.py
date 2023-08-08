from random import Random
from typing import Any, Optional, Literal


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
