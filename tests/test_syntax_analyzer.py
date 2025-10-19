import unittest
from pathlib import Path
import sys

# Garante que `src` seja importável
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer import LexerPython
from syntax import (
    SyntaxAnalyzer,
    Program,
    VarAssign,
    Call,
    Identifier,
    Literal,
    BinaryOperation,
)


class TestSyntaxAnalyzer(unittest.TestCase):
    def test_parse_example_program_ast_shape(self):
        """Verifica a estrutura geral da AST de exemplo_valido.txt (sem funções, com operações binárias)"""
        example_path = ROOT / "tests" / "files" / "exemplo_valido.txt"
        source = example_path.read_text(encoding="utf-8")

        tokens = LexerPython(source).get_tokens()
        parser = SyntaxAnalyzer(tokens)
        ast = parser.parse()

        # O programa principal deve ser uma instância de Program
        self.assertIsInstance(ast, Program)
        self.assertGreaterEqual(len(ast.statements), 3)

        # -------------------------------------------------------------
        # 1) Deve existir uma atribuição x = 1
        # -------------------------------------------------------------
        assign_x = next(
            (s for s in ast.statements if isinstance(s, VarAssign) and s.name == "x"),
            None,
        )
        self.assertIsNotNone(assign_x, "Variável x não encontrada")
        self.assertIsInstance(assign_x.expr, Literal)

        # -------------------------------------------------------------
        # 2) Deve existir uma atribuição y = 2
        # -------------------------------------------------------------
        assign_y = next(
            (s for s in ast.statements if isinstance(s, VarAssign) and s.name == "y"),
            None,
        )
        self.assertIsNotNone(assign_y, "Variável y não encontrada")
        self.assertIsInstance(assign_y.expr, Literal)

        # -------------------------------------------------------------
        # 3) Deve existir uma atribuição r = x + y
        # -------------------------------------------------------------
        assign_r = next(
            (s for s in ast.statements if isinstance(s, VarAssign) and s.name == "r"),
            None,
        )
        self.assertIsNotNone(assign_r, "Variável r não encontrada")
        self.assertIsInstance(assign_r.expr, BinaryOperation)
        self.assertEqual(assign_r.expr.op, "+")
        self.assertIsInstance(assign_r.expr.left, Identifier)
        self.assertIsInstance(assign_r.expr.right, Identifier)

        # -------------------------------------------------------------
        # 4) Deve existir um print("A soma é:", r)
        # -------------------------------------------------------------
        print_call = next(
            (
                s
                for s in ast.statements
                if isinstance(s, Call)
                and isinstance(s.callee, Identifier)
                and s.callee.name == "print"
            ),
            None,
        )
        self.assertIsNotNone(print_call, "Chamada a print() não encontrada")
        self.assertTrue(
            any(isinstance(arg, (Literal, Identifier)) for arg in print_call.args),
            "print() deve conter pelo menos um literal ou identificador",
        )


if __name__ == "__main__":
    unittest.main()
