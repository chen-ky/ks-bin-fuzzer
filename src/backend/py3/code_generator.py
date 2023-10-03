from datastructure.intermediate_representation import IntermediateRepresentation
from backend.generator import Generator
from backend.utils.indenter import Indenter
import backend.py3.utils.sanitiser as sanitiser
from utils.types import SeqEntry
from .base_type_code_generator import BaseTypeCodeGenerator

from io import StringIO
from pathlib import Path
from typing import List
import logging
import sys


class Python3CodeGenerator(Generator):

    KS_HELPER_INSTANCE = "ks_helper"  # Defined in _99_global_obj.py

    def __init__(self, ir: IntermediateRepresentation, output: StringIO) -> None:
        self.ir = ir
        self.output = output

        self.base_type_code_generator = BaseTypeCodeGenerator(
            ks_helper_instance_name=self.KS_HELPER_INSTANCE)

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

    def write_file_from_include_dir(self) -> None:
        """Write the contents of the files in the include directory to the specified output"""
        path_glob = "include/_[0-9][0-9]*.py"
        # This includes directory which matches the glob pattern
        match_list = list(Path(__file__).parent.glob(path_glob))
        match_list.sort()  # Sort the list so the files are included in the correct order

        for item_path in match_list:
            if item_path.is_dir():
                continue
            with open(item_path, "r") as f:
                # Add file name as comment
                self.output.write(f"# include_start <{item_path.name}>\n")
                # Write file content
                self.output.writelines(f.readlines())
                # Add file name as comment
                self.output.write(f"# include_end <{item_path.name}>\n")
                # Add 2 new lines after every include
                self.output.write("\n\n")

    def write_base_object_class(self) -> None:
        meta_val = self.ir.source["meta"]
        seq_val = self.ir.source["seq"]
        types_val = self.ir.source["types"]  # TODO
        self.output.writelines(
            self.generate_class(meta_val["id"], seq_val)
        )

    def write_entry_point(self) -> None:
        self.output.writelines(self.generate_entry_point())

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
        code.append("\n")
        indenter.unindent()
        code.extend(
            indenter.apply([
                "def generate(self) -> bytes:",
                "    result = SeekableBuffer()"
            ])
        )
        indenter.indent()
        for seq_entry in seq:
            entry_name = f"self.{seq_entry['id']}"  # FIXME sanitise name?
            entry_type = seq_entry['type']
            match entry_type:
                case "u1":
                    indenter.append_line(
                        f"result.append(struct.pack('B', {entry_name}))", code)
                case "u2le":
                    indenter.append_line(
                        f"result.append(struct.pack('<H', {entry_name}))", code)
                case "u2be":
                    indenter.append_line(
                        f"result.append(struct.pack('>H', {entry_name}))", code)
                case "u4le":
                    indenter.append_line(
                        f"result.append(struct.pack('<I', {entry_name}))", code)
                case "u4be":
                    indenter.append_line(
                        f"result.append(struct.pack('>I', {entry_name}))", code)
                case "u8le":
                    indenter.append_line(
                        f"result.append(struct.pack('<Q', {entry_name}))", code)
                case "u8be":
                    indenter.append_line(
                        f"result.append(struct.pack('>Q', {entry_name}))", code)
                case "s1":
                    indenter.append_line(
                        f"result.append(struct.pack('b', {entry_name}))", code)
                case "s2le":
                    indenter.append_line(
                        f"result.append(struct.pack('<h', {entry_name}))", code)
                case "s2be":
                    indenter.append_line(
                        f"result.append(struct.pack('>h', {entry_name}))", code)
                case "s4le":
                    indenter.append_line(
                        f"result.append(struct.pack('<i', {entry_name}))", code)
                case "s4be":
                    indenter.append_line(
                        f"result.append(struct.pack('>i', {entry_name}))", code)
                case "s8le":
                    indenter.append_line(
                        f"result.append(struct.pack('<q', {entry_name}))", code)
                case "s8be":
                    indenter.append_line(
                        f"result.append(struct.pack('>q', {entry_name}))", code)
                case "f4le":
                    indenter.append_line(
                        f"result.append(struct.pack('<f', {entry_name}))", code)
                case "f4be":
                    indenter.append_line(
                        f"result.append(struct.pack('>f', {entry_name}))", code)
                case "f8le":
                    indenter.append_line(
                        f"result.append(struct.pack('<d', {entry_name}))", code)
                case "f8be":
                    indenter.append_line(
                        f"result.append(struct.pack('>d', {entry_name}))", code)
                case _:
                    raise NotImplementedError  # TODO
        code.extend(indenter.apply([
            "result.seek(0)",  # Move pointer to start
            "return result.get_data()",  # Return bytes using pointer
        ]))
        indenter.append_line("\n", code)
        return code

    def generate_seq_entry(self, seq_entry: SeqEntry) -> List[str]:
        entry_name = f"{seq_entry['id']}"  # FIXME sanitise name?
        entry_type = seq_entry["type"]
        self.logger.debug(entry_name)
        indenter = Indenter(add_newline=True)
        code = indenter.apply([
            f"self.{entry_name} = {self.base_type_code_generator.get_gen_type_fn(entry_type)(start=seq_entry['-fz-range-min'], end=seq_entry['-fz-range-max'])}  # TODO",
        ])
        return code

    def generate_entry_point(self) -> List[str]:
        indenter = Indenter(add_newline=True)
        entry_point_class_name = sanitiser.sanitise_class_name(
            self.ir.entry_point_class_name)
        code = indenter.apply([
            'if "__main__" == __name__:',
            f'    entry_point = {entry_point_class_name}()',
            '    sys.stdout.buffer.write(entry_point.generate())',
            '    sys.stdout.flush()'
        ])
        return code

    def generate_code(self) -> None:
        self.logger.debug(self.ir.source)
        self.write_file_from_include_dir()
        self.write_base_object_class()
        self.write_entry_point()
