from __future__ import annotations
from typing import Any


class IntermediateRepresentation():
    def __init__(self, source: dict[str, Any], entry_point_class_name: str):
        self.source = source
        self.entry_point_class_name = entry_point_class_name
