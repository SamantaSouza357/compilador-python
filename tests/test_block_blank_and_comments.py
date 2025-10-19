import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer import LexerPython
from syntax import SyntaxAnalyzer, Program, FunctionDeclaration, IfStatement, ReturnStatement


class TestBlockBlankAndComments(unittest.TestCase):
    def test_blank_lines_and_comments_before_first_statement_in_block(self):
        code = (
            "def outer():\n"
            "\n"
            "    # first comment\n"
            "    # second comment\n"
            "\n"
            "    if True:\n"
            "        # inside then comment\n"
            "        return 1\n"
            "    else:\n"
            "        # inside else comment\n"
            "        return 0\n"
        )
        tokens = LexerPython(code).get_tokens()
        ast = SyntaxAnalyzer(tokens).parse()
        self.assertIsInstance(ast, Program)
        self.assertGreaterEqual(len(ast.statements), 1)
        func = ast.statements[0]
        self.assertIsInstance(func, FunctionDeclaration)
        self.assertEqual(len(func.body.statements), 1)
        if_stmt = func.body.statements[0]
        self.assertIsInstance(if_stmt, IfStatement)
        self.assertIsInstance(if_stmt.then_block.statements[0], ReturnStatement)
        self.assertIsInstance(if_stmt.else_block.statements[0], ReturnStatement)

    def test_triple_quoted_block_comment_inside_block(self):
        # Strings com aspas triplas usadas como comentários de bloco devem ser permitidas.
        code = (
            "def foo():\n"
            "    '''comentário de bloco'''\n"
            "    x = 1\n"
            "    if x > 0:\n"
            "        print(x)\n"
        )
        tokens = LexerPython(code).get_tokens()
        ast = SyntaxAnalyzer(tokens).parse()
        self.assertIsInstance(ast, Program)
        func = ast.statements[0]
        self.assertIsInstance(func, FunctionDeclaration)
        # Corpo deve ter duas instruções: a atribuição e o if
        self.assertEqual(len(func.body.statements), 2)


if __name__ == "__main__":
    unittest.main()
