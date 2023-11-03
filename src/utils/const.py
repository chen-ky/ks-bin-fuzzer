import math


u1_MIN, u1_MAX = 0, 255
u2_MIN, u2_MAX = 0, 65535
u4_MIN, u4_MAX = 0, 4294967295
u8_MIN, u8_MAX = 0, 18446744073709551615
s1_MIN, s1_MAX = -128, 127
s2_MIN, s2_MAX = -32768, 32767
s4_MIN, s4_MAX = -2147483648, 2147483647
s8_MIN, s8_MAX = -9223372036854775808, 9223372036854775807

f4_MIN, f4_MAX = -math.inf, math.inf
f8_MIN, f8_MAX = -math.inf, math.inf

ARITHMETIC_OPERATORS = ("+", "-", "*", "/", "%")
STRING_OPERATORS = ("+", )
RELATIONAL_OPERATORS = ("<", "<=", ">", ">=", "==", "!=")
BITWISE_OPERATORS = ("<<", ">>", "&", "|", "^")
LOGICAL_OPERATORS = ("not", "and", "or")
OPERATORS = tuple(set().union(ARITHMETIC_OPERATORS, STRING_OPERATORS,
                              RELATIONAL_OPERATORS, BITWISE_OPERATORS, LOGICAL_OPERATORS))

VALID_PROCESS_KEY_VALUE = ["zlib"]

KEY_WITH_EXPRESSION = ["size", "switch-on", "repeat-expr", "valid", "value"]
KEY_WITH_EXPRESSION_PRODUCE_BYTES = [r"\-fz\-process\-.+", "-fz-attr-len"]
