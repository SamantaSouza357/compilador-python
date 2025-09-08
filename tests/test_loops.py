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
    WhileStatement,
    ForStatement,
    BreakStatement,
    ContinueStatement,
    VarAssign,
    Literal,
    Identifier,
)
from errors import SyntaxErrorCompilador


def parse_source(source: str) -> Program:
    tokens = LexerPython(source).get_tokens()
    return SyntaxAnalyzer(tokens).parse()


class TestLoops(unittest.TestCase):
    def test_parse_simple_while_with_break(self):
        code = (
            "x=0\n"
            "while x<10:\n"
            "    break\n"
        )
        ast = parse_source(code)
        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 2)
        loop = ast.statements[1]
        self.assertIsInstance(loop, WhileStatement)
        self.assertEqual(len(loop.body.statements), 1)
        self.assertIsInstance(loop.body.statements[0], BreakStatement)

    def test_parse_simple_for_with_continue(self):
        code = (
            "xs=0\n"
            "for i in xs:\n"
            "    continue\n"
        )
        ast = parse_source(code)
        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 2)
        loop = ast.statements[1]
        self.assertIsInstance(loop, ForStatement)
        self.assertEqual(len(loop.body.statements), 1)
        self.assertIsInstance(loop.body.statements[0], ContinueStatement)

    def test_nested_loops(self):
        code = (
            "i=0\n"
            "while i<3:\n"
            "    for j in i:\n"
            "        x=1\n"
        )
        ast = parse_source(code)
        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 2)
        outer = ast.statements[1]
        self.assertIsInstance(outer, WhileStatement)
        self.assertEqual(len(outer.body.statements), 1)
        inner = outer.body.statements[0]
        self.assertIsInstance(inner, ForStatement)
        self.assertEqual(len(inner.body.statements), 1)
        assign = inner.body.statements[0]
        self.assertIsInstance(assign, VarAssign)
        self.assertEqual(assign.name, "x")
        self.assertIsInstance(assign.expr, Literal)
        self.assertEqual(assign.expr.value, 1)

    def test_while_missing_colon_raises(self):
        code = (
            "while True\n"
            "    x=1\n"
        )
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador) as ctx:
            SyntaxAnalyzer(tokens).parse()
        # Should point to the while line
        self.assertEqual(ctx.exception.linha, 1)

    def test_for_missing_in_raises(self):
        code = (
            "for i xs:\n"
            "    x=1\n"
        )
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador) as ctx:
            SyntaxAnalyzer(tokens).parse()
        self.assertEqual(ctx.exception.linha, 1)

    def test_for_missing_colon_raises(self):
        code = (
            "for i in xs\n"
            "    x=1\n"
        )
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador) as ctx:
            SyntaxAnalyzer(tokens).parse()
        self.assertEqual(ctx.exception.linha, 1)


if __name__ == "__main__":
    unittest.main()

