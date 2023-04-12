class Generator:

    KS_HELPER_INSTANCE = "self.ks_helper"

    @staticmethod
    def _get_ks_helper_fn_call(fn_name: str) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.{fn_name}"

    @staticmethod
    def gen_bytes_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes({kwargs.get('n_bytes')})"

    @staticmethod
    def gen_u1_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(1)"

    @staticmethod
    def gen_u2_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(2)"

    @staticmethod
    def gen_u2le_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(2)"

    @staticmethod
    def gen_u2be_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(2)"

    @staticmethod
    def gen_u4_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_u4le_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_u4be_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_u8_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_u8le_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_u8be_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_s1_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(1)"

    @staticmethod
    def gen_s2_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(2)"

    @staticmethod
    def gen_s2le_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(2)"

    @staticmethod
    def gen_s2be_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(2)"

    @staticmethod
    def gen_s4_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_s4le_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_s4be_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_s8_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_s8le_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_s8be_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_f4_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_f4le_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_f4be_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(4)"

    @staticmethod
    def gen_f8_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_f8le_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_f8be_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_bytes(8)"

    @staticmethod
    def gen_str_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_utf8({kwargs.get('n_bytes')})"

    @staticmethod
    def gen_strz_fn(**kwargs) -> str:
        return f"{Generator.KS_HELPER_INSTANCE}.rand_utf8({kwargs.get('n_bytes')}, \"\\0\")"

    def generate_code(self) -> None:
        raise NotImplementedError

    TYPE_TO_FN_MAP = {
        None: gen_bytes_fn,
        "u1": gen_u1_fn,
        "u2": gen_u2_fn,
        "u2le": gen_u2le_fn,
        "u2be": gen_u2be_fn,
        "u4": gen_u4_fn,
        "u4le": gen_u4le_fn,
        "u4be": gen_u4be_fn,
        "u8": gen_u8_fn,
        "u8le": gen_u8le_fn,
        "u8be": gen_u8be_fn,
        "s1": gen_s1_fn,
        "s2": gen_s2_fn,
        "s2le": gen_s2le_fn,
        "s2be": gen_s2be_fn,
        "s4": gen_s4_fn,
        "s4le": gen_s4le_fn,
        "s4be": gen_s4be_fn,
        "s8": gen_s8_fn,
        "s8le": gen_s8le_fn,
        "s8be": gen_s8be_fn,
        "f4": gen_f4_fn,
        "f4be": gen_f4be_fn,
        "f4le": gen_f4le_fn,
        "f8": gen_f8_fn,
        "f8be": gen_f8be_fn,
        "f8le": gen_f8le_fn,
        "str": gen_str_fn,
        "strz": gen_strz_fn,
    }
