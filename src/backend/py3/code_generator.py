from datastructure.intermediate_representation import IntermediateRepresentation
from backend.generator import Generator
from backend.utils.indenter import Indenter
import backend.py3.utils.sanitiser as sanitiser
from utils.types import SeqEntry, VerboseEnumClassEntry
from utils.const import KEY_WITH_EXPRESSION, KEY_WITH_EXPRESSION_PRODUCE_BYTES
from datastructure.dependency_graph import DependencyGraph
from .value_code_generator import ValueCodeGenerator
import re

from io import StringIO
from pathlib import Path
from typing import List, Any
import logging
import sys


class Python3CodeGenerator(Generator):

    KS_HELPER_INSTANCE = "ks_helper"  # Defined in _99_global_obj.py

    CHECKSUM_FN_NAME_MAP = {
        "-fz-process-crc32": "crc32",
        "-fz-process-md5": "md5",
        "-fz-process-sha1": "sha1",
        "-fz-process-sha224": "sha224",
        "-fz-process-sha256": "sha256",
        "-fz-process-sha384": "sha384",
        "-fz-process-sha512": "sha512",
        "-fz-process-sha3-224": "sha3_224",
        "-fz-process-sha3-256": "sha3_256",
        "-fz-process-sha3-384": "sha3_384",
        "-fz-process-sha3-512": "sha3_512",
    }

    def __init__(self, ir: IntermediateRepresentation, output: StringIO, is_entry_point: bool = False) -> None:
        self.ir = ir
        self.output = output
        self.is_entry_point = is_entry_point

        self.type_code_generator = ValueCodeGenerator(
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
    def _transpile_namespace(expression: str) -> str:
        cleaned_expression = []
        for ns in expression.split("::"):
            ns = ns.strip()
            if len(ns) <= 0:
                continue
            cleaned_expression.append(ns)
        for i in range(len(cleaned_expression) - 1):
            cleaned_expression[i] = sanitiser.sanitise_class_name(
                cleaned_expression[i])
        return ".".join(cleaned_expression)

    @staticmethod
    def _transpile_local_ref(available_ref: List[str], expression: str) -> str:
        cleaned_expression = []
        for value in expression.split():
            if value in available_ref:
                cleaned_expression.append(f"self.{value}")
            else:
                cleaned_expression.append(value)
        return " ".join(cleaned_expression)

    @classmethod
    def _transpile_local_ref_to_bytes(cls, available_ref: List[str], expression: str) -> str:
        expression = cls._transpile_local_ref(available_ref, expression)
        cleaned_expression = []
        for value in expression.split():
            # "_" is a special variable, representing the previously parsed/generated object
            if value.startswith("self.") or value.startswith("_."):
                cleaned_expression.append(f"{value}_to_bytes()")
            else:
                cleaned_expression.append(value)
        return " ".join(cleaned_expression)

    @staticmethod
    def _transpile_ternary(expression: str) -> str:
        last_quote_type = None
        ternary_question_mark_pos = None
        ternary_colon_pos = None
        for i, c in enumerate(expression):
            if last_quote_type is None and (c == "\"" or c == "'"):
                if i > 0 and expression[i - 1] == "\\":
                    # Escaped quote
                    continue
                else:
                    # Opening quote
                    last_quote_type = c
                    continue
            elif last_quote_type == c:
                # Closing quote
                last_quote_type = None
                continue
            if last_quote_type is None and c == "?":
                if ternary_question_mark_pos is None:
                    ternary_question_mark_pos = i
                else:
                    raise ValueError("Stray `?` in ternary?")
            elif last_quote_type is None and ternary_question_mark_pos is not None and c == ":":
                if ternary_colon_pos is None:
                    ternary_colon_pos = i
                else:
                    raise ValueError("Stray `:` in ternary?")

        if last_quote_type is not None:
            raise ValueError("Unmatched quote in ternary")
        elif ternary_question_mark_pos is None:
            # Not a ternary
            return expression
        elif ternary_colon_pos is None:
            raise ValueError("Invalid ternary syntax")

        condition = expression[:ternary_question_mark_pos]
        if_true = expression[ternary_question_mark_pos + 1: ternary_colon_pos]
        if_false = expression[ternary_colon_pos + 1:]
        return f"{if_true} if {condition} else {if_false}"

    @classmethod
    def _expression_transpiler(cls, available_ref: List[str], expression: str, produce_bytes: bool = False) -> str:
        # Do not process anything other than string (int, list etc.)
        if not isinstance(expression, str):
            return expression
        expression = cls._transpile_namespace(expression)
        if produce_bytes:
            expression = cls._transpile_local_ref_to_bytes(
                available_ref, expression)
        else:
            expression = cls._transpile_local_ref(available_ref, expression)
        expression = cls._transpile_ternary(expression)
        return expression

    # def _process_expression_in_seq(self):
    #     pass

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

    def write_class(self) -> None:
        meta_val = self.ir.source["meta"]
        doc_val = self.ir.source["doc"]
        seq_val = self.ir.source["seq"]
        available_ref = self.ir.source["_available_ref"]
        dependency_graph = self.ir.source["_dependency_graph"]
        self.output.writelines(
            self.generate_class(meta_val, seq_val, doc_val,
                                available_ref, dependency_graph)
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

    def generate_class_init_method(self, class_name: str, seq: List[SeqEntry], available_ref: List[str], dependency_graph: DependencyGraph) -> List[str]:
        indenter = Indenter(add_newline=True)
        code = []
        indenter.append_lines([
            "def __init__(self, _parent=None, _root=None) -> None:",
            "    self._parent = _parent",
            "    self._root = _root if _root is not None else self",
            "    self._io = SeekableBuffer()",
            "    self._cached = False",
        ], code)
        indenter.indent()
        # Generate data for each field taking into account dependencies on each other
        for dependency_node in dependency_graph.linearise_graph():
            seq_entry = None
            for entry in seq:
                if dependency_node.data == entry["id"]:
                    seq_entry = entry
            if seq_entry is None:
                raise ValueError(
                    f"Invalid reference `{dependency_node.data}`.")
        # for seq_entry in seq:
            indenter.append_lines(self.generate_seq_entry(
                class_name, seq_entry, available_ref), code)
        indenter.append_line("", code)
        return code

    def generate_seq_to_bytes_method(self, seq: List[SeqEntry]) -> List[str]:
        indenter = Indenter(add_newline=True)
        code = []
        for seq_entry in seq:
            enum_name = seq_entry.get("enum")
            entry_name = f"{seq_entry['id']}"  # FIXME sanitise name?
            indenter.append_lines(
                [f"def {entry_name}_to_bytes(self) -> bytes:"], code)
            indenter.indent()
            self_entry_name = f"self.{seq_entry['id']}"
            if enum_name is not None:
                self_entry_name = f"{self_entry_name}.value"
            entry_type = seq_entry['type']
            match entry_type:
                case "u1":
                    indenter.append_line(
                        f"return struct.pack('B', {self_entry_name})", code)
                case "u2le":
                    indenter.append_line(
                        f"return struct.pack('<H', {self_entry_name})", code)
                case "u2be":
                    indenter.append_line(
                        f"return struct.pack('>H', {self_entry_name})", code)
                case "u4le":
                    indenter.append_line(
                        f"return struct.pack('<I', {self_entry_name})", code)
                case "u4be":
                    indenter.append_line(
                        f"return struct.pack('>I', {self_entry_name})", code)
                case "u8le":
                    indenter.append_line(
                        f"return struct.pack('<Q', {self_entry_name})", code)
                case "u8be":
                    indenter.append_line(
                        f"return struct.pack('>Q', {self_entry_name})", code)
                case "s1":
                    indenter.append_line(
                        f"return struct.pack('b', {self_entry_name})", code)
                case "s2le":
                    indenter.append_line(
                        f"return struct.pack('<h', {self_entry_name})", code)
                case "s2be":
                    indenter.append_line(
                        f"return struct.pack('>h', {self_entry_name})", code)
                case "s4le":
                    indenter.append_line(
                        f"return struct.pack('<i', {self_entry_name})", code)
                case "s4be":
                    indenter.append_line(
                        f"return struct.pack('>i', {self_entry_name})", code)
                case "s8le":
                    indenter.append_line(
                        f"return struct.pack('<q', {self_entry_name})", code)
                case "s8be":
                    indenter.append_line(
                        f"return struct.pack('>q', {self_entry_name})", code)
                case "f4le":
                    indenter.append_line(
                        f"return struct.pack('<f', {self_entry_name})", code)
                case "f4be":
                    indenter.append_line(
                        f"return struct.pack('>f', {self_entry_name})", code)
                case "f8le":
                    indenter.append_line(
                        f"return struct.pack('<d', {self_entry_name})", code)
                case "f8be":
                    indenter.append_line(
                        f"return struct.pack('>d', {self_entry_name})", code)
                case "str" | "strz":
                    indenter.append_line(
                        f"return {self_entry_name}.encode(encoding=\"{seq_entry['encoding'].lower()}\")", code
                    )
                case None:
                    indenter.append_line(
                        f"return {self_entry_name}", code
                    )
                case _:
                    # Custom type
                    if "repeat" in seq_entry:
                        indenter.append_lines([
                            "result = b''",
                            f"for entry_instance in {self_entry_name}:",
                            "    result += entry_instance.result()",
                            "return result",
                        ], code)
                    else:
                        indenter.append_line(
                            f"return {self_entry_name}.result()", code
                        )
            indenter.append_line("", code)
            indenter.unindent()
        return code

    def generate_fz_process_code(self, fz_process_key: str, class_name: str, seq_entry: SeqEntry) -> List[str]:
        indenter = Indenter(add_newline=True)
        code = []
        entry_name = seq_entry["id"]
        expression = seq_entry[fz_process_key]
        if fz_process_key in self.CHECKSUM_FN_NAME_MAP.keys():
            fn_name = self.CHECKSUM_FN_NAME_MAP[fz_process_key]
            indenter.append_line(
                f"self.{entry_name} = {fn_name}({expression})", code)
        else:
            raise ValueError(f"Unknown key: '{fz_process_key}'")
        return code

    def generate_switch_type(self, entry_name: str, match_on: str, cases: dict[str, str]) -> List[str]:
        indenter = Indenter(add_newline=True)
        code = indenter.apply(f"match {match_on}:")
        indenter.indent()
        for match_value, type_name in cases.items():
            indenter.append_lines([
                f"case {match_value}:",
                f"    self.{entry_name} = {self.type_code_generator.generate_code(type=type_name)}",
            ], code)
        return code

    def generate_class(self, meta: dict[str, Any], seq: List[SeqEntry], doc: str, available_ref: List[str], dependency_graph: DependencyGraph) -> List[str]:
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
        indenter.append_lines(
            self.generate_class_init_method(class_name, seq, available_ref, dependency_graph), code)
        indenter.append_lines(self.generate_seq_to_bytes_method(seq), code)

        indenter.append_lines([
            "def result(self) -> bytes:",
            "    if self._cached:",
            "        self._io.seek(0)",  # Move pointer to start
            "        return self._io.get_data()",  # Return bytes using pointer,
        ], code)
        indenter.indent()
        for seq_entry in seq:
            # FIXME sanitise name?
            to_bytes_fn = f"self.{seq_entry['id']}_to_bytes()"
            indenter.append_lines([
                f"self._io.append({to_bytes_fn})"
            ], code)
        indenter.append_lines([
            "self._cached = True",
            "self._io.seek(0)",  # Move pointer to start
            "return self._io.get_data()",  # Return bytes using pointer,
            "",
        ], code)
        indenter.unindent()

        indenter.append_lines([
            "def __len__(self) -> int:",
            "    return len(self.result())",
        ], code)
        indenter.reset()
        indenter.append_line("\n", code)
        self.logger.debug(f"Done generating class \"{class_name}\"")
        return code

    def generate_seq_entry(self, class_name: str, seq_entry: SeqEntry, available_ref: List[str]) -> List[str]:
        entry_name = f"{seq_entry['id']}"  # FIXME sanitise name?
        self.logger.debug(f"Generating seq entry \"{entry_name}\"")
        indenter = Indenter(add_newline=True)
        code = []

        fz_process_key = None
        # Process expression
        for key in seq_entry.keys():
            for regex_key in KEY_WITH_EXPRESSION:
                if re.fullmatch(regex_key, key) is not None:
                    seq_entry[key] = self._expression_transpiler(
                        available_ref, seq_entry[key])
            for regex_key in KEY_WITH_EXPRESSION_PRODUCE_BYTES:
                if re.fullmatch(regex_key, key) is not None:
                    seq_entry[key] = self._expression_transpiler(
                        available_ref, seq_entry[key], produce_bytes=True)
            if re.fullmatch(r"\-fz\-process\-.+", key):
                fz_process_key = key
        # Process expression in a `type` block
        if isinstance(seq_entry["type"], dict):
            type_block = seq_entry["type"]
            for key in type_block.keys():
                for regex_key in KEY_WITH_EXPRESSION:
                    if re.fullmatch(regex_key, key) is not None:
                        type_block[key] = self._expression_transpiler(
                            available_ref, type_block[key])

        if "-fz-attr-len" in seq_entry:
            expression = seq_entry["-fz-attr-len"]
            indenter.append_line(
                f"self.{entry_name} = len({expression})",
                code
            )
        elif "repeat" in seq_entry:
            seq_class_name = sanitiser.sanitise_class_name(seq_entry["type"])
            indenter.append_line(
                f"self.{entry_name} = []",
                code
            )
            repeat_type = seq_entry["repeat"]
            if repeat_type == "until":
                # loop_conditions = seq_entry["repeat-until"].replace("_io.eof", "self._io.is_eos()")
                # Ignore eos/eof for now
                loop_conditions = seq_entry["repeat-until"].replace(
                    "_io.eof", "False")
                indenter.append_lines([
                    # Do while loop
                    "while True:",
                    f"    _ = {seq_class_name}(_parent=self, _root=self._root)",
                    f"    self.{entry_name}.append(_)",
                    f"    if ({loop_conditions}):",
                    "        break",
                ], code)
            else:
                raise NotImplementedError("Loop type not implemented")
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
                    choice_list.append(self._transpile_namespace(choice))
                # Remove quotes from enum string
                choice_list = "[" + ", ".join(choice_list) + "]"
            else:
                choice_list = seq_entry["-fz-choice"]

            indenter.append_line(
                f"self.{entry_name} = {self.KS_HELPER_INSTANCE}.rand_choice({choice_list})",
                code
            )
        elif fz_process_key is not None:
            indenter.append_lines(self.generate_fz_process_code(
                fz_process_key, class_name, seq_entry), code)
        elif isinstance(seq_entry["type"], dict):
            # Switch on type
            match_on = seq_entry["type"]["switch-on"]
            cases = seq_entry["type"]["cases"]
            indenter.append_lines(self.generate_switch_type(
                entry_name, match_on, cases), code)
        else:
            indenter.append_line(
                f"self.{entry_name} = {self.type_code_generator.generate_code(**seq_entry)}",
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
            '    sys.stdout.buffer.write(entry_point.result())',
            '    sys.stdout.flush()',
        ])
        return code

    def generate_code(self) -> None:
        # import json
        # self.logger.debug(json.dumps(self.ir.source, indent=2))
        self.logger.debug(self.ir.source)
        if self.is_entry_point:
            self.write_file_from_include_dir()
        self.write_enums()
        self.write_class()
        for t_val in self.ir.source["types"].values():
            # Recursively generate code for subtypes
            ir = IntermediateRepresentation(t_val, self.ir.entry_point_class_name)
            code_gen = Python3CodeGenerator(ir, self.output, is_entry_point=False)
            code_gen.generate_code()
        if self.is_entry_point:
            self.write_entry_point()
