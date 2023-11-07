from typing import Any


class ValidProcessor():
    def __init__(self, source: dict[str, Any]):
        self.source = source

    def pre_process(self):
        seq = self.source["seq"]
        for seq_entry in seq:
            if "valid" in seq_entry and isinstance(seq_entry["valid"], dict):
                min_val = seq_entry["valid"].get("min")
                max_val = seq_entry["valid"].get("max")
                if min_val is not None:
                    seq_entry["-fz-range-min"] = min_val
                if max_val is not None:
                    seq_entry["-fz-range-max"] = max_val
                seq_entry.pop("valid")
        # Process valid key that might be in nested types
        custom_types = self.source.get("types")
        if custom_types is not None:
            for custom_type_src in custom_types.values():
                ValidProcessor(custom_type_src).pre_process()

    def post_process(self):
        pass
