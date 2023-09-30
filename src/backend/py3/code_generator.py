from datastructure.intermediate_representation import IntermediateRepresentation
from backend.generator import Generator
import backend.py3.utils.sanitiser as sanitiser
from io import StringIO
from pathlib import Path


class Python3CodeGenerator(Generator):

    def __init__(self, ir: IntermediateRepresentation, output: StringIO) -> None:
        self.ir = ir
        self.output = output

    def write_file_from_include_dir(self):
        path_glob = "include/_[0-9][0-9]*.py"
        # This includes directory which matches the glob pattern
        match_list = list(Path(__file__).parent.glob(path_glob))
        match_list.sort()  # Sort the list so the files are included in the correct order

        for item_path in match_list:
            if item_path.is_dir():
                continue
            with open(item_path, "r") as f:
                self.output.writelines(f.readlines())

    def generate_code(self) -> str:
        self.write_file_from_include_dir()
        print(self.ir.source)
        print(sanitiser.sanitise_class_name("Class"))
