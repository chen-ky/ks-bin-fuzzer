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
# METHODS=("to_s", "to_i", "length")

# re.split(r"[ \-\+\*/]", "asdf + atr-aghf*sdf/dasf".replace(string.whitespace, ""))
# "asdf + atr-aghf*sdf/dasf".replace(string.whitespace, "")
# a="asdf + atr-aghf*sdf/dasf"
# a.replace(" ", "")
# re.sub.__doc__
# a.split()
# "".join(a.split())
# a
# a="asdf + atr\t -        aghf\r\n*sdf/dasf"
# "".join(a.split())
