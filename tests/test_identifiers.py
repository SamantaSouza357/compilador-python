import unittest
from pathlib import Path
import sys

# Ensure `src` is importable
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer import LexerPython, TokenType


class TestIdentifiers(unittest.TestCase):
    def test_valid_identifiers_with_and_without_underscore(self):
        code = "abc _ a1 a_b2 _Z9 _1 __x _a\n"
        tokens = LexerPython(code).get_tokens()

        idents = [(t.tipo, t.lexema) for t in tokens if t.tipo in (TokenType.IDENTIFIER,)]
        self.assertEqual(
            idents,
            [
                (TokenType.IDENTIFIER, "abc"),
                (TokenType.IDENTIFIER, "_"),
                (TokenType.IDENTIFIER, "a1"),
                (TokenType.IDENTIFIER, "a_b2"),
                (TokenType.IDENTIFIER, "_Z9"),
                (TokenType.IDENTIFIER, "_1"),
                (TokenType.IDENTIFIER, "__x"),
                (TokenType.IDENTIFIER, "_a"),
            ],
        )

        self.assertEqual(tokens[-2].tipo, TokenType.NEWLINE)
        self.assertEqual(tokens[-1].tipo, TokenType.EOF)

    def test_identifier_too_long_raises_error(self):
        long_ident = "a" * 21  # 21 chars
        code = f"{long_ident}\n"
        with self.assertRaises(Exception) as ctx:
            LexerPython(code).get_tokens()
        msg = str(ctx.exception)
        self.assertIn("Erro léxico na linha 1", msg)
        self.assertIn("identificador com mais de 20 caracteres", msg)

    def test_identifier_cannot_start_with_number_simple(self):
        code = "1abc\n"
        with self.assertRaises(Exception) as ctx:
            LexerPython(code).get_tokens()
        self.assertIn("Erro léxico na linha 1", str(ctx.exception))
        self.assertIn("iniciando com número", str(ctx.exception))

    def test_identifier_cannot_start_with_number_with_underscore(self):
        code = "9_var\n"
        with self.assertRaises(Exception) as ctx:
            LexerPython(code).get_tokens()
        self.assertIn("Erro léxico na linha 1", str(ctx.exception))
        self.assertIn("iniciando com número", str(ctx.exception))

    def test_valid_identifier_mixed_underscore_and_digits(self):
        code = "_ab_2_a2\n"
        tokens = LexerPython(code).get_tokens()
        self.assertGreaterEqual(len(tokens), 3)
        self.assertEqual(tokens[0].tipo, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].lexema, "_ab_2_a2")
        self.assertEqual(tokens[1].tipo, TokenType.NEWLINE)
        self.assertEqual(tokens[2].tipo, TokenType.EOF)

if __name__ == "__main__":
    unittest.main()
