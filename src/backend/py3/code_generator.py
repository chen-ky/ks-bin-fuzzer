from datastructure.intermediate_representation import IntermediateRepresentation
from backend.generator import Generator
from backend.utils.indenter import Indenter
import backend.py3.utils.sanitiser as sanitiser
from utils.types import SeqEntry, VerboseEnumClassEntry
from .value_code_generator import ValueCodeGenerator

from io import StringIO
from pathlib import Path
from typing import List, Any
import logging
import sys


class Python3CodeGenerator(Generator):

    KS_HELPER_INSTANCE = "ks_helper"  # Defined in _99_global_obj.py

    def __init__(self, ir: IntermediateRepresentation, output: StringIO) -> None:
        self.ir = ir
        self.output = output

        self.base_type_code_generator = ValueCodeGenerator(
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

    @staticmethod
    def _enum_literal_to_enum(enum_literal: str) -> str:
        enum_name, enum_val = enum_literal.split("::", maxsplit=1)
        enum_name = sanitiser.sanitise_class_name(enum_name)
        return f"{enum_name}.{enum_val}"


    def write_file_from_include_dir(self) -> None:
        """Write the contents of the files in the 'include' directory to the specified output"""
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
        doc_val = self.ir.source["doc"]
        seq_val = self.ir.source["seq"]
        self.output.writelines(
            self.generate_class(meta_val, seq_val, doc_val)
        )

    def write_types(self) -> None:
        types_val = self.ir.source["types"]
        for t_name, t_val in types_val.items():
            meta_val = t_val
            meta_val["id"] = t_name
            doc_val = meta_val["doc"]
            seq_val = meta_val["seq"]
            self.output.writelines(
                self.generate_class(meta_val, seq_val, doc_val)
            )

    def write_enums(self) -> None:
        enums = self.ir.source["enums"]
        for enum_class_name, enum_entries in enums.items():
            self.output.writelines(
                self.generate_enum(enum_class_name, enum_entries)
            )

    def write_entry_point(self) -> None:
        self.output.writelines(self.generate_entry_point())

    def generate_doc(self, doc: str) -> List[str]:
        indenter = Indenter(add_newline=True)
        doc_str = indenter.apply([
            "\"\"\"",
            f"{doc}",
            "\"\"\""
        ])
        return doc_str

    def generate_enum(self, enum_name: str, enum_entries: VerboseEnumClassEntry) -> List[str]:
        enum_name = sanitiser.sanitise_class_name(enum_name)
        self.logger.debug(f"Generating enum \"{enum_name}\"")
        indenter = Indenter(add_newline=True)
        code = indenter.apply([
            "@unique",
            f"class {enum_name}(Enum):",
        ])
        indenter.indent()
        for enum_int_key, enum_val in enum_entries.items():
            enum_int_id = enum_val["id"]
            indenter.append_line(f"{enum_int_id} = {enum_int_key}", code)
        indenter.reset()
        indenter.append_line("\n", code)
        return code

    def generate_class_static_var(self, seq: List[SeqEntry]) -> List[str]:
        """Handle static variable for a type, such as those using `-fz-order`"""
        indenter = Indenter(add_newline=True)
        code = []
        for seq_entry in seq:
            generate_order = seq_entry.get("-fz-order")
            if generate_order is not None and len(generate_order) > 0:
                entry_name = seq_entry["id"]
                indenter.append_line(f"{entry_name} = {generate_order}", code)
        code.append("")
        return code

    def generate_class_init_method(self, class_name: str, seq: List[SeqEntry]) -> List[str]:
        indenter = Indenter(add_newline=True)
        code = []
        indenter.append_lines([
            "def __init__(self, _parent=None, _root=None) -> None:",
            "    self._parent = _parent",
            "    self._root = _root if _root is not None else self",
            "    self._io = SeekableBuffer()",
        ], code)
        indenter.indent()
        for seq_entry in seq:
            indenter.append_lines(self.generate_seq_entry(
                class_name, seq_entry), code)
        indenter.append_line("", code)
        return code

    def generate_class(self, meta: dict[str, Any], seq: List[SeqEntry], doc: str) -> List[str]:
        class_name = sanitiser.sanitise_class_name(meta["id"])
        self.logger.debug(f"Generating class \"{class_name}\"")
        indenter = Indenter(add_newline=True)
        code = indenter.apply([
            f"class {class_name}():",
        ])
        indenter.indent()
        if len(doc) > 0:
            indenter.append_lines(self.generate_doc(doc), code)
        indenter.append_lines(self.generate_class_static_var(seq), code)
        indenter.append_lines(self.generate_class_init_method(class_name, seq), code)
        indenter.append_lines([
            "def generate(self) -> bytes:",
        ], code)
        indenter.indent()
        for seq_entry in seq:
            enum_name = seq_entry.get("enum")
            entry_name = f"self.{seq_entry['id']}"  # FIXME sanitise name?
            if enum_name is not None:
                entry_name = f"{entry_name}.value"
            entry_type = seq_entry['type']
            match entry_type:
                case "u1":
                    indenter.append_line(
                        f"self._io.append(struct.pack('B', {entry_name}))", code)
                case "u2le":
                    indenter.append_line(
                        f"self._io.append(struct.pack('<H', {entry_name}))", code)
                case "u2be":
                    indenter.append_line(
                        f"self._io.append(struct.pack('>H', {entry_name}))", code)
                case "u4le":
                    indenter.append_line(
                        f"self._io.append(struct.pack('<I', {entry_name}))", code)
                case "u4be":
                    indenter.append_line(
                        f"self._io.append(struct.pack('>I', {entry_name}))", code)
                case "u8le":
                    indenter.append_line(
                        f"self._io.append(struct.pack('<Q', {entry_name}))", code)
                case "u8be":
                    indenter.append_line(
                        f"self._io.append(struct.pack('>Q', {entry_name}))", code)
                case "s1":
                    indenter.append_line(
                        f"self._io.append(struct.pack('b', {entry_name}))", code)
                case "s2le":
                    indenter.append_line(
                        f"self._io.append(struct.pack('<h', {entry_name}))", code)
                case "s2be":
                    indenter.append_line(
                        f"self._io.append(struct.pack('>h', {entry_name}))", code)
                case "s4le":
                    indenter.append_line(
                        f"self._io.append(struct.pack('<i', {entry_name}))", code)
                case "s4be":
                    indenter.append_line(
                        f"self._io.append(struct.pack('>i', {entry_name}))", code)
                case "s8le":
                    indenter.append_line(
                        f"self._io.append(struct.pack('<q', {entry_name}))", code)
                case "s8be":
                    indenter.append_line(
                        f"self._io.append(struct.pack('>q', {entry_name}))", code)
                case "f4le":
                    indenter.append_line(
                        f"self._io.append(struct.pack('<f', {entry_name}))", code)
                case "f4be":
                    indenter.append_line(
                        f"self._io.append(struct.pack('>f', {entry_name}))", code)
                case "f8le":
                    indenter.append_line(
                        f"self._io.append(struct.pack('<d', {entry_name}))", code)
                case "f8be":
                    indenter.append_line(
                        f"self._io.append(struct.pack('>d', {entry_name}))", code)
                case "str" | "strz":
                    indenter.append_line(
                        f"self._io.append({entry_name}.encode(encoding=\"{seq_entry['encoding'].lower()}\"))", code
                    )
                case None:
                    indenter.append_line(
                        f"self._io.append({entry_name})", code
                    )
                case _:
                    # Custom type
                    if "repeat" in seq_entry:
                        indenter.append_lines([
                            f"for entry_instance in {entry_name}:",
                            "    self._io.append(entry_instance.generate())",
                        ], code)
                    else:
                        indenter.append_line(
                            f"self._io.append({entry_name}.generate())", code
                        )
        indenter.append_lines([
            "self._io.seek(0)",  # Move pointer to start
            "return self._io.get_data()",  # Return bytes using pointer,
            "",
        ], code)
        indenter.unindent()
        indenter.append_lines([
            "def __len__(self) -> int:",
            "    return len(self._io)",
        ], code)
        indenter.reset()
        indenter.append_line("\n", code)
        self.logger.debug(f"Done generating class \"{class_name}\"")
        return code

    def generate_seq_entry(self, class_name: str, seq_entry: SeqEntry) -> List[str]:
        entry_name = f"{seq_entry['id']}"  # FIXME sanitise name?
        self.logger.debug(f"Generating seq entry \"{entry_name}\"")
        indenter = Indenter(add_newline=True)
        code = []

        if "repeat" in seq_entry:
            seq_class_name = sanitiser.sanitise_class_name(seq_entry["type"])
            indenter.append_line(
                f"self.{entry_name} = []",
                code
            )
            repeat_type = seq_entry["repeat"]
            if repeat_type == "until":
                # loop_conditions = seq_entry["repeat-until"].replace("_io.eof", "self._io.is_eos()")
                loop_conditions = seq_entry["repeat-until"].replace("_io.eof", "False")  # Ignore eos/eof for now
                indenter.append_lines([
                    "while True:",
                    f"    _ = {seq_class_name}(_parent=self, _root=self._root)",
                    f"    self.{entry_name}.append(_)",
                    f"    if ({loop_conditions}):",
                    "        break",
                ], code)
            else:
                raise NotImplementedError
        elif "-fz-order" in seq_entry:
            indenter.append_line(
                f"self.{entry_name} = {class_name}.{entry_name}.pop(0)",
                code
            )
        elif "-fz-choice" in seq_entry:
            choice_list = []
            if "enum" in seq_entry:
                choice_list = []
                for choice in seq_entry["-fz-choice"]:
                    choice_list.append(self._enum_literal_to_enum(choice))
                choice_list = "[" + ", ".join(choice_list) + "]"  # Remove quotes from enum string
            else:
                choice_list = seq_entry["-fz-choice"]

            indenter.append_line(
                f"self.{entry_name} = {self.KS_HELPER_INSTANCE}.rand_choice({choice_list})",
                code
            )
        else:
            indenter.append_line(
                f"self.{entry_name} = {self.base_type_code_generator.generate_code(**seq_entry)}",
                code
            )
        return code

    def generate_entry_point(self) -> List[str]:
        indenter = Indenter(add_newline=True)
        entry_point_class_name = sanitiser.sanitise_class_name(
            self.ir.entry_point_class_name)
        code = indenter.apply([
            'if "__main__" == __name__:',
            f'    entry_point = {entry_point_class_name}(_parent=None, _root=None)',
            '    sys.stdout.buffer.write(entry_point.generate())',
            '    sys.stdout.flush()',
        ])
        return code

    def generate_code(self) -> None:
        # import json
        # self.logger.debug(json.dumps(self.ir.source, indent=2))
        self.logger.debug(self.ir.source)
        self.write_file_from_include_dir()
        self.write_enums()
        self.write_base_object_class()
        self.write_types()
        self.write_entry_point()
