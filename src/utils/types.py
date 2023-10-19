from typing import Any, TypeAlias, Literal


# UnsignedInt: TypeAlias = Literal["u1", "u2", "u2le", "u2be", "u4", "u4le", "u4be", "u8", "u8le", "u8be"]
VALID_INT_TYPE_VAL = ["u1", "u2", "u2le", "u2be", "u4", "u4le", "u4be", "u8", "u8le",
                      "u8be", "s1", "s2", "s2le", "s2be", "s4", "s4le", "s4be", "s8", "s8le", "s8be"]
VALID_FLOAT_TYPE_VAL = ["f4", "f4le", "f4be", "f8", "f8le", "f8be"]
VALID_STR_TYPE_VAL = ["str", "strz"]
VALID_BYTE_TYPE_VAL = [None, ]
VALID_BASE_TYPE_VAL = list(VALID_INT_TYPE_VAL)
VALID_BASE_TYPE_VAL.extend(VALID_FLOAT_TYPE_VAL)
VALID_BASE_TYPE_VAL.extend(VALID_STR_TYPE_VAL)
VALID_BASE_TYPE_VAL.extend(VALID_BYTE_TYPE_VAL)

BaseObject: TypeAlias = dict[str, Any]
SeqEntry: TypeAlias = dict[str, Any]
EnumClassEntry: TypeAlias = dict[int, str]
VerboseEnumClassEntry: TypeAlias = dict[int, dict[str, str]]
