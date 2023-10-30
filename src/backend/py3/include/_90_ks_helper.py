from random import Random
import struct
from typing import Any, Optional, Literal, Sequence, TypeVar


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

T = TypeVar('T')


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

    def rand_bytes(self, n_bytes: int, min_n_bytes: int = 0, max_n_bytes: Optional[int] = None) -> bytes:
        """Generate `n_bytes` if it is a valid value, otherwise, generate based on `min_n_bytes` and `max_n_bytes`."""
        if n_bytes < 0 and max_n_bytes is not None:
            if max_n_bytes < 0:
                raise ValueError("`max_n_bytes` cannot be less than 0.")
            if min_n_bytes < 0:
                raise ValueError("`min_n_bytes` cannot be less than 0.")
            n_bytes = self.rng.randint(min_n_bytes, max_n_bytes)
        if n_bytes < 0:
            raise ValueError("Number of bytes cannot be less than 0.")
        result = bytes()
        C_INT_MAX = 65536
        remaining_bytes = n_bytes
        # Workaround for n_bytes that is larger than C int
        while remaining_bytes > 0:
            result += self.rng.randbytes(C_INT_MAX if remaining_bytes
                                         > C_INT_MAX else remaining_bytes)
            remaining_bytes -= C_INT_MAX
        return result

    def rand_utf8(self, n_bytes: int, terminator: Optional[bytes] = None, min_n_bytes: int = 0, max_n_bytes: Optional[int] = None) -> str:
        if n_bytes < 0 and max_n_bytes is not None:
            if max_n_bytes < 0:
                raise ValueError("`max_n_bytes` cannot be less than 0.")
            if min_n_bytes < 0:
                raise ValueError("`min_n_bytes` cannot be less than 0.")
            n_bytes = self.rng.randint(min_n_bytes, max_n_bytes)
        if n_bytes < 0:
            raise ValueError("Number of bytes cannot be less than 0.")
        bytes_remaining = n_bytes
        if terminator is not None:
            bytes_remaining -= 1
            if bytes_remaining < 0:
                raise ValueError("Terminator cannot fit into the specified size.")
        ret = ""
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
            ret += terminator.decode(encoding="utf-8")
        return ret

    def rand_ascii(self, n_bytes: int, terminator: Optional[bytes] = None, min_n_bytes: int = 0, max_n_bytes: Optional[int] = None) -> str:
        encoding = "ascii"
        if n_bytes < 0 and max_n_bytes is not None:
            if max_n_bytes < 0:
                raise ValueError("`max_n_bytes` cannot be less than 0.")
            if min_n_bytes < 0:
                raise ValueError("`min_n_bytes` cannot be less than 0.")
            n_bytes = self.rng.randint(min_n_bytes, max_n_bytes)
        if n_bytes < 0:
            raise ValueError("Number of bytes cannot be less than 0.")
        bytes_remaining = n_bytes
        if terminator is not None:
            bytes_remaining -= 1
            if bytes_remaining < 0:
                raise ValueError("Terminator cannot fit into the specified size.")
        ret = b""
        b_length = 1
        while bytes_remaining > 0:
            code_point = self.rng.randint(0, 127)
            ret += int.to_bytes(code_point, length=b_length)
            bytes_remaining -= b_length
        if terminator is not None:
            ret += terminator
        return ret.decode(encoding=encoding)

    def rand_iso8859(self, n_bytes: int, encoding: Literal["ISO8859-1", "ISO8859-2", "ISO8859-3", "ISO8859-4", "ISO8859-5", "ISO8859-6", "ISO8859-7", "ISO8859-8", "ISO8859-9", "ISO8859-10", "ISO8859-11", "ISO8859-13", "ISO8859-14", "ISO8859-15", "ISO8859-16"], terminator: Optional[bytes] = None, min_n_bytes: int = 0, max_n_bytes: Optional[int] = None) -> str:
        if n_bytes <= 0:
            raise ValueError("Number of bytes must be at least 1.")
        if not encoding.lower().startswith("iso8859"):
            raise ValueError("Invalid ISO 8859 encoding type.")
        if n_bytes < 0 and max_n_bytes is not None:
            if max_n_bytes < 0:
                raise ValueError("`max_n_bytes` cannot be less than 0.")
            if min_n_bytes < 0:
                raise ValueError("`min_n_bytes` cannot be less than 0.")
            n_bytes = self.rng.randint(min_n_bytes, max_n_bytes)
        if n_bytes < 0:
            raise ValueError("Number of bytes cannot be less than 0.")
        bytes_remaining = n_bytes
        if terminator is not None:
            bytes_remaining -= 1
            if bytes_remaining < 0:
                raise ValueError("Terminator cannot fit into the specified size.")
        ret = self.rand_bytes(bytes_remaining)
        if terminator is not None:
            ret += terminator
        return ret.decode(encoding=encoding)

    def rand_int(self, start: int = -32767, end: int = 32767) -> int:
        return self.rng.randint(start, end)

    def rand_float(self) -> float:
        return struct.unpack("=f", self.rand_bytes(4))[0]

    def rand_double(self) -> float:
        return struct.unpack("=d", self.rand_bytes(8))[0]

    def rand_choice(self, seq: Sequence[T]) -> T:
        return self.rng.choice(seq)
