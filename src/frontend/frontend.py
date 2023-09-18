from typing import Any
from datastructure.intermediate_representation import IntermediateRepresentation
from frontend.default_value import DefaultValuePopulator


class Frontend():
    def __init__(self, source: dict[str, Any]):
        self.source = source

    def populate_default_value(self) -> None:
        populator = DefaultValuePopulator(self.source)
        populator.populate_default()

    def generate_ir(self) -> IntermediateRepresentation:
        self.populate_default_value()
        return IntermediateRepresentation(self.source)
