import unittest
from pathlib import Path
import sys

# Ensure `src` is importable
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer_analyzer import LexerPython
from syntax_analyzer import (
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
    tokens = LexerPython(code).get_tokens()
    ast = SyntaxAnalyzer(tokens).parse()
    assert isinstance(ast, Program)
    assert len(ast.statements) >= 1
    return ast.statements[0]


class TestUnaryExpressions(unittest.TestCase):
    def test_unary_minus_simple_number(self):
        node = parse_stmt("x=-1\n")
        self.assertIsInstance(node, VarAssign)
        self.assertEqual(node.name, "x")
        self.assertIsInstance(node.expr, UnaryOp)
        self.assertEqual(node.expr.op, "-")
        self.assertIsInstance(node.expr.operand, Literal)
        self.assertEqual(node.expr.operand.value, 1)

    def test_unary_minus_binding_power_over_multiply(self):
        node = parse_stmt("-a * b\n")
        # (-a) * b
        self.assertIsInstance(node, BinaryOperation)
        self.assertEqual(node.op, "*")
        self.assertIsInstance(node.left, UnaryOp)
        self.assertEqual(node.left.op, "-")
        self.assertIsInstance(node.left.operand, Identifier)
        self.assertEqual(node.left.operand.name, "a")

    def test_double_unary_minus(self):
        node = parse_stmt("--x\n")
        self.assertIsInstance(node, UnaryOp)
        self.assertEqual(node.op, "-")
        inner = node.operand
        self.assertIsInstance(inner, UnaryOp)
        self.assertEqual(inner.op, "-")
        self.assertIsInstance(inner.operand, Identifier)
        self.assertEqual(inner.operand.name, "x")

    def test_binary_minus_and_unary_minus_mix(self):
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
        node = parse_stmt("f(-x, y)\n")
        self.assertIsInstance(node, Call)
        self.assertEqual(len(node.args), 2)
        self.assertIsInstance(node.args[0], UnaryOp)
        self.assertEqual(node.args[0].op, "-")
        self.assertIsInstance(node.args[0].operand, Identifier)
        self.assertEqual(node.args[0].operand.name, "x")

    def test_unary_in_parentheses(self):
        node = parse_stmt("(-1 + 2) * 3\n")
        self.assertIsInstance(node, BinaryOperation)
        self.assertEqual(node.op, "*")
        self.assertIsInstance(node.left, BinaryOperation)
        self.assertEqual(node.left.op, "+")
        self.assertIsInstance(node.left.left, UnaryOp)
        self.assertIsInstance(node.left.left.operand, Literal)
        self.assertEqual(node.left.left.operand.value, 1)
        self.assertIsInstance(node.left.right, Literal)
        self.assertEqual(node.left.right.value, 2)


if __name__ == "__main__":
    unittest.main()

