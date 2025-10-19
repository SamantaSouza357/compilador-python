import unittest
from pathlib import Path
import sys

# Garante que `src` seja importável
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lexer import LexerPython
from syntax import SyntaxAnalyzer
from semantic import SemanticAnalyzer
from codegen import MepaGenerator, CodeGenerationError


class TestMepaGenerator(unittest.TestCase):
    def compile_source(self, source: str):
        """Executa o pipeline completo até o código MEPA."""
        tokens = LexerPython(source).get_tokens()
        ast = SyntaxAnalyzer(tokens).parse()
        SemanticAnalyzer(ast).analyze()
        return MepaGenerator().generate(ast)

    # ======================================================
    # TESTES SUPORTADOS PELO GERADOR ATUAL
    # ======================================================

    def test_simple_loop_and_print(self):
        """Verifica while + print."""
        code = (
            "x=1\n"
            "y=2\n"
            "while x<y:\n"
            "    x=x+1\n"
            "print(x)\n"
        )
        instructions = self.compile_source(code)

        # As instruções devem conter os blocos esperados
        self.assertIn("INPP", instructions[0])
        self.assertIn("CMME", " ".join(instructions))
        self.assertIn("IMPR", " ".join(instructions))
        self.assertIn("PARA", instructions[-1])

    def test_print_requires_call(self):
        """Verifica erro para expressão isolada sem print()."""
        code = (
            "x=1\n"
            "print(x)\n"
            "x\n"
        )
        with self.assertRaises(CodeGenerationError):
            self.compile_source(code)

    def test_break_and_continue_in_while(self):
        """Verifica uso de break e continue dentro de while."""
        code = (
            "x=0\n"
            "while x<3:\n"
            "    x=x+1\n"
            "    if x==2:\n"
            "        continue\n"
            "    if x==3:\n"
            "        break\n"
            "print(x)\n"
        )
        instructions = self.compile_source(code)
        joined = "\n".join(instructions)
        self.assertIn("DSVS", joined)
        self.assertIn("CMME", joined)
        self.assertIn("IMPR", joined)

    # ======================================================
    # TESTES NÃO IMPLEMENTADOS (IGNORADOS)
    # ======================================================

    @unittest.skip("Funções ainda não suportadas pelo gerador MEPA atual.")
    def test_function_call_with_return(self):
        code = (
            "def soma(a, b):\n"
            "    r=a+b\n"
            "    return r\n"
            "x=0\n"
            "y=soma(1,2)\n"
            "print(y)\n"
        )
        instructions = self.compile_source(code)
        self.assertIn("CHPR", " ".join(instructions))

    @unittest.skip("Loop for-range ainda não suportado pelo gerador MEPA atual.")
    def test_for_range_loop(self):
        code = (
            "x=0\n"
            "for i in range(3):\n"
            "    x=x+1\n"
            "print(x)\n"
        )
        instructions = self.compile_source(code)
        self.assertIn("CMME", " ".join(instructions))
        self.assertIn("IMPR", " ".join(instructions))


if __name__ == "__main__":
    unittest.main()
