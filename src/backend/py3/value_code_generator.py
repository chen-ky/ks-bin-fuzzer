from typing import Callable, Union, List, Optional
from utils import const
import backend.py3.utils.sanitiser as sanitiser


INT_TYPE = ("u1", "u2", "u2le", "u2be", "u4", "u4le", "u4be", "u8", "u8le",
            "u8be", "s1", "s2", "s2le", "s2be", "s4", "s4le", "s4be", "s8", "s8le", "s8be")
FLOAT_TYPE = ("f4", "f4le", "f4be", "f8", "f8le", "f8be")
STR_TYPE = ("str", "strz")
BYTE_TYPE = (None, )
ISO8859_TYPE = ("ISO8859-1", "ISO8859-2", "ISO8859-3", "ISO8859-4", "ISO8859-5", "ISO8859-6", "ISO8859-7",
                "ISO8859-8", "ISO8859-9", "ISO8859-10", "ISO8859-11", "ISO8859-13", "ISO8859-14", "ISO8859-15", "ISO8859-16")


class ValueCodeGenerator():

    def __init__(self, ks_helper_instance_name: str) -> None:
        self.ks_helper_instance_name = ks_helper_instance_name

    def _gen_bytes_fixed_contents(self, contents: str | List[Union[str, int]]) -> str:
        byte_val = b''
        for content in contents:
            if isinstance(content, str):
                byte_val += content.encode(encoding="utf8")
            elif isinstance(content, int):
                byte_val += content.to_bytes(1)
            else:
                raise TypeError("Unknown type in `contents` key")
        return f"{byte_val}"

    def gen_bytes_fn(self, n_bytes: int | str, contents: Optional[str | List[Union[str, int]]] = None) -> str:
        # Fixed bytes
        if contents is not None:
            return self._gen_bytes_fixed_contents(contents)

        # Generated bytes
        if isinstance(n_bytes, int):  # Not an expression
            if n_bytes < 0:
                raise ValueError("`n_bytes` cannot be less than 0")
            elif n_bytes == 0:
                return 'b\"\"'
        fn_name = "rand_bytes"
        fn_args = f"({n_bytes})"
        return f"{self.ks_helper_instance_name}.{fn_name}{fn_args}"

    def gen_u1_fn(self, start: int = const.u1_MIN, end: int = const.u1_MAX) -> str:
        if start < const.u1_MIN or end > const.u1_MAX:
            raise ValueError("Provided value is out of u1 range")
        fn_name = "rand_int"
        fn_args = f"({start}, {end})"
        return f"{self.ks_helper_instance_name}.{fn_name}{fn_args}"

    def gen_u2_fn(self, start: int = const.u2_MIN, end: int = const.u2_MAX) -> str:
        if start < const.u2_MIN or end > const.u2_MAX:
            raise ValueError("Provided value is out of u2 range")
        fn_name = "rand_int"
        fn_args = f"({start}, {end})"
        return f"{self.ks_helper_instance_name}.{fn_name}{fn_args}"

    def gen_u2le_fn(self, start: int = const.u2_MIN, end: int = const.u2_MAX) -> str:
        return self.gen_u2_fn(start=start, end=end)

    def gen_u2be_fn(self, start: int = const.u2_MIN, end: int = const.u2_MAX) -> str:
        return self.gen_u2_fn(start=start, end=end)

    def gen_u4_fn(self, start: int = const.u4_MIN, end: int = const.u4_MAX) -> str:
        if start < const.u4_MIN or end > const.u4_MAX:
            raise ValueError("Provided value is out of u4 range")
        fn_name = "rand_int"
        fn_args = f"({start}, {end})"
        return f"{self.ks_helper_instance_name}.{fn_name}{fn_args}"

    def gen_u4le_fn(self, start: int = const.u4_MIN, end: int = const.u4_MAX) -> str:
        return self.gen_u4_fn(start=start, end=end)

    def gen_u4be_fn(self, start: int = const.u4_MIN, end: int = const.u4_MAX) -> str:
        return self.gen_u4_fn(start=start, end=end)

    def gen_u8_fn(self, start: int = const.u8_MIN, end: int = const.u8_MAX) -> str:
        if start < const.u8_MIN or end > const.u8_MAX:
            raise ValueError("Provided value is out of u8 range")
        fn_name = "rand_int"
        fn_args = f"({start}, {end})"
        return f"{self.ks_helper_instance_name}.{fn_name}{fn_args}"

    def gen_u8le_fn(self, start: int = const.u8_MIN, end: int = const.u8_MAX) -> str:
        return self.gen_u8_fn(start=start, end=end)

    def gen_u8be_fn(self, start: int = const.u8_MIN, end: int = const.u8_MAX) -> str:
        return self.gen_u8_fn(start=start, end=end)

    def gen_s1_fn(self, start: int = const.s1_MIN, end: int = const.s1_MAX) -> str:
        if start < const.s1_MIN or end > const.s1_MAX:
            raise ValueError("Provided value is out of s1 range")
        fn_name = "rand_int"
        fn_args = f"({start}, {end})"
        return f"{self.ks_helper_instance_name}.{fn_name}{fn_args}"

    def gen_s2_fn(self, start: int = const.s2_MIN, end: int = const.s2_MAX) -> str:
        if start < const.s2_MIN or end > const.s2_MAX:
            raise ValueError("Provided value is out of s2 range")
        fn_name = "rand_int"
        fn_args = f"({start}, {end})"
        return f"{self.ks_helper_instance_name}.{fn_name}{fn_args}"

    def gen_s2le_fn(self, start: int = const.s2_MIN, end: int = const.s2_MAX) -> str:
        return self.gen_s2_fn(start=start, end=end)

    def gen_s2be_fn(self, start: int = const.s2_MIN, end: int = const.s2_MAX) -> str:
        return self.gen_s2_fn(start=start, end=end)

    def gen_s4_fn(self, start: int = const.s4_MIN, end: int = const.s4_MAX) -> str:
        if start < const.s4_MIN or end > const.s4_MAX:
            raise ValueError("Provided value is out of s4 range")
        fn_name = "rand_int"
        fn_args = f"({start}, {end})"
        return f"{self.ks_helper_instance_name}.{fn_name}{fn_args}"

    def gen_s4le_fn(self, start: int = const.s4_MIN, end: int = const.s4_MAX) -> str:
        return self.gen_s4_fn(start=start, end=end)

    def gen_s4be_fn(self, start: int = const.s4_MIN, end: int = const.s4_MAX) -> str:
        return self.gen_s4_fn(start=start, end=end)

    def gen_s8_fn(self, start: int = const.s8_MIN, end: int = const.s8_MAX) -> str:
        if start < const.s8_MIN or end > const.s8_MAX:
            raise ValueError("Provided value is out of s8 range")
        fn_name = "rand_int"
        fn_args = f"({start}, {end})"
        return f"{self.ks_helper_instance_name}.{fn_name}{fn_args}"

    def gen_s8le_fn(self, start: int = const.s8_MIN, end: int = const.s8_MAX) -> str:
        return self.gen_s8_fn(start=start, end=end)

    def gen_s8be_fn(self, start: int = const.s8_MIN, end: int = const.s8_MAX) -> str:
        return self.gen_s8_fn(start=start, end=end)

    def gen_f4_fn(self, start: float = const.f4_MIN, end: float = const.f4_MAX) -> str:
        # TODO Does not actually support range generation
        if start < const.f4_MIN or end > const.f4_MAX:
            raise ValueError("Provided value is out of f4 range")
        fn_name = "rand_float"
        fn_args = "()"
        return f"{self.ks_helper_instance_name}.{fn_name}{fn_args}"

    def gen_f4le_fn(self, start: float = const.f4_MIN, end: float = const.f4_MAX) -> str:
        return self.gen_f4_fn(start=start, end=end)

    def gen_f4be_fn(self, start: float = const.f4_MIN, end: float = const.f4_MAX) -> str:
        return self.gen_f4_fn(start=start, end=end)

    def gen_f8_fn(self, start: float = const.f8_MIN, end: float = const.f8_MAX) -> str:
        # TODO Does not actually support range generation
        if start < const.f8_MIN or end > const.f8_MAX:
            raise ValueError("Provided value is out of f8 range")
        fn_name = "rand_double"
        fn_args = "()"
        return f"{self.ks_helper_instance_name}.{fn_name}{fn_args}"

    def gen_f8le_fn(self, start: float = const.f8_MIN, end: float = const.f8_MAX) -> str:
        return self.gen_f8_fn(start=start, end=end)

    def gen_f8be_fn(self, start: float = const.f8_MIN, end: float = const.f8_MAX) -> str:
        return self.gen_f8_fn(start=start, end=end)

    def gen_str_fn(self, n_bytes: int, encoding: Optional[str] = "UTF-8", terminator: Optional[int] = None) -> str:
        if isinstance(n_bytes, int):  # Not an expression
            if n_bytes <= 0:
                raise ValueError("`n_bytes` cannot be less than or equal to 0")
            elif terminator is not None and (terminator < 0 or terminator > 255):
                raise ValueError("`terminator` must be between 0 and 255")
        encoding = encoding.upper()
        fn_name = None
        fn_args = f"({n_bytes}"
        terminator = None if terminator is None else terminator.to_bytes(1)
        if encoding == "UTF-8":
            fn_name = "rand_utf8"
            fn_args += f", {terminator})"
        elif encoding == "ASCII":
            fn_name = "rand_ascii"
            fn_args += f", {terminator})"
        elif encoding in ISO8859_TYPE:
            fn_name = "rand_iso8859"
            fn_args += f", \"{encoding}\", {terminator})"
        if fn_name is None:
            raise ValueError("Unknown string encoding")
        return f"{self.ks_helper_instance_name}.{fn_name}{fn_args}"

    def gen_strz_fn(self, n_bytes: int, encoding: Optional[str] = "UTF-8", terminator: None = None) -> str:
        return self.gen_str_fn(n_bytes=n_bytes, encoding=encoding, terminator=0)

    def gen_enum_fn(self, enum_name: str):
        fn_name = "rand_choice"
        fn_args = f"(list({sanitiser.sanitise_class_name(enum_name)}))"
        return f"{self.ks_helper_instance_name}.{fn_name}{fn_args}"

    def gen_custom_type(self, type_name: str):
        type_name = sanitiser.sanitise_class_name(type_name)
        return f"{type_name}(_parent=self, _root=self._root)"

    def generate_code(self, **kwargs) -> str:
        seq_type = kwargs["type"]
        gen_fn = self.get_gen_type_fn(seq_type)
        if seq_type in INT_TYPE:
            if kwargs.get("valid") is not None:
                return f"{kwargs['valid']}"
            enum_name = kwargs.get("enum")  # Enum type can only be int
            if enum_name is not None:
                return self.gen_enum_fn(enum_name)
            return gen_fn(start=kwargs["-fz-range-min"], end=kwargs["-fz-range-max"])
        elif seq_type in FLOAT_TYPE:
            if kwargs.get("valid") is not None:
                return f"{kwargs['valid']}"
            return gen_fn(start=kwargs["-fz-range-min"], end=kwargs["-fz-range-max"])
        elif seq_type in BYTE_TYPE:
            return gen_fn(n_bytes=kwargs["size"], contents=kwargs["contents"])
        elif seq_type in STR_TYPE:
            return gen_fn(n_bytes=kwargs["size"], encoding=kwargs["encoding"], terminator=kwargs["terminator"])
        else:
            # Not a base type
            return self.gen_custom_type(seq_type)

    def get_gen_type_fn(self, key: Union[str, None]) -> Optional[Callable[..., str]]:
        TYPE_TO_FN_MAP = {
            None: self.gen_bytes_fn,
            "u1": self.gen_u1_fn,
            "u2": self.gen_u2_fn,
            "u2le": self.gen_u2le_fn,
            "u2be": self.gen_u2be_fn,
            "u4": self.gen_u4_fn,
            "u4le": self.gen_u4le_fn,
            "u4be": self.gen_u4be_fn,
            "u8": self.gen_u8_fn,
            "u8le": self.gen_u8le_fn,
            "u8be": self.gen_u8be_fn,
            "s1": self.gen_s1_fn,
            "s2": self.gen_s2_fn,
            "s2le": self.gen_s2le_fn,
            "s2be": self.gen_s2be_fn,
            "s4": self.gen_s4_fn,
            "s4le": self.gen_s4le_fn,
            "s4be": self.gen_s4be_fn,
            "s8": self.gen_s8_fn,
            "s8le": self.gen_s8le_fn,
            "s8be": self.gen_s8be_fn,
            "f4": self.gen_f4_fn,
            "f4be": self.gen_f4be_fn,
            "f4le": self.gen_f4le_fn,
            "f8": self.gen_f8_fn,
            "f8be": self.gen_f8be_fn,
            "f8le": self.gen_f8le_fn,
            "str": self.gen_str_fn,
            "strz": self.gen_strz_fn,
        }
        return TYPE_TO_FN_MAP.get(key)
