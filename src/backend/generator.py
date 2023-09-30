from typing import Any, Callable, Union


class Generator:

    @staticmethod
    def gen_bytes_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_u1_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_u2_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_u2le_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_u2be_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_u4_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_u4le_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_u4be_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_u8_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_u8le_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_u8be_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_s1_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_s2_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_s2le_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_s2be_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_s4_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_s4le_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_s4be_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_s8_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_s8le_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_s8be_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_f4_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_f4le_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_f4be_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_f8_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_f8le_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_f8be_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_str_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    @staticmethod
    def gen_strz_fn(**kwargs: dict[str, Any]) -> str:
        raise NotImplementedError

    def generate_code(self) -> None:
        raise NotImplementedError

    @classmethod
    def get_gen_type_fn(cls, key: Union[str, None]) -> Callable[[dict[str, Any]], str]:
        TYPE_TO_FN_MAP = {
            None: cls.gen_bytes_fn,
            "u1": cls.gen_u1_fn,
            "u2": cls.gen_u2_fn,
            "u2le": cls.gen_u2le_fn,
            "u2be": cls.gen_u2be_fn,
            "u4": cls.gen_u4_fn,
            "u4le": cls.gen_u4le_fn,
            "u4be": cls.gen_u4be_fn,
            "u8": cls.gen_u8_fn,
            "u8le": cls.gen_u8le_fn,
            "u8be": cls.gen_u8be_fn,
            "s1": cls.gen_s1_fn,
            "s2": cls.gen_s2_fn,
            "s2le": cls.gen_s2le_fn,
            "s2be": cls.gen_s2be_fn,
            "s4": cls.gen_s4_fn,
            "s4le": cls.gen_s4le_fn,
            "s4be": cls.gen_s4be_fn,
            "s8": cls.gen_s8_fn,
            "s8le": cls.gen_s8le_fn,
            "s8be": cls.gen_s8be_fn,
            "f4": cls.gen_f4_fn,
            "f4be": cls.gen_f4be_fn,
            "f4le": cls.gen_f4le_fn,
            "f8": cls.gen_f8_fn,
            "f8be": cls.gen_f8be_fn,
            "f8le": cls.gen_f8le_fn,
            "str": cls.gen_str_fn,
            "strz": cls.gen_strz_fn,
        }
        return TYPE_TO_FN_MAP[key]
