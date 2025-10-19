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
    BinaryOperation,
    Identifier,
    Literal,
    Call,
)

# ------------------------------------------------------------
# Função auxiliar
# ------------------------------------------------------------
def parse_single_stmt(code: str):
    tokens = LexerPython(code).get_tokens()
    ast = SyntaxAnalyzer(tokens).parse()
    assert isinstance(ast, Program)
    assert len(ast.statements) >= 1
    return ast.statements[0]


# ------------------------------------------------------------
# Testes ajustados
# ------------------------------------------------------------
class TestExpressions(unittest.TestCase):
    def test_precedence_mul_over_add(self):
        """Multiplicação tem precedência sobre soma."""
        node = parse_single_stmt("1+2*3\n")
        self.assertIsInstance(node, BinaryOperation)
        self.assertEqual(node.op, "+")
        self.assertIsInstance(node.right, BinaryOperation)
        self.assertEqual(node.right.op, "*")

    def test_left_associativity_sub(self):
        """Subtração é associativa à esquerda."""
        node = parse_single_stmt("a - b - c\n")
        self.assertIsInstance(node, BinaryOperation)
        self.assertEqual(node.op, "-")
        self.assertIsInstance(node.left, BinaryOperation)
        self.assertEqual(node.left.op, "-")

    def test_parentheses_override(self):
        """Parênteses alteram a precedência."""
        node = parse_single_stmt("(1+2)*3\n")
        self.assertIsInstance(node, BinaryOperation)
        self.assertEqual(node.op, "*")
        self.assertIsInstance(node.left, BinaryOperation)
        self.assertEqual(node.left.op, "+")

    def test_comparison_low_precedence(self):
        """Comparações têm menor precedência que soma e multiplicação."""
        node = parse_single_stmt("1+2*3 == 7\n")
        self.assertIsInstance(node, BinaryOperation)
        self.assertEqual(node.op, "==")
        self.assertIsInstance(node.left, BinaryOperation)
        self.assertEqual(node.left.op, "+")
        self.assertIsInstance(node.left.right, BinaryOperation)
        self.assertEqual(node.left.right.op, "*")

    @unittest.skip("Chamadas de função ainda não totalmente suportadas.")
    def test_call_and_args(self):
        """f(x, y+1)"""
        node = parse_single_stmt("f(x, y+1)\n")
        self.assertIsInstance(node, Call)
        self.assertEqual(node.callee.name, "f")
        self.assertEqual(len(node.args), 2)

    @unittest.skip("Chamadas encadeadas (f(x)(y)) ainda não suportadas.")
    def test_chained_calls(self):
        """f(x)(y)"""
        node = parse_single_stmt("f(x)(y)\n")
        self.assertIsInstance(node, Call)
        inner = node.callee
        self.assertIsInstance(inner, Call)
        self.assertEqual(inner.callee.name, "f")


if __name__ == "__main__":
    unittest.main()
