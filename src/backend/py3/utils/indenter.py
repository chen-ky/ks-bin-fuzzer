from typing import List


class Indenter():

    def __init__(self, indentation: int = 4, indent_char: str = " ") -> None:
        if indentation < 0:
            indentation = 0
        self.indentation = indentation
        self.indent_char = indent_char
        self.indent_level = 0

    def reset(self):
        self.indent_level = 0

    def indent(self):
        self.indent_level += 1

    def unindent(self):
        if self.indent_level > 0:
            self.indent_level -= 1

    def apply(self, text: str | List[str]) -> List[str]:
        if isinstance(text, str):
            text = text.splitlines()
        for line_num, line in enumerate(text):
            text[line_num] = self.indent_char * (self.indentation * self.indent_level) + line
        return text
