import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer import LexerPython
from syntax import SyntaxAnalyzer, Program, SyntaxErrorCompilador


class TestFilesSyntax(unittest.TestCase):
    def read(self, name: str) -> str:
        return (ROOT / "tests" / "files" / name).read_text(encoding="utf-8")

    def test_valid_simple_parse(self):
        code = self.read("exemplo_valido.txt")
        tokens = LexerPython(code).get_tokens()
        ast = SyntaxAnalyzer(tokens).parse()
        self.assertIsInstance(ast, Program)
        self.assertGreaterEqual(len(ast.statements), 4)

    def test_corner_blank_lines_indent_parse(self):
        code = self.read("exemplo_linhas_em_branco.txt")
        tokens = LexerPython(code).get_tokens()
        ast = SyntaxAnalyzer(tokens).parse()
        self.assertIsInstance(ast, Program)
        self.assertGreaterEqual(len(ast.statements), 1)

    def test_invalid_syntax_missing_colon(self):
        code = self.read("exemplo_erro_sintatico.txt")
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador) as ctx:
            SyntaxAnalyzer(tokens).parse()
        # O erro deve estar na linha 2 (a linha com o if)
        self.assertEqual(ctx.exception.linha, 2)


if __name__ == "__main__":
    unittest.main()
