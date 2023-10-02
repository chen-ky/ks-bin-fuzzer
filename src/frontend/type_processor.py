from typing import Any


class TypeProccessor():
    def __init__(self, source: dict[str, Any]):
        self.source = source
        self.endian = self.source["meta"]["endian"]

    def process(self):
        for seq_entry in self.source["seq"]:
            if seq_entry["type"] in ("u2", "u4", "u8", "s2", "s4", "s8", "f4", "f8"):
                seq_entry["type"] += self.endian
