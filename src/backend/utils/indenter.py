from typing import List


class Indenter():

    def __init__(self, indentation: int = 4, indent_char: str = " ", add_newline: bool = False) -> None:
        if indentation < 0:
            indentation = 0
        self.indentation = indentation
        self.indent_char = indent_char
        self.indent_level = 0
        self.add_newline = add_newline

    def reset(self):
        self.indent_level = 0

    def indent(self, add_indent: int = 1):
        if add_indent < 0:
            raise ValueError("`add_indent` cannot be smaller than 0")
        self.indent_level += add_indent

    def unindent(self, remove_indent: int = 1):
        if remove_indent < 0:
            raise ValueError("`remove_indent` cannot be smaller than 0")
        if self.indent_level > 0:
            self.indent_level -= remove_indent

    def append_line(self, line: str, text: List[str]) -> List[str]:
        text.append(self.apply_to_line(line))
        return text

    def apply_to_line(self, line: str) -> str:
        line = self.indent_char * (self.indentation * self.indent_level) + line
        if self.add_newline and not line.endswith("\n"):
            line += "\n"
        return line

    def apply(self, text: str | List[str]) -> List[str]:
        if isinstance(text, str):
            text = text.splitlines()
        for line_num, line in enumerate(text):
            text[line_num] = self.apply_to_line(line)
        return text
