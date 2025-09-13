import unittest
from pathlib import Path
import sys

# Ensure `src` is importable
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer import LexerPython
from syntax import SyntaxAnalyzer, SyntaxErrorCompilador, Program, WhileStatement, ForStatement, BreakStatement, ContinueStatement


class TestContextRules(unittest.TestCase):
    def parse(self, code):
        tokens = LexerPython(code).get_tokens()
        return SyntaxAnalyzer(tokens).parse()

    def test_break_inside_while_parses(self):
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

    def test_continue_inside_for_parses(self):
        code = (
            "for i in x:\n"
            "    continue\n"
        )
        ast = self.parse(code)
        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 1)
        loop = ast.statements[0]
        self.assertIsInstance(loop, ForStatement)
        self.assertEqual(len(loop.body.statements), 1)
        self.assertIsInstance(loop.body.statements[0], ContinueStatement)

    def test_break_outside_loop_raises(self):
        code = (
            "break\n"
        )
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador):
            SyntaxAnalyzer(tokens).parse()

    def test_continue_outside_loop_raises(self):
        code = (
            "continue\n"
        )
        tokens = LexerPython(code).get_tokens()
        with self.assertRaises(SyntaxErrorCompilador):
            SyntaxAnalyzer(tokens).parse()


if __name__ == "__main__":
    unittest.main()
