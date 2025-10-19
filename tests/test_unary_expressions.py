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
    UnaryOp,
    BinaryOperation,
    Identifier,
    Literal,
    Call,
)


def parse_stmt(code: str):
    """Função auxiliar para retornar o primeiro statement da AST."""
    tokens = LexerPython(code).get_tokens()
    ast = SyntaxAnalyzer(tokens).parse()
    assert isinstance(ast, Program)
    assert len(ast.statements) >= 1
    return ast.statements[0]


class TestUnaryExpressions(unittest.TestCase):
    def test_unary_minus_simple_number(self):
        """x = -1 deve gerar VarAssign(UnaryOp(Literal(1)))"""
        node = parse_stmt("x=-1\n")
        self.assertIsInstance(node, VarAssign)
        self.assertEqual(node.name, "x")
        self.assertIsInstance(node.expr, UnaryOp)
        self.assertEqual(node.expr.op, "-")
        self.assertIsInstance(node.expr.operand, Literal)
        self.assertEqual(node.expr.operand.value, 1)

    def test_unary_minus_binding_power_over_multiply(self):
        """Verifica se -a * b é interpretado como (-a) * b"""
        node = parse_stmt("-a * b\n")
        self.assertIsInstance(node, BinaryOperation)
        self.assertEqual(node.op, "*")
        self.assertIsInstance(node.left, UnaryOp)
        self.assertEqual(node.left.op, "-")
        self.assertIsInstance(node.left.operand, Identifier)
        self.assertEqual(node.left.operand.name, "a")

    def test_double_unary_minus(self):
        """--x deve criar dois UnaryOp aninhados."""
        node = parse_stmt("--x\n")

        # Pode ser UnaryOp(UnaryOp(Identifier('x'))) ou simplificado
        self.assertIsInstance(node, UnaryOp)
        self.assertEqual(node.op, "-")

        inner = node.operand
        self.assertIsInstance(inner, UnaryOp)
        self.assertEqual(inner.op, "-")
        self.assertIsInstance(inner.operand, Identifier)
        self.assertEqual(inner.operand.name, "x")

    def test_binary_minus_and_unary_minus_mix(self):
        """a - -b deve criar BinaryOperation('-', Identifier(a), UnaryOp('-', Identifier(b)))"""
        node = parse_stmt("a - -b\n")
        self.assertIsInstance(node, BinaryOperation)
        self.assertEqual(node.op, "-")
        self.assertIsInstance(node.left, Identifier)
        self.assertEqual(node.left.name, "a")
        self.assertIsInstance(node.right, UnaryOp)
        self.assertEqual(node.right.op, "-")
        self.assertIsInstance(node.right.operand, Identifier)
        self.assertEqual(node.right.operand.name, "b")

    def test_unary_inside_call_arguments(self):
        """f(-x, y) deve permitir UnaryOp dentro dos argumentos."""
        node = parse_stmt("f(-x, y)\n")
        self.assertIsInstance(node, Call)
        self.assertEqual(len(node.args), 2)

        arg1 = node.args[0]
        self.assertIsInstance(arg1, UnaryOp)
        self.assertEqual(arg1.op, "-")
        self.assertIsInstance(arg1.operand, Identifier)
        self.assertEqual(arg1.operand.name, "x")

        arg2 = node.args[1]
        self.assertIsInstance(arg2, Identifier)
        self.assertEqual(arg2.name, "y")

    def test_unary_in_parentheses(self):
        """(-1 + 2) * 3 deve respeitar precedência dos parênteses."""
        node = parse_stmt("(-1 + 2) * 3\n")
        self.assertIsInstance(node, BinaryOperation)
        self.assertEqual(node.op, "*")

        left = node.left
        self.assertIsInstance(left, BinaryOperation)
        self.assertEqual(left.op, "+")

        # (-1) deve ser UnaryOp(Literal(1))
        self.assertIsInstance(left.left, UnaryOp)
        self.assertEqual(left.left.op, "-")
        self.assertIsInstance(left.left.operand, Literal)
        self.assertEqual(left.left.operand.value, 1)

        self.assertIsInstance(left.right, Literal)
        self.assertEqual(left.right.value, 2)

        self.assertIsInstance(node.right, Literal)
        self.assertEqual(node.right.value, 3)


if __name__ == "__main__":
    unittest.main()
