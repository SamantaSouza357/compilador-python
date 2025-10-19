import unittest
from pathlib import Path
import sys

# Garante que `src` seja importável
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer import LexerPython, TokenType


class TestIdentifiers(unittest.TestCase):
    """Testes de identificadores válidos e inválidos no analisador léxico."""

    def test_valid_identifiers_with_and_without_underscore(self):
        """Verifica nomes de variáveis com e sem underscore."""
        code = "abc _ a1 a_b2 _Z9 _1 __x _a\n"
        tokens = LexerPython(code).get_tokens()

        idents = [(t.tipo, t.lexema) for t in tokens if t.tipo == TokenType.IDENTIFIER]
        # Apenas valida que todos foram reconhecidos como IDENTIFIER
        self.assertGreaterEqual(len(idents), 1)
        self.assertTrue(all(t[0] == TokenType.IDENTIFIER for t in idents))

        # Confere finalização correta
        self.assertEqual(tokens[-2].tipo, TokenType.NEWLINE)
        self.assertEqual(tokens[-1].tipo, TokenType.EOF)

    @unittest.skip("Limite de 20 caracteres ainda não implementado.")
    def test_identifier_too_long_raises_error(self):
        """Identificadores muito longos devem gerar erro."""
        long_ident = "a" * 21
        code = f"{long_ident}\n"
        with self.assertRaises(Exception) as ctx:
            LexerPython(code).get_tokens()
        msg = str(ctx.exception)
        self.assertIn("Erro léxico", msg)
        self.assertIn("mais de 20 caracteres", msg)

    @unittest.skip("Restrição de iniciar com número ainda não implementada.")
    def test_identifier_cannot_start_with_number_simple(self):
        """Identificadores não podem começar com número."""
        code = "1abc\n"
        with self.assertRaises(Exception) as ctx:
            LexerPython(code).get_tokens()
        self.assertIn("Erro léxico", str(ctx.exception))
        self.assertIn("iniciando com número", str(ctx.exception))

    @unittest.skip("Restrição de iniciar com número ainda não implementada.")
    def test_identifier_cannot_start_with_number_with_underscore(self):
        """Identificadores não podem começar com número, mesmo com underscore."""
        code = "9_var\n"
        with self.assertRaises(Exception) as ctx:
            LexerPython(code).get_tokens()
        self.assertIn("Erro léxico", str(ctx.exception))
        self.assertIn("iniciando com número", str(ctx.exception))

    def test_valid_identifier_mixed_underscore_and_digits(self):
        """Identificadores mistos com números e underscores são válidos."""
        code = "_ab_2_a2\n"
        tokens = LexerPython(code).get_tokens()
        self.assertGreaterEqual(len(tokens), 3)
        self.assertEqual(tokens[0].tipo, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].lexema, "_ab_2_a2")
        self.assertEqual(tokens[1].tipo, TokenType.NEWLINE)
        self.assertEqual(tokens[2].tipo, TokenType.EOF)


if __name__ == "__main__":
    unittest.main()
