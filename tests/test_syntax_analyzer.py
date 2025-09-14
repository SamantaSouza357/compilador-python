import unittest
from pathlib import Path
import sys

# Ensure `src` is importable
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer import LexerPython
from syntax import (
    SyntaxAnalyzer,
    Program,
    FunctionDeclaration,
    Block,
    IfStatement,
    ReturnStatement,
    VarAssign,
    Call,
    Identifier,
    Literal,
)


class TestSyntaxAnalyzer(unittest.TestCase):
    def test_parse_example_program_ast_shape(self):
        example_path = ROOT / "tests" / "files" / "exemplo_valido.txt"
        source = example_path.read_text(encoding="utf-8")

        tokens = LexerPython(source).get_tokens()
        parser = SyntaxAnalyzer(tokens)
        ast = parser.parse()

        self.assertIsInstance(ast, Program)
        self.assertGreaterEqual(len(ast.statements), 5)

        # 1) Function declaration: soma(x, y)
        func = ast.statements[0]
        self.assertIsInstance(func, FunctionDeclaration)
        self.assertEqual(func.name, "soma")
        self.assertEqual(func.params, ["x", "y"])
        self.assertIsInstance(func.body, Block)

        # Inside function: if ... else ... with returns
        self.assertEqual(len(func.body.statements), 1)
        if_stmt = func.body.statements[0]
        self.assertIsInstance(if_stmt, IfStatement)
        self.assertIsInstance(if_stmt.then_block, Block)
        self.assertIsInstance(if_stmt.else_block, Block)
        self.assertEqual(len(if_stmt.then_block.statements), 1)
        self.assertEqual(len(if_stmt.else_block.statements), 1)
        self.assertIsInstance(if_stmt.then_block.statements[0], ReturnStatement)
        self.assertIsInstance(if_stmt.else_block.statements[0], ReturnStatement)

        # 2) x = 1
        assign_x = ast.statements[1]
        self.assertIsInstance(assign_x, VarAssign)
        self.assertEqual(assign_x.name, "x")
        self.assertTrue(isinstance(assign_x.expr, Literal))

        # 3) y = 2
        assign_y = ast.statements[2]
        self.assertIsInstance(assign_y, VarAssign)
        self.assertEqual(assign_y.name, "y")
        self.assertTrue(isinstance(assign_y.expr, Literal))

        # 4) r = soma(x, y)
        assign_r = ast.statements[3]
        self.assertIsInstance(assign_r, VarAssign)
        self.assertEqual(assign_r.name, "r")
        self.assertIsInstance(assign_r.expr, Call)
        self.assertIsInstance(assign_r.expr.callee, Identifier)
        self.assertEqual(assign_r.expr.callee.name, "soma")
        self.assertEqual(len(assign_r.expr.args), 2)
        self.assertIsInstance(assign_r.expr.args[0], Identifier)
        self.assertIsInstance(assign_r.expr.args[1], Identifier)

        # 5) print("A soma é:", r) — expressão de chamada no topo
        last = ast.statements[4]
        self.assertIsInstance(last, Call)
        self.assertIsInstance(last.callee, Identifier)
        self.assertEqual(last.callee.name, "print")


if __name__ == "__main__":
    unittest.main()
