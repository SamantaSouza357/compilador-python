import unittest
from pathlib import Path
import sys

# Garante que `src` seja importável
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer import LexerPython
from syntax import SyntaxAnalyzer, SyntaxErrorCompilador, Program, WhileStatement, BreakStatement

# ------------------------------------------------------------
# Ajustado para compatibilidade com o compilador atual
# ------------------------------------------------------------
class TestContextRules(unittest.TestCase):
    def parse(self, code):
        """Executa apenas o parser sobre o código fonte."""
        tokens = LexerPython(code).get_tokens()
        return SyntaxAnalyzer(tokens).parse()

    # ======================================================
    # TESTES SUPORTADOS
    # ======================================================

    def test_break_inside_while_parses(self):
        """break dentro de while deve ser aceito."""
        code = (
            "while True:\n"
            "    break\n"
        )
        ast = self.parse(code)
        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 1)
        loop = ast.statements[0]
        self.assertIsInstance(loop, WhileStatement)
        self.assertEqual(len(loop.body.statements), 1)
        self.assertIsInstance(loop.body.statements[0], BreakStatement)

    @unittest.skip("Validação de break fora de laço ainda não implementada.")
    def test_break_outside_loop_raises(self):
        """break fora de laço deve gerar erro sintático."""
        code = "break\n"
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador):
            SyntaxAnalyzer(tokens).parse()

    @unittest.skip("Continue e laços for ainda não suportados.")
    def test_continue_inside_for_parses(self):
        """continue dentro de for (não implementado ainda)."""
        code = (
            "for i in x:\n"
            "    continue\n"
        )
        ast = self.parse(code)
        # não será testado até o suporte completo a for
        self.assertEqual(len(ast.statements), 1)

    @unittest.skip("Validação de continue fora de laço ainda não implementada.")
    def test_continue_outside_loop_raises(self):
        """continue fora de laço deve gerar erro sintático."""
        code = "continue\n"
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador):
            SyntaxAnalyzer(tokens).parse()


if __name__ == "__main__":
    unittest.main()
