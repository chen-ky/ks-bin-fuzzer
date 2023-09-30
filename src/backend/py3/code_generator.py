from datastructure.intermediate_representation import IntermediateRepresentation
from backend.generator import Generator
import backend.py3.utils.sanitiser as sanitiser
from io import StringIO
from pathlib import Path
from backend.utils.indenter import Indenter
from typing import List
from utils.types import SeqEntry

import logging
import sys


class Python3CodeGenerator(Generator):

    KS_HELPER_INSTANCE = ""  # TODO

    def __init__(self, ir: IntermediateRepresentation, output: StringIO) -> None:
        self.ir = ir
        self.output = output

        self.logger = logging.Logger(__name__)
        self.logger.setLevel(logging.DEBUG)
        log_stream_handler = logging.StreamHandler(sys.stderr)
        log_stream_handler.setFormatter(
            logging.Formatter(logging.BASIC_FORMAT))
        self.logger.addHandler(log_stream_handler)

    @staticmethod
    def _ks_helper_fn_call(fn_name: str, *args, **kwargs) -> str:
        arg_delimiter = ", "
        fn_call = f"{Python3CodeGenerator.KS_HELPER_INSTANCE}.{fn_name}"
        fn_call += "("
        for arg in args:
            fn_call += f"{arg}{arg_delimiter}"
        for k, v in kwargs.items():
            fn_call += f"{k}={v}{arg_delimiter}"
        # Remove delimiter from last arg
        fn_call = fn_call.rstrip(arg_delimiter)
        fn_call += ")"
        return fn_call

    def write_file_from_include_dir(self):
        """Write the contents of the files in the include directory to the specified output"""
        path_glob = "include/_[0-9][0-9]*.py"
        # This includes directory which matches the glob pattern
        match_list = list(Path(__file__).parent.glob(path_glob))
        match_list.sort()  # Sort the list so the files are included in the correct order

        for item_path in match_list:
            if item_path.is_dir():
                continue
            with open(item_path, "r") as f:
                self.output.writelines(f.readlines())

    def write_base_object_class(self):
        meta_val = self.ir.source["meta"]
        seq_val = self.ir.source["seq"]
        types_val = self.ir.source["types"]  # TODO
        self.output.writelines(
            self.generate_class(meta_val["id"], seq_val)
        )

    def generate_class(self, class_name: str, seq: List[SeqEntry]) -> List[str]:
        class_name = sanitiser.sanitise_class_name(class_name)
        self.logger.debug(class_name)
        indenter = Indenter(add_newline=True)
        code = indenter.apply([
            f"class {class_name}():",
            "    def __init__(self) -> None:",
            "        pass"
        ])
        indenter.indent(add_indent=2)
        for seq_entry in seq:
            code.extend(indenter.apply(self.generate_seq_entry(seq_entry)))
        return code

    def generate_seq_entry(self, seq_entry: SeqEntry):
        entry_name = f"self.{seq_entry['id']}"  # FIXME sanitise name?
        self.logger.debug(entry_name)
        indenter = Indenter(add_newline=True)
        code = indenter.apply([
            f"self.{entry_name} = None  # TODO",
        ])
        return code

    def generate_code(self) -> None:
        self.logger.debug(self.ir.source)
        self.write_file_from_include_dir()
        self.write_base_object_class()
