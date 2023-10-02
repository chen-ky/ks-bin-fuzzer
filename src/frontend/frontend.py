from typing import Any
from datastructure.intermediate_representation import IntermediateRepresentation
from frontend.default_value import DefaultValuePopulator
from frontend.type_processor import TypeProccessor


class Frontend():
    def __init__(self, source: dict[str, Any]):
        self.source = source

    def populate_default_value(self) -> None:
        populator = DefaultValuePopulator(self.source)
        populator.populate_default()

    def run_processor(self) -> None:
        type_proc = TypeProccessor(self.source)
        type_proc.process()

    def generate_ir(self) -> IntermediateRepresentation:
        self.populate_default_value()
        self.run_processor()
        return IntermediateRepresentation(self.source)
