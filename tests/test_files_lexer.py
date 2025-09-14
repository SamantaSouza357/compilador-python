import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer import LexerPython, TokenType, LexicalError


class TestFilesLexer(unittest.TestCase):
    def read(self, name: str) -> str:
        return (ROOT / "tests" / "files" / name).read_text(encoding="utf-8")

    def test_valid_simple_tokens(self):
        code = self.read("exemplo_valido.txt")
        tokens = LexerPython(code).get_tokens()
        # Ensure we got EOF and at least one INDENT/DEDENT for function
        kinds = [t.tipo for t in tokens]
        self.assertIn(TokenType.INDENT, kinds)
        self.assertIn(TokenType.DEDENT, kinds)
        self.assertEqual(tokens[-1].tipo, TokenType.EOF)

    def test_corner_blank_lines_indent_tokens(self):
        code = self.read("exemplo_linhas_em_branco.txt")
        tokens = LexerPython(code).get_tokens()
        # Should not raise and should close indentation properly
        self.assertEqual(tokens[-1].tipo, TokenType.EOF)

    def test_invalid_lexical_unexpected_char(self):
        code = self.read("exemplo_erro_lexico.txt")
        with self.assertRaises(LexicalError) as ctx:
            LexerPython(code).get_tokens()
        msg = str(ctx.exception)
        self.assertIn("Erro léxico na linha 2", msg)
        self.assertIn("caractere inesperado", msg)


if __name__ == "__main__":
    unittest.main()
