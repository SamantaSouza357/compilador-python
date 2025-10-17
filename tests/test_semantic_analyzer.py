import unittest
from pathlib import Path
import sys

# Configura caminho para importar src
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer import LexerPython
from syntax import SyntaxAnalyzer
from semantic import SemanticAnalyzer, SemanticError


def analyze_source(code: str) -> None:
    tokens = LexerPython(code).get_tokens()
    ast = SyntaxAnalyzer(tokens).parse()
    SemanticAnalyzer(ast).analyze()


class TestSemanticAnalyzer(unittest.TestCase):
    def test_duplicate_global_declaration_raises(self):
        code = (
            "x=1\n"
            "x=2\n"
            "print(x)\n"
        )
        with self.assertRaises(SemanticError) as ctx:
            analyze_source(code)
        self.assertIn("já declarada", str(ctx.exception))

    def test_use_of_undeclared_variable_raises(self):
        code = (
            "print(x)\n"
        )
        with self.assertRaises(SemanticError) as ctx:
            analyze_source(code)
        self.assertIn("não declarada", str(ctx.exception))

    def test_assignment_to_undeclared_variable_after_body_raises(self):
        code = (
            "x=1\n"
            "print(x)\n"
            "y=x+1\n"
        )
        with self.assertRaises(SemanticError) as ctx:
            analyze_source(code)
        self.assertIn("não declarada", str(ctx.exception))

    def test_valid_program_passes_semantic_analysis(self):
        code = (
            "valor=0\n"
            "contador=0\n"
            "print(contador)\n"
            "contador=contador+1\n"
            "valor=valor+contador\n"
        )
        analyze_source(code)  # não deve lançar

    def test_function_parameters_are_considered_declared(self):
        code = (
            "resultado=0\n"
            "def soma(a, b):\n"
            "    return a + b\n"
            "resultado=soma(1, 2)\n"
            "print(resultado)\n"
        )
        analyze_source(code)

    def test_undeclared_variable_inside_function_raises(self):
        code = (
            "def foo(a):\n"
            "    return a + b\n"
            "b=1\n"
            "print(b)\n"
        )
        with self.assertRaises(SemanticError):
            analyze_source(code)


if __name__ == "__main__":
    unittest.main()
