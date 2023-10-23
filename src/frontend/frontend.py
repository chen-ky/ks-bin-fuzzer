from typing import Any
from datastructure.intermediate_representation import IntermediateRepresentation
from frontend.default_value import DefaultValuePopulator
from frontend.type_processor import TypeProcessor
from frontend.enum_processor import EnumProcessor
from frontend.ref_processor import RefProcessor


class Frontend():
    def __init__(self, source: dict[str, Any]):
        self.source = source

    def populate_default_value(self) -> None:
        populator = DefaultValuePopulator(self.source, self.source["meta"]["endian"])
        populator.populate_default()

    def run_preprocessor(self) -> None:
        processors = [EnumProcessor(self.source),]
        for proc in processors:
            proc.pre_process()

    def run_postprocessor(self) -> None:
        processors = [TypeProcessor(self.source), RefProcessor(self.source)]
        for proc in processors:
            proc.post_process()

    def generate_ir(self) -> IntermediateRepresentation:
        self.run_preprocessor()
        self.populate_default_value()
        self.run_postprocessor()
        return IntermediateRepresentation(self.source, self.source["meta"]["id"])
