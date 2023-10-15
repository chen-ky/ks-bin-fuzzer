from typing import Any
import re


class RefProcessor():
    """Do processing on references"""

    KEY_WITH_REFERENCES = (r"size", r"process", r"\-fz\-process\-.+")

    def __init__(self, source: dict[str, Any]):
        self.source = source

    def pre_process(self):
        pass

    def post_process(self):
        for seq_entry in self.source["seq"]:
            for seq_entry_k, seq_entry_v in seq_entry.items():
                for regex in self.KEY_WITH_REFERENCES:
                    if re.fullmatch(regex, seq_entry_k) is not None and isinstance(seq_entry_v, str):
                        seq_entry[seq_entry_k] = "".join(seq_entry_v.split())  # Remove any whitespace
                        break
        custom_types = self.source.get("types")
        if custom_types is not None:
            for custom_type_src in custom_types.values():
                RefProcessor(custom_type_src).post_process()
