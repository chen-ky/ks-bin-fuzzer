from generator import Generator
import string

TYPE_TO_FN_MAP = {
    "u1": "self.ks_helper.rand_bytes(1)", 
    "u2": "self.ks_helper.rand_bytes(2)",
    "u2le": "self.ks_helper.rand_bytes(2)",
    "u2be": "self.ks_helper.rand_bytes(2)",
    "u4": "self.ks_helper.rand_bytes(4)",
    "u4le": "self.ks_helper.rand_bytes(4)",
    "u4be": "self.ks_helper.rand_bytes(4)",
    "u8": "self.ks_helper.rand_bytes(8)",
    "u8le": "self.ks_helper.rand_bytes(8)",
    "u8be": "self.ks_helper.rand_bytes(8)",
    "s1": "self.ks_helper.rand_bytes(1)",
    "s2": "self.ks_helper.rand_bytes(2)",
    "s2le": "self.ks_helper.rand_bytes(2)",
    "s2be": "self.ks_helper.rand_bytes(2)",
    "s4": "self.ks_helper.rand_bytes(4)",
    "s4le": "self.ks_helper.rand_bytes(4)",
    "s4be": "self.ks_helper.rand_bytes(4)",
    "s8": "self.ks_helper.rand_bytes(8)",
    "s8le": "self.ks_helper.rand_bytes(8)",
    "s8be": "self.ks_helper.rand_bytes(8)",
    "f4": "self.ks_helper.rand_bytes(4)",
    "f4be": "self.ks_helper.rand_bytes(4)",
    "f4le": "self.ks_helper.rand_bytes(4)",
    "f8": "self.ks_helper.rand_bytes(8)",
    "f8be": "self.ks_helper.rand_bytes(8)",
    "f8le": "self.ks_helper.rand_bytes(8)",
    # "str": "self.ks_helper.rand_utf8(24)",
    # "strz": "", // TODO
}

KS_HELPER_SRC_PATH = "include/py3/ks_helper.py"


class Python3Generator(Generator):

    def __init__(self, class_name: str, seq: list[dict[str, any]]) -> None:
        # super().__init__()
        self.class_name = Python3Generator._sanitise_class_name(class_name)
        self.seq = seq
        with open(KS_HELPER_SRC_PATH, "r") as f:
            self.ks_helper_src = f.read()

    @staticmethod
    def _sanitise_class_name(class_name: str) -> str:
        result = class_name.title()
        to_remove_chars = string.punctuation + string.whitespace
        for c in to_remove_chars:
            result = result.replace(c, "")
        result += "_"
        return result

    @staticmethod
    def _sanitise_fn_name(fn_name: str) -> str:
        result = fn_name.lower()
        to_remove_chars = string.punctuation.replace("_", "") + string.whitespace
        for c in to_remove_chars:
            result = result.replace(c, "")
        result += "_"
        return result

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
        result = """    def generate(self):
        return ("""
        first_entry = True
        for entry in self.seq:
            fn_name = Python3Generator._sanitise_fn_name(entry["id"])
            if first_entry:
                result += f"self.gen_{fn_name}()\n"
                first_entry = False
            else:
                result += f"        + self.gen_{fn_name}()\n"
        result += "        )"
        return result

    def generate_fns(self) -> str:
        result = ""
        for entry in self.seq:
            data_type = entry["type"] if "type" in entry else None
            sz = None
            if data_type is None:
                sz = int(entry["size"])
            elif data_type == "str":
                sz = int(entry["size"])
            elif data_type == "strz":
                sz = int(entry["size"]) - 1
            fn_name = f"gen_{Python3Generator._sanitise_fn_name(entry['id'])}"
            result += f"    def {fn_name}(self):\n"
            if data_type is None:
                result += f"        return self.ks_helper.rand_bytes({sz})\n\n"
            elif data_type == "str":
                result += f"        return self.ks_helper.rand_utf8({sz})\n\n"
            elif data_type == "strz":
                result += f"        return self.ks_helper.rand_utf8({sz}) + b'\\0'\n\n"
            else:
                result += f"        return {TYPE_TO_FN_MAP[data_type]}\n\n"

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
