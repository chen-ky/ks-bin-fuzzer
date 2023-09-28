from datastructure.intermediate_representation import IntermediateRepresentation
from backend.generator import Generator
import backend.py3.utils.sanitiser as sanitiser


class Python3CodeGenerator(Generator):

    def __init__(self, ir: IntermediateRepresentation) -> None:
        self.ir = ir

    def generate_code(self) -> str:
        print(self.ir.source)
        print(sanitiser.sanitise_class_name("Class"))
