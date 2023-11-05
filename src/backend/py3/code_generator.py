from datastructure.intermediate_representation import IntermediateRepresentation
from backend.generator import Generator
from backend.utils.indenter import Indenter
import backend.py3.utils.sanitiser as sanitiser
from utils.types import SeqEntry, VerboseEnumClassEntry, is_base_type
from utils.const import KEY_WITH_EXPRESSION, KEY_WITH_EXPRESSION_PRODUCE_BYTES, OPERATORS
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
    def _transpile_local_ref(class_name: str, available_ref: List[str], static_ref: List[str], expression: str) -> str:
        cleaned_expression = []
        for value in expression.split():
            instance = "self"
            if value in static_ref:
                instance = class_name
            if value in available_ref:
                cleaned_expression.append(f"{instance}.{value}")
            else:
                cleaned_expression.append(value)
        return " ".join(cleaned_expression)

    @classmethod
    def _transpile_local_ref_to_bytes(cls, class_name: str, available_ref: List[str], static_ref: List[str], expression: str) -> str:
        expression = cls._transpile_local_ref(class_name, available_ref, static_ref, expression)
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
    def _expression_transpiler(cls, class_name: str, available_ref: List[str], static_ref: List[str], expression: str, produce_bytes: bool = False) -> str:
        # Do not process anything other than string (int, list etc.)
        if not isinstance(expression, str):
            return expression
        result = []
        for expression_component in expression.split(" "):
            if expression_component in OPERATORS:
                result.append(expression_component)
                continue
            expression_component = cls._transpile_namespace(
                expression_component)
            if expression_component.startswith("_root") or expression_component.startswith("(_root"):
                expression_component = expression_component.replace(
                    "_root", "self._root", 1)
            elif expression_component.startswith("_parent") or expression_component.startswith("(_parent"):
                expression_component = expression_component.replace(
                    "_parent", "self._parent", 1)
            if produce_bytes:
                expression_component = cls._transpile_local_ref_to_bytes(
                    class_name, available_ref, static_ref, expression_component)
            else:
                expression_component = cls._transpile_local_ref(
                    class_name, available_ref, static_ref, expression_component)
            result.append(expression_component)
        # expression = cls._transpile_ternary(expression)
        return " ".join(result)

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
        instances_val = self.ir.source["instances"]
        available_ref = self.ir.source["_available_ref"]
        static_ref = self.ir.source["_static_ref"]
        dependency_graph = self.ir.source["_dependency_graph"]
        self.output.writelines(
            self.generate_class(meta_val, seq_val, instances_val, doc_val,
                                available_ref, static_ref, dependency_graph)
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

    def generate_class_static_var(self, seq: List[SeqEntry], class_name: str, instances: dict[dict[str, Any]], available_ref: List[str], static_ref: List[str]) -> List[str]:
        """Handle static variable for a type, such as those using `-fz-order`"""
        indenter = Indenter(add_newline=True)
        code = []
        # Handle seq entry
        for seq_entry in seq:
            generate_order = seq_entry.get("-fz-order")
            if generate_order is not None and len(generate_order) > 0:
                entry_name = seq_entry["id"]
                indenter.append_line(f"{entry_name} = {generate_order}", code)
            generate_random_order = seq_entry.get("-fz-random-order")
            if generate_random_order is not None and len(generate_random_order) > 0:
                entry_name = seq_entry["id"]
                indenter.append_line(
                    f"{entry_name} = {generate_random_order}", code)
        # Handle instances
        for instance_name, instance_entry in instances.items():
            if instance_entry["-fz-static"]:
                val = self._expression_transpiler(
                    class_name, available_ref, static_ref, instance_entry["value"])
                indenter.append_line(f"{instance_name} = {val}", code)
        code.append("")
        return code

    def generate_class_init_method(self, class_name: str, seq: List[SeqEntry], instances: dict[str, dict[str, Any]], available_ref: List[str], static_ref: List[str], dependency_graph: DependencyGraph) -> List[str]:
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
            instance_name = None
            instance_entry = None
            for entry in seq:
                if dependency_node.data == entry["id"]:
                    seq_entry = entry
                    break
            if seq_entry is None:
                for entry_name, entry in instances.items():
                    if dependency_node.data == entry_name:
                        instance_entry = entry
                        instance_name = entry_name
                        break
            if seq_entry is None and instance_entry is None:
                raise ValueError(
                    f"Invalid reference `{dependency_node.data}`.")
        # for seq_entry in seq:
            if seq_entry is not None:
                indenter.append_lines(self.generate_seq_entry(
                    class_name, seq_entry, available_ref, static_ref), code)
            if instance_entry is not None and not instance_entry["-fz-static"]:
                indenter.append_lines(self.generate_instance_entry(
                    class_name, instance_name, instance_entry, available_ref, static_ref), code)
        indenter.append_line("", code)
        return code

    def generate_seq_to_bytes_method(self, seq: List[SeqEntry]) -> List[str]:
        indenter = Indenter(add_newline=True)
        code = []
        for seq_entry in seq:
            enum_name = seq_entry.get("enum")
            process_key = seq_entry.get("process")
            entry_name = f"{seq_entry['id']}"  # FIXME sanitise name?
            indenter.append_lines(
                [f"def {entry_name}_to_bytes(self) -> bytes:"], code)
            indenter.indent()
            self_entry_name = f"self.{seq_entry['id']}"
            process_fn_prepend, process_fn_append = ("", "")
            if enum_name is not None:
                self_entry_name = f"{self_entry_name}.value"
            if process_key is not None:
                process_fn_prepend = f"{process_key}_("
                process_fn_append = ")"
            entry_type = seq_entry['type']
            match entry_type:
                case "u1":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('B', {self_entry_name}){process_fn_append}", code)
                case "u2le":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('<H', {self_entry_name}){process_fn_append}", code)
                case "u2be":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('>H', {self_entry_name}){process_fn_append}", code)
                case "u4le":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('<I', {self_entry_name}){process_fn_append}", code)
                case "u4be":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('>I', {self_entry_name}){process_fn_append}", code)
                case "u8le":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('<Q', {self_entry_name}){process_fn_append}", code)
                case "u8be":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('>Q', {self_entry_name}){process_fn_append}", code)
                case "s1":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('b', {self_entry_name}){process_fn_append}", code)
                case "s2le":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('<h', {self_entry_name}){process_fn_append}", code)
                case "s2be":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('>h', {self_entry_name}){process_fn_append}", code)
                case "s4le":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('<i', {self_entry_name}){process_fn_append}", code)
                case "s4be":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('>i', {self_entry_name}){process_fn_append}", code)
                case "s8le":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('<q', {self_entry_name}){process_fn_append}", code)
                case "s8be":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('>q', {self_entry_name}){process_fn_append}", code)
                case "f4le":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('<f', {self_entry_name}){process_fn_append}", code)
                case "f4be":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('>f', {self_entry_name}){process_fn_append}", code)
                case "f8le":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('<d', {self_entry_name}){process_fn_append}", code)
                case "f8be":
                    indenter.append_line(
                        f"return {process_fn_prepend}struct.pack('>d', {self_entry_name}){process_fn_append}", code)
                case "str" | "strz":
                    indenter.append_line(
                        f"return {process_fn_prepend}{self_entry_name}.encode(encoding=\"{seq_entry['encoding'].lower()}\"){process_fn_append}", code
                    )
                case None:
                    indenter.append_line(
                        f"return {process_fn_prepend}{self_entry_name}{process_fn_append}", code
                    )
                case _:
                    # Custom type
                    if "repeat" in seq_entry:
                        indenter.append_lines([
                            "result = b''",
                            f"for entry_instance in {self_entry_name}:",
                            "    result += entry_instance.result()",
                            f"return {process_fn_prepend}result{process_fn_append}",
                        ], code)
                    else:
                        indenter.append_line(
                            f"return {process_fn_prepend}{self_entry_name}.result(){process_fn_append}", code
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

    def generate_switch_type(self, assign_to: str, match_on: str, cases: dict[str, str]) -> List[str]:
        indenter = Indenter(add_newline=True)
        code = indenter.apply(f"match {match_on}:")
        indenter.indent()
        for match_value, type_name in cases.items():
            indenter.append_lines([
                f"case {self._transpile_namespace(match_value)}:",
                f"    {assign_to} = {self.type_code_generator.generate_code(type=type_name)}",
            ], code)
        return code

    def generate_class(self, meta: dict[str, Any], seq: List[SeqEntry], instances: dict[str, dict[str, Any]], doc: str, available_ref: List[str], static_ref: List[str], dependency_graph: DependencyGraph) -> List[str]:
        class_name = sanitiser.sanitise_class_name(meta["id"])
        self.logger.debug(f"Generating class \"{class_name}\"")
        indenter = Indenter(add_newline=True)
        code = indenter.apply([
            f"class {class_name}():",
        ])
        indenter.indent()
        if len(doc) > 0:
            indenter.append_lines(self.generate_doc(doc), code)
        indenter.append_lines(self.generate_class_static_var(
            seq, class_name, instances, available_ref, static_ref), code)
        indenter.append_lines(
            self.generate_class_init_method(class_name, seq, instances, available_ref, static_ref, dependency_graph), code)
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
            if "if" in seq_entry:
                # Expression already parsed when we generate data for the field, no need to parse again
                expression = seq_entry["if"]
                indenter.append_lines([
                    f"if {expression}:",
                    f"    self._io.append({to_bytes_fn})",
                ], code)
            else:
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

    def generate_seq_entry(self, class_name: str, seq_entry: SeqEntry, available_ref: List[str], static_ref: List[str]) -> List[str]:
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
                        class_name, available_ref, static_ref, seq_entry[key])
            for regex_key in KEY_WITH_EXPRESSION_PRODUCE_BYTES:
                if re.fullmatch(regex_key, key) is not None:
                    seq_entry[key] = self._expression_transpiler(
                        class_name, available_ref, static_ref, seq_entry[key], produce_bytes=True)
            if re.fullmatch(r"\-fz\-process\-.+", key):
                fz_process_key = key
        # Process expression in a `type` block
        if isinstance(seq_entry["type"], dict):
            type_block: dict = seq_entry["type"]
            for key in type_block.keys():
                for regex_key in KEY_WITH_EXPRESSION:
                    if re.fullmatch(regex_key, key) is not None:
                        type_block[key] = self._expression_transpiler(
                            class_name, available_ref, static_ref, type_block[key])
            if "switch-on" in type_block:
                new_cases = dict()
                for k, v in type_block["cases"].items():
                    new_cases[self._expression_transpiler(
                        class_name, available_ref, static_ref, k)] = v
                type_block["cases"] = new_cases

        if "if" in seq_entry:
            expression = seq_entry["if"]
            indenter.append_lines([
                f"if {expression}:",
            ], code)
            indenter.indent()
        if "-fz-attr-len" in seq_entry:
            expression = seq_entry["-fz-attr-len"]
            indenter.append_line(
                f"self.{entry_name} = len({expression})",
                code
            )
        elif "repeat" in seq_entry:
            indenter.append_line(
                f"self.{entry_name} = []",
                code
            )
            # Handle switch-on combined with repeat
            if isinstance(seq_entry["type"], dict):
                match_on = seq_entry["type"]["switch-on"]
                cases = seq_entry["type"]["cases"]
                code_to_initialise_object = ["_ = None"]
                code_to_initialise_object.extend(
                    self.generate_switch_type("_", match_on, cases))
            else:
                if is_base_type(seq_entry["type"]):
                    code_to_initialise_object = [
                        f"_ = {self.type_code_generator.generate_code(**seq_entry)}"
                    ]
                else:
                    seq_class_name = sanitiser.sanitise_class_name(
                        seq_entry["type"])
                    code_to_initialise_object = [
                        f"_ = {seq_class_name}(_parent=self, _root=self._root)"]
            repeat_type = seq_entry["repeat"]
            match repeat_type:
                case "until":
                    # loop_conditions = seq_entry["repeat-until"].replace("_io.eof", "self._io.is_eos()")
                    # Ignore eos/eof for now
                    loop_conditions = seq_entry["repeat-until"].replace(
                        "_io.eof", "False")
                    # Do while loop
                    do_while_loop_code = ["while True:"]
                    for line in code_to_initialise_object:
                        do_while_loop_code.append(f"    {line}")
                    do_while_loop_code.extend([
                        f"    self.{entry_name}.append(_)",
                        f"    if ({loop_conditions}):",
                        "        break",])
                    indenter.append_lines(do_while_loop_code, code)
                case "expr":
                    loop_conditions = f'int({seq_entry["repeat-expr"]})'
                    for_loop_code = [f"for _i in range({loop_conditions}):",]
                    for line in code_to_initialise_object:
                        for_loop_code.append(f"    {line}")
                    for_loop_code.extend([f"    self.{entry_name}.append(_)",])
                    indenter.append_lines(for_loop_code, code)
                case "eos":
                    min_n_loop = seq_entry.get("-fz-repeat-min")
                    min_n_loop = min_n_loop if min_n_loop is not None else 0
                    max_n_loop = seq_entry["-fz-repeat-max"]
                    for_loop_code = [
                        f'repeat_n_times = {self._ks_helper_fn_call("rand_int", start=min_n_loop, end=max_n_loop)}',
                        "for _i in range(repeat_n_times):",]
                    for line in code_to_initialise_object:
                        for_loop_code.append(f"    {line}")
                    for_loop_code.extend([f"    self.{entry_name}.append(_)",])
                    indenter.append_lines(for_loop_code, code)
                case _:
                    raise NotImplementedError("Unknown loop type")
        elif "-fz-random-order" in seq_entry:
            fn_name = "rand_int"
            end_val = f"(0 if (len({class_name}.{entry_name}) - 1) < 0 else (len({class_name}.{entry_name}) - 1))"
            indenter.append_line(
                f"self.{entry_name} = {class_name}.{entry_name}.pop({self._ks_helper_fn_call(fn_name, start=0, end=end_val)})",
                code
            )
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
                f"self.{entry_name}", match_on, cases), code)
        else:
            indenter.append_line(
                f"self.{entry_name} = {self.type_code_generator.generate_code(**seq_entry)}",
                code
            )
            fz_increment_step = seq_entry.get("-fz-increment-step")
            if fz_increment_step is not None:
                indenter.append_line(
                    f'{seq_entry["-fz-increment"]} += ({seq_entry["-fz-increment-step"]})', code)
        if "if" in seq_entry:
            indenter.unindent()
            indenter.append_lines([
                "else:",
                f"    self.{entry_name} = b''"
            ], code)
            indenter.indent()
        return code

    def generate_instance_entry(self, class_name: str, instance_name: str, instance_entry: dict[str, Any], available_ref: List[str], static_ref: List[str]) -> List[str]:
        self.logger.debug(f"Generating instance entry \"{instance_name}\"")
        indenter = Indenter(add_newline=True)
        code = []

        val = self._expression_transpiler(
            class_name, available_ref, static_ref, instance_entry["value"])
        indenter.append_line(f"self.{instance_name} = {val}", code)
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
            ir = IntermediateRepresentation(
                t_val, self.ir.entry_point_class_name)
            code_gen = Python3CodeGenerator(
                ir, self.output, is_entry_point=False)
            code_gen.generate_code()
        if self.is_entry_point:
            self.write_entry_point()
