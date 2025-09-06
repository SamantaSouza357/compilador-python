import unittest
from pathlib import Path
import sys

# Ensure `src` is importable
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from compilador import LexerPython, TokenType

class TestLexer(unittest.TestCase):
    def test_tokens_for_entire_example_file(self):
        
        example = (ROOT / "tests" / "files" / "exemplo.py").read_text(encoding="utf-8")

        lexer = LexerPython(example)
        tokens = lexer.get_tokens()

        expected = [
            # def soma(x, y):\n
            (TokenType.KEYWORD, "def"),
            (TokenType.IDENTIFIER, "soma"),
            (TokenType.DELIMITER, "("),
            (TokenType.IDENTIFIER, "x"),
            (TokenType.DELIMITER, ","),
            (TokenType.IDENTIFIER, "y"),
            (TokenType.DELIMITER, ")"),
            (TokenType.DELIMITER, ":"),
            (TokenType.NEWLINE, "\n"),

            #     if x>y:\n
            (TokenType.KEYWORD, "if"),
            (TokenType.IDENTIFIER, "x"),
            (TokenType.OPERATOR, ">"),
            (TokenType.IDENTIFIER, "y"),
            (TokenType.DELIMITER, ":"),
            (TokenType.NEWLINE, "\n"),

            #         return x\n
            (TokenType.KEYWORD, "return"),
            (TokenType.IDENTIFIER, "x"),
            (TokenType.NEWLINE, "\n"),

            #     else:\n
            (TokenType.KEYWORD, "else"),
            (TokenType.DELIMITER, ":"),
            (TokenType.NEWLINE, "\n"),

            #         return y\n
            (TokenType.KEYWORD, "return"),
            (TokenType.IDENTIFIER, "y"),
            (TokenType.NEWLINE, "\n"),

            # blank line
            (TokenType.NEWLINE, "\n"),

            # x=1\n
            (TokenType.IDENTIFIER, "x"),
            (TokenType.ASSIGN, "="),
            (TokenType.NUMBER, "1"),
            (TokenType.NEWLINE, "\n"),

            # y=2\n
            (TokenType.IDENTIFIER, "y"),
            (TokenType.ASSIGN, "="),
            (TokenType.NUMBER, "2"),
            (TokenType.NEWLINE, "\n"),

            # r=soma(x,y)\n
            (TokenType.IDENTIFIER, "r"),
            (TokenType.ASSIGN, "="),
            (TokenType.IDENTIFIER, "soma"),
            (TokenType.DELIMITER, "("),
            (TokenType.IDENTIFIER, "x"),
            (TokenType.DELIMITER, ","),
            (TokenType.IDENTIFIER, "y"),
            (TokenType.DELIMITER, ")"),
            (TokenType.NEWLINE, "\n"),

            # print("A soma é:",r)
            (TokenType.IDENTIFIER, "print"),
            (TokenType.DELIMITER, "("),
            (TokenType.STRING, '"A soma é:"'),
            (TokenType.DELIMITER, ","),
            (TokenType.IDENTIFIER, "r"),
            (TokenType.DELIMITER, ")"),

            # EOF
            (TokenType.EOF, "EOF"),
        ]

        got = [(t.tipo, t.lexema) for t in tokens]
        self.assertEqual(got, expected)

    def test_lexical_error_unexpected_character_and_line(self):
        # Error on line 2 with unexpected '$'
        code = "x=1\n$\n"
        lexer = LexerPython(code)
        with self.assertRaises(Exception) as ctx:
            lexer.get_tokens()

        msg = str(ctx.exception)
        self.assertIn("Erro léxico na linha 2", msg)
        self.assertIn("'$'", msg)

if __name__ == "__main__":
    unittest.main()
