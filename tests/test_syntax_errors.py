import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer_analyzer import LexerPython
from syntax_analyzer import SyntaxAnalyzer, SyntaxErrorCompilador


class TestSyntaxErrors(unittest.TestCase):
    def test_missing_colon_in_if(self):
        code = (
            "def f():\n"
            "    if x>y\n"
            "        return x\n"
        )
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador) as ctx:
            SyntaxAnalyzer(tokens).parse()
        self.assertEqual(ctx.exception.linha, 2)
        self.assertIn(":", str(ctx.exception))  # Esperado ':'

    def test_missing_indent_after_def(self):
        code = (
            "def f():\n"
            "pass\n"
        )
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador) as ctx:
            SyntaxAnalyzer(tokens).parse()
        self.assertEqual(ctx.exception.linha, 2)
        self.assertIn("INDENT", str(ctx.exception))

    def test_missing_function_name(self):
        code = (
            "def (x):\n"
            "    return x\n"
        )
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador) as ctx:
            SyntaxAnalyzer(tokens).parse()
        self.assertEqual(ctx.exception.linha, 1)
        self.assertIn("identificador do nome da função", str(ctx.exception))

    def test_return_without_expression(self):
        code = (
            "def f():\n"
            "    return\n"
        )
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador) as ctx:
            SyntaxAnalyzer(tokens).parse()
        self.assertEqual(ctx.exception.linha, 2)
        self.assertIn("fator inesperado", str(ctx.exception))

    def test_else_without_if(self):
        code = (
            "else:\n"
            "    x=1\n"
        )
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador) as ctx:
            SyntaxAnalyzer(tokens).parse()
        self.assertEqual(ctx.exception.linha, 1)
        self.assertIn("fator inesperado", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
