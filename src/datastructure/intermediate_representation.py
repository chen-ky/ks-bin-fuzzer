from __future__ import annotations
from typing import Any


class IntermediateRepresentation():
    def __init__(self, source: dict[str, Any]):
        self.source = source
        self.entry_point_class_name = source["meta"]["id"]  # TODO job for frontend
