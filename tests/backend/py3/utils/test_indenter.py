import unittest
from src.backend.py3.utils.indenter import Indenter


class IndenterTest(unittest.TestCase):
    def test_no_indent_str(self):
        indenter = Indenter(indentation=4, indent_char=" ")
        expected_output = ["test str", "another one"]
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)

    def test_increase_indentation(self):
        indenter = Indenter(indentation=4, indent_char=" ")
        expected_output = ["test str", "another one"]
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)
        indenter.indent()
        expected_output = ["    test str", "    another one"]
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)

    def test_decrease_indentation(self):
        indenter = Indenter(indentation=4, indent_char=" ")
        indenter.indent()
        expected_output = ["    test str", "    another one"]
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)
        indenter.unindent()
        expected_output = ["test str", "another one"]
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)

    def test_unindent_on_zero_indent(self):
        indenter = Indenter(indentation=4, indent_char=" ")
        indenter.unindent()
        expected_output = ["test str", "another one"]
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)

    def test_zero_indentation(self):
        indenter = Indenter(indentation=0, indent_char=" ")
        indenter.indent()
        expected_output = ["test str", "another one"]
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)

    def test_negative_indentation(self):
        indenter = Indenter(indentation=-1, indent_char=" ")
        expected_output = ["test str", "another one"]
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)
        indenter.indent()
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)

    def test_custom_indent_char(self):
        indenter = Indenter(indentation=1, indent_char="\t")
        expected_output = ["test str", "another one"]
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)
        indenter.indent()
        expected_output = ["\ttest str", "\tanother one"]
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)

    def test_crlf(self):
        indenter = Indenter(indentation=1, indent_char="\t")
        expected_output = ["test str", "another one"]
        result = indenter.apply("test str\r\nanother one")
        self.assertEqual(result, expected_output)
        indenter.indent()
        expected_output = ["\ttest str", "\tanother one"]
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)

    def test_multiple_level_indent(self):
        indenter = Indenter(indentation=1, indent_char="\t")
        expected_output = ["test str", "another one"]
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)
        indenter.indent()
        expected_output = ["\ttest str", "\tanother one"]
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)
        indenter.indent()
        expected_output = ["\t\ttest str", "\t\tanother one"]
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)
        indenter.unindent()
        expected_output = ["\ttest str", "\tanother one"]
        result = indenter.apply("test str\nanother one")
        self.assertEqual(result, expected_output)
