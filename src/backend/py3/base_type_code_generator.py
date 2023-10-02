from typing import Callable, Union
from utils import const


class BaseTypeCodeGenerator():

    def __init__(self, ks_helper_instance_name: str) -> None:
        self.ks_helper_instance_name = ks_helper_instance_name

    def gen_bytes_fn(self, n_bytes: int) -> str:
        if n_bytes <= 0:
            raise ValueError("`n_bytes` cannot be less than or equal to 0")
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

    @staticmethod
    def gen_f4_fn(self, start: int = 0, end: int = 4294967295) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_f4le_fn(self, start: int = 0, end: int = 4294967295) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_f4be_fn(self, start: int = 0, end: int = 4294967295) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_f8_fn(self, start: int = 0, end: int = 4294967295) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_f8le_fn(self, start: int = 0, end: int = 4294967295) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_f8be_fn(self, start: int = 0, end: int = 4294967295) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_str_fn(**kwargs) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_strz_fn(**kwargs) -> str:
        raise NotImplementedError

    def generate_code(self) -> str:
        raise NotImplementedError

    def get_gen_type_fn(self, key: Union[str, None]) -> Callable[..., str]:
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
        return TYPE_TO_FN_MAP[key]
