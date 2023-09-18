from typing import Any
import math

VALID_INT_TYPE_VAL = ["u1", "u2", "u2le", "u2be", "u4", "u4le", "u4be", "u8", "u8le",
                      "u8be", "s1", "s2", "s2le", "s2be", "s4", "s4le", "s4be", "s8", "s8le", "s8be"]
VALID_FLOAT_TYPE_VAL = ["f4", "f4le", "f4be", "f8", "f8le", "f8be"]
VALID_STR_TYPE_VAL = ["str", "strz"]


class DefaultValuePopulator():

    def __init__(self, source: dict[str, Any]):
        self.key_handler = dict()
        self.source = source
        self._register_default_handler()

    @staticmethod
    def _int_min_max(type_key: str) -> tuple[int, int]:
        """
        Arguments:
        type_key: Valid type for int (u1, u2, s4be, etc.)
        """
        match type_key:
            case "u1":
                return (0, 255)
            case "u2" | "u2le" | "u2be":
                return (0, 65535)
            case "u4" | "u4le" | "u4be":
                return (0, 4294967295)
            case "u8" | "u8le" | "u8be":
                return (0, 18446744073709551615)
            case "s1":
                return (-128, 127)
            case "s2" | "s2le" | "s2be":
                return (-32768, 32767)
            case "s4" | "s4le" | "s4be":
                return (-2147483648, 2147483647)
            case "s8" | "s8le" | "s8be":
                return (-9223372036854775808, 9223372036854775807)
            case _:
                raise ValueError("Not a valid integer type")

    @staticmethod
    def _float_min_max(type_key: str) -> tuple[float, float]:
        return (-math.inf, math.inf)

    def _register_default_handler(self):
        default_handler = {
            "meta": self.handle_meta,
            "seq": self.handle_seq
        }
        for k, v in default_handler.items():
            self.key_handler.setdefault(k, v)

    def handle_meta(self, val):
        pass

    def handle_seq(self, val):
        print(val)
        for entry in val:
            self.handle_seq_entry(entry)

    def handle_seq_entry(self, val):
        if "type" in val:
            t = val["type"]
            if t in VALID_INT_TYPE_VAL:
                min_val, max_val = self._int_min_max(t)
                val.setdefault("-fz-range-min", min_val)
                val.setdefault("-fz-range-max", max_val)
            elif t in VALID_FLOAT_TYPE_VAL:
                min_val, max_val = self._float_min_max(t)
                val.setdefault("-fz-range-min", min_val)
                val.setdefault("-fz-range-max", max_val)
            elif t in VALID_STR_TYPE_VAL:
                raise NotImplementedError

    def populate_default(self):
        for k, v in self.source.items():
            fn = self.key_handler[k]
            fn(v)
