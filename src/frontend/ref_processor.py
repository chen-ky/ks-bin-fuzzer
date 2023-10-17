from typing import Any
import re


class RefProcessor():
    """Do processing on references"""

    def __init__(self, source: dict[str, Any]):
        self.source = source

    def pre_process(self):
        pass

    def post_process(self):
        self.source["_available_ref"] = []
        for seq_entry in self.source["seq"]:
            self.source["_available_ref"].append(seq_entry["id"])

        custom_types = self.source.get("types")
        if custom_types is not None:
            for custom_type_src in custom_types.values():
                RefProcessor(custom_type_src).post_process()
