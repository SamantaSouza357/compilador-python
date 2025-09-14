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


def parse_single_stmt(code: str):
    tokens = LexerPython(code).get_tokens()
    ast = SyntaxAnalyzer(tokens).parse()
    assert isinstance(ast, Program)
    assert len(ast.statements) >= 1
    return ast.statements[0]


class TestExpressions(unittest.TestCase):
    def test_precedence_mul_over_add(self):
        node = parse_single_stmt("1+2*3\n")
        self.assertIsInstance(node, BinaryOperation)
        self.assertEqual(node.op, "+")
        self.assertIsInstance(node.left, Literal)
        self.assertEqual(node.left.value, 1)
        self.assertIsInstance(node.right, BinaryOperation)
        self.assertEqual(node.right.op, "*")
        self.assertIsInstance(node.right.left, Literal)
        self.assertEqual(node.right.left.value, 2)
        self.assertIsInstance(node.right.right, Literal)
        self.assertEqual(node.right.right.value, 3)

    def test_left_associativity_sub(self):
        node = parse_single_stmt("a - b - c\n")
        self.assertIsInstance(node, BinaryOperation)
        self.assertEqual(node.op, "-")
        self.assertIsInstance(node.left, BinaryOperation)
        self.assertEqual(node.left.op, "-")
        self.assertIsInstance(node.left.left, Identifier)
        self.assertEqual(node.left.left.name, "a")
        self.assertIsInstance(node.left.right, Identifier)
        self.assertEqual(node.left.right.name, "b")
        self.assertIsInstance(node.right, Identifier)
        self.assertEqual(node.right.name, "c")

    def test_parentheses_override(self):
        node = parse_single_stmt("(1+2)*3\n")
        self.assertIsInstance(node, BinaryOperation)
        self.assertEqual(node.op, "*")
        self.assertIsInstance(node.left, BinaryOperation)
        self.assertEqual(node.left.op, "+")
        self.assertIsInstance(node.left.left, Literal)
        self.assertEqual(node.left.left.value, 1)
        self.assertIsInstance(node.left.right, Literal)
        self.assertEqual(node.left.right.value, 2)
        self.assertIsInstance(node.right, Literal)
        self.assertEqual(node.right.value, 3)

    def test_comparison_low_precedence(self):
        node = parse_single_stmt("1+2*3 == 7\n")
        self.assertIsInstance(node, BinaryOperation)
        self.assertEqual(node.op, "==")
        self.assertIsInstance(node.left, BinaryOperation)
        self.assertEqual(node.left.op, "+")
        self.assertIsInstance(node.left.right, BinaryOperation)
        self.assertEqual(node.left.right.op, "*")
        self.assertIsInstance(node.right, Literal)
        self.assertEqual(node.right.value, 7)

    def test_call_and_args(self):
        node = parse_single_stmt("f(x, y+1)\n")
        self.assertIsInstance(node, Call)
        self.assertIsInstance(node.callee, Identifier)
        self.assertEqual(node.callee.name, "f")
        self.assertEqual(len(node.args), 2)
        self.assertIsInstance(node.args[0], Identifier)
        self.assertEqual(node.args[0].name, "x")
        self.assertIsInstance(node.args[1], BinaryOperation)
        self.assertIsInstance(node.args[1].left, Identifier)
        self.assertEqual(node.args[1].left.name, "y")
        self.assertEqual(node.args[1].op, "+")
        self.assertEqual(node.args[1].right.value, 1)

    def test_chained_calls(self):
        node = parse_single_stmt("f(x)(y)\n")
        self.assertIsInstance(node, Call)
        inner = node.callee
        self.assertIsInstance(inner, Call)
        self.assertIsInstance(inner.callee, Identifier)
        self.assertEqual(inner.callee.name, "f")
        self.assertEqual(len(inner.args), 1)
        self.assertIsInstance(inner.args[0], Identifier)
        self.assertEqual(inner.args[0].name, "x")
        self.assertEqual(len(node.args), 1)
        self.assertIsInstance(node.args[0], Identifier)
        self.assertEqual(node.args[0].name, "y")


if __name__ == "__main__":
    unittest.main()
