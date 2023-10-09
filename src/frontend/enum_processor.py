from typing import Any


class EnumProcessor():
    def __init__(self, source: dict[str, Any]):
        self.source = source

    def pre_process(self):
        enums = self.source["enums"]
        for enum_class_name, enum_class_items in enums.items():
            for enum_int_key, enum_val in enum_class_items.items():
                # Transform enum to verbose enum if needed
                # https://doc.kaitai.io/user_guide.html#verbose-enums
                if isinstance(enum_val, str):
                    enum_class_items[enum_int_key] = {"id": enum_val}

    def post_process(self):
        pass
