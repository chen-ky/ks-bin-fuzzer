from typing import Any
from utils.types import SeqEntry


class TypeProcessor():
    def __init__(self, source: dict[str, Any]):
        self.source = source
        self.endian = self.source["meta"]["endian"]

    def _to_explicit_endian(self, seq_entry: SeqEntry):
        if seq_entry["type"] in ("u2", "u4", "u8", "s2", "s4", "s8", "f4", "f8"):
            seq_entry["type"] += self.endian

    def pre_process(self):
        pass

    def post_process(self):
        for seq_entry in self.source["seq"]:
            self._to_explicit_endian(seq_entry)
        for type_name, type_entry in self.source["types"].items():
            # Recursively process custom types
            TypeProcessor(type_entry).post_process()
