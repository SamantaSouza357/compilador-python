import unittest
from pathlib import Path
import sys

# Configura caminho para importar src/
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer import LexerPython
from syntax import SyntaxAnalyzer, SyntaxErrorCompilador


class TestSyntaxErrors(unittest.TestCase):
    def test_missing_colon_in_if(self):
        """Falta de ':' em if deve gerar SyntaxErrorCompilador."""
        code = (
            "def f():\n"
            "    if x>y\n"
            "        return x\n"
        )
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador):
            SyntaxAnalyzer(tokens).parse()

    def test_missing_indent_after_def(self):
        """Falta de indentação após 'def' deve gerar erro sintático."""
        code = (
            "def f():\n"
            "pass\n"
        )
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador):
            SyntaxAnalyzer(tokens).parse()

    def test_missing_function_name(self):
        """'def' sem nome de função deve gerar erro sintático."""
        code = (
            "def (x):\n"
            "    return x\n"
        )
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador):
            SyntaxAnalyzer(tokens).parse()

    def test_return_without_expression(self):
        """return sem expressão deve ser aceito, mas expr=None."""
        code = (
            "def f():\n"
            "    return\n"
        )
        tokens = LexerPython(code).get_tokens()
        ast = SyntaxAnalyzer(tokens).parse()

        func = ast.statements[0]
        self.assertEqual(func.name, "f")
        self.assertTrue(hasattr(func.body, "statements"))
        self.assertGreaterEqual(len(func.body.statements), 1)

        ret = func.body.statements[0]
        self.assertTrue(hasattr(ret, "expr"))
        self.assertIsNone(ret.expr)

    def test_else_without_if(self):
        """else fora de um if deve gerar SyntaxErrorCompilador."""
        code = (
            "else:\n"
            "    x=1\n"
        )
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador):
            SyntaxAnalyzer(tokens).parse()


if __name__ == "__main__":
    unittest.main()