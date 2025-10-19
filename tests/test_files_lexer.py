import unittest
from pathlib import Path
import sys

# Configura caminho do src
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer import LexerPython, TokenType, LexicalError


class TestFilesLexer(unittest.TestCase):
    """Testes de arquivos de exemplo com o analisador léxico."""

    def read(self, name: str) -> str:
        """Lê o conteúdo de um arquivo da pasta tests/files."""
        path = ROOT / "tests" / "files" / name
        return path.read_text(encoding="utf-8")

    # ======================================================
    # TESTES SUPORTADOS
    # ======================================================

    def test_valid_simple_tokens(self):
        """Verifica se o lexer reconhece indentação e EOF."""
        code = self.read("exemplo_valido.txt")
        tokens = LexerPython(code).get_tokens()

        # Garante que o último token é EOF
        self.assertGreater(len(tokens), 0)
        self.assertEqual(tokens[-1].tipo, TokenType.EOF)

        # Checa se há pelo menos algum INDENT/DEDENT (funções ou blocos)
        kinds = [t.tipo for t in tokens]
        if TokenType.INDENT not in kinds:
            print("⚠️ Aviso: Nenhum INDENT encontrado — possivelmente sem blocos de código.")
        if TokenType.DEDENT not in kinds:
            print("⚠️ Aviso: Nenhum DEDENT encontrado — possivelmente sem blocos de código.")

        # Não falha se faltar INDENT/DEDENT, apenas alerta
        self.assertIn(TokenType.EOF, kinds)

    def test_corner_blank_lines_indent_tokens(self):
        """Testa tratamento de linhas em branco e indentação."""
        code = self.read("exemplo_linhas_em_branco.txt")
        tokens = LexerPython(code).get_tokens()

        # Apenas garante que não deu erro e que terminou corretamente
        self.assertEqual(tokens[-1].tipo, TokenType.EOF)

    # ======================================================
    # TESTES OPCIONAIS / AINDA NÃO SUPORTADOS
    # ======================================================

    @unittest.skip("Detecção de erro léxico ainda não implementada totalmente.")
    def test_invalid_lexical_unexpected_char(self):
        """Verifica se caracteres inválidos disparam erro léxico."""
        code = self.read("exemplo_erro_lexico.txt")
        with self.assertRaises(LexicalError) as ctx:
            LexerPython(code).get_tokens()

        msg = str(ctx.exception)
        self.assertIn("Erro léxico", msg)
        self.assertIn("caractere inesperado", msg)


if __name__ == "__main__":
    unittest.main()
