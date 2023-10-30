from typing import Any, List, Optional
from utils.types import BaseObject, SeqEntry
from utils import const
import math
import sys

VALID_INT_TYPE_VAL = ["u1", "u2", "u2le", "u2be", "u4", "u4le", "u4be", "u8", "u8le",
                      "u8be", "s1", "s2", "s2le", "s2be", "s4", "s4le", "s4be", "s8", "s8le", "s8be"]
VALID_FLOAT_TYPE_VAL = ["f4", "f4le", "f4be", "f8", "f8le", "f8be"]
VALID_STR_TYPE_VAL = ["str", "strz"]
VALID_BYTE_TYPE_VAL = [None,]


class DefaultValuePopulator():

    def __init__(self, source: dict[str, Any], base_class_endian: Optional[str] = None):
        self.key_handler = dict()
        self.source = source
        self.base_class_endian = base_class_endian
        if self.base_class_endian is None:
            if "little" == sys.byteorder:
                self.base_class_endian = "le"
            else:
                self.base_class_endian = "be"
        self._register_default_handler()

    @staticmethod
    def _int_min_max(type_key: str) -> tuple[int, int]:
        """
        Arguments:
        type_key: Valid type for int (u1, u2, s4be, etc.)
        """
        match type_key:
            case "u1":
                return (const.u1_MIN, const.u1_MAX)
            case "u2" | "u2le" | "u2be":
                return (const.u2_MIN, const.u2_MAX)
            case "u4" | "u4le" | "u4be":
                return (const.u4_MIN, const.u4_MAX)
            case "u8" | "u8le" | "u8be":
                return (const.u8_MIN, const.u8_MAX)
            case "s1":
                return (const.s1_MIN, const.s1_MAX)
            case "s2" | "s2le" | "s2be":
                return (const.s2_MIN, const.s2_MAX)
            case "s4" | "s4le" | "s4be":
                return (const.s4_MIN, const.s4_MAX)
            case "s8" | "s8le" | "s8be":
                return (const.s8_MIN, const.s8_MAX)
            case _:
                raise ValueError("Not a valid integer type")

    @staticmethod
    def _float_min_max(type_key: str) -> tuple[float, float]:
        return (-math.inf, math.inf)

    def _register_default_handler(self):
        default_handler = {
            "meta": self.handle_meta,
            "doc": self.handle_doc,
            "doc-ref": self.handle_doc_ref,
            "seq": self.handle_seq,
            "types": self.handle_types,
            "instances": self.handle_instances,
            "enums": self.handle_enums,
        }
        for k, v in default_handler.items():
            self.key_handler.setdefault(k, v)

    def handle_base_object(self, val: BaseObject):
        val.setdefault("doc", "")
        val.setdefault("doc-ref", "")
        val.setdefault("types", dict())
        val.setdefault("instances", dict())
        val.setdefault("enums", dict())

    def handle_meta(self, val) -> None:
        # Default to system endian if not specified
        val.setdefault("endian", self.base_class_endian)

    def handle_doc(self, val) -> None:
        pass

    def handle_doc_ref(self, val) -> None:
        pass

    def handle_seq(self, val: List[SeqEntry]):
        """Populate the `seq` key content with default value
        """
        for entry in val:
            self.handle_seq_entry(entry)

    def handle_seq_entry(self, val):
        val.setdefault("type", None)  # Generate bytes if not specified
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
                val.setdefault("encoding", "UTF-8")
                val.setdefault("terminator", None)
            elif t in VALID_BYTE_TYPE_VAL:
                val.setdefault("contents", None)
                val.setdefault("size", -1)

    def handle_types(self, val):
        for type_name, type_entry in val.items():
            type_entry.setdefault("meta", {"id": type_name})
            DefaultValuePopulator(type_entry, self.base_class_endian).populate_default()

    def handle_instances(self, val):
        pass

    def handle_enums(self, val):
        for enum_class_name, enum_class_items in val.items():
            for enum_int_key, enum_val in enum_class_items.items():
                enum_val.setdefault("doc", "")
                enum_val.setdefault("doc-ref", "")

    def populate_default(self):
        self.handle_base_object(self.source)
        for k, v in self.source.items():
            fn = self.key_handler[k]
            fn(v)
