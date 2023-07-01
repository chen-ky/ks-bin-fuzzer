from backend.generator import Generator
import string
from typing import Any
import os


KS_HELPER_SRC_PATH = os.path.join(os.path.dirname(__file__), "include", "py3", "ks_helper.py")


class Python3Generator(Generator):

    KS_HELPER_INSTANCE = "self.ks_helper"

    def __init__(self, class_name: str, seq: list[dict[str, any]]) -> None:
        # super().__init__()
        self.class_name = Python3Generator._sanitise_class_name(class_name)
        self.seq = seq
        with open(KS_HELPER_SRC_PATH, "r") as f:
            self.ks_helper_src = f.read()

    @staticmethod
    def gen_bytes_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes({kwargs.get('n_bytes')})"

    @staticmethod
    def gen_u1_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(1)"

    @staticmethod
    def gen_u2_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(2)"

    @staticmethod
    def gen_u2le_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(2)"

    @staticmethod
    def gen_u2be_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(2)"

    @staticmethod
    def gen_u4_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_u4le_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_u4be_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_u8_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_u8le_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_u8be_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_s1_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(1)"

    @staticmethod
    def gen_s2_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(2)"

    @staticmethod
    def gen_s2le_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(2)"

    @staticmethod
    def gen_s2be_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(2)"

    @staticmethod
    def gen_s4_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_s4le_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_s4be_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_s8_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_s8le_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_s8be_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_f4_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_f4le_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_f4be_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_f8_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_f8le_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_f8be_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_str_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_utf8({kwargs.get('n_bytes')})"

    @staticmethod
    def gen_strz_fn(**kwargs: dict[str, Any]) -> str:
        return f"{Python3Generator.KS_HELPER_INSTANCE}.rand_utf8({kwargs.get('n_bytes')}, \"\\0\")"

    @staticmethod
    def _sanitise_class_name(class_name: str) -> str:
        """
        Clean provided string to be used as class name. Will remove
        whitespace, punctuations (excluding `_`) and convert the name to 
        titlecase.

        :param class_name: String to sanitise
        :returns: Cleaned string with `_` appended (to prevent Python name
        collision)
        """
        result = class_name.title()
        to_remove_chars = string.punctuation + string.whitespace
        for c in to_remove_chars:
            result = result.replace(c, "")
        result += "_"
        return result

    @staticmethod
    def _sanitise_fn_name(fn_name: str) -> str:
        """
        Clean provided string to be used as function name. Will remove
        whitespace, punctuations (excluding `_`) and convert the name to 
        lowercase.

        :param fn_name: String to sanitise
        :returns: Cleaned string with `_` appended (to prevent Python name
        collision)
        """
        result = fn_name.lower()
        to_remove_chars = string.punctuation.replace(
            "_", "") + string.whitespace
        for c in to_remove_chars:
            result = result.replace(c, "")
        result += "_"
        return result

    def _handle_attribute(self, attribute: dict[str, Any]) -> str:
        entry_id = attribute["id"]
        fn_name = f"gen_{Python3Generator._sanitise_fn_name(entry_id)}"
        result = f"    def {fn_name}(self):\n"
        if attribute.__contains__("contents"):
            result += self._handle_contents_key(attribute)
            result += "\n\n"
        else:
            data_type = attribute["type"] if "type" in attribute else None
            sz = None
            if data_type is None or data_type == "str" or data_type == "strz":
                sz = int(attribute["size"])
                # TODO check sz greater than 0, terminator can fit in sz
            result += f"        return {self.get_gen_type_fn(data_type)(n_bytes = sz)}\n\n"
        return result

    def _handle_contents_key(self, attribute: dict[str, Any]) -> str:
        contents = attribute["contents"]
        if not (isinstance(contents, str) or isinstance(contents, list)):
            raise TypeError(
                "`contents` key accepts UTF-8 string or array type only.")
        b_arr = []
        for idx, elem in enumerate(contents):
            if isinstance(elem, str):
                b_arr.extend(elem.encode(encoding="utf-8"))
            elif isinstance(elem, int):
                if elem > 0xFF or elem < 0:
                    raise ValueError(
                        f"Out of range byte value at index {idx}.")
                b_arr.append(elem)
            else:
                raise TypeError(
                    f"`contents` key contain an invalid type at index {idx}.")
        return f"        return {bytes(b_arr)}"

    def imports(self) -> str:
        imports_statements = """import sys
        """
        return imports_statements

    def constants(self) -> str:
        const = ""
        return const

    def ks_helper_class(self) -> str:
        return self.ks_helper_src

    def seq_class(self) -> str:
        return """class %s:
    def __init__(self):
        self.ks_helper = KsHelper()
        """ % self.class_name

    def generate_fn(self) -> str:
        """
        Generate the function calls required to produce the binary format.
        """
        result = """    def generate(self):
        return ("""
        first_entry = True
        for entry in self.seq:
            fn_name = Python3Generator._sanitise_fn_name(entry["id"])
            if first_entry:
                result += f"self.gen_{fn_name}()\n"
                first_entry = False
            else:
                result += f"                + self.gen_{fn_name}()\n"
        result += "                )\n"
        return result

    def generate_fns(self) -> str:
        """
        Generate the functions required to help produce the binary format.
        """
        result = ""
        for attribute in self.seq:
            result += self._handle_attribute(attribute)
        return result

    def generate_entry_point(self):
        return """if "__main__" == __name__:
    record = %s()
    sys.stdout.buffer.write(record.generate())
    sys.stdout.flush()""" % self.class_name

    def generate_code(self) -> None:
        print(self.ks_helper_class())
        print(self.imports())
        print(self.constants())
        print(self.seq_class())
        print(self.generate_fn())
        print(self.generate_fns())
        print(self.generate_entry_point())
