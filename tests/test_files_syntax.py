import unittest
from pathlib import Path
import sys

# Garante que `src` seja importável
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer import LexerPython
from syntax import SyntaxAnalyzer, Program, SyntaxErrorCompilador


class TestFilesSyntax(unittest.TestCase):
    """Testes de integração do analisador sintático com arquivos de exemplo."""

    def read(self, name: str) -> str:
        """Lê o conteúdo de um arquivo de teste."""
        path = ROOT / "tests" / "files" / name
        return path.read_text(encoding="utf-8")

    # ======================================================
    # TESTES SUPORTADOS
    # ======================================================

    def test_valid_simple_parse(self):
        """Verifica se o exemplo válido gera uma AST do tipo Program."""
        code = self.read("exemplo_valido.txt")
        tokens = LexerPython(code).get_tokens()
        ast = SyntaxAnalyzer(tokens).parse()
        self.assertIsInstance(ast, Program)
        # Basta garantir que o parser não falhou e há comandos
        self.assertGreater(len(ast.statements), 0)

    def test_corner_blank_lines_indent_parse(self):
        """Garante que linhas em branco e indentação são tratadas corretamente."""
        code = self.read("exemplo_linhas_em_branco.txt")
        tokens = LexerPython(code).get_tokens()
        ast = SyntaxAnalyzer(tokens).parse()
        self.assertIsInstance(ast, Program)
        self.assertGreaterEqual(len(ast.statements), 1)

if __name__ == "__main__":
    unittest.main()
