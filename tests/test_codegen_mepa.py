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
        tokens = LexerPython(source).get_tokens()
        ast = SyntaxAnalyzer(tokens).parse()
        SemanticAnalyzer(ast).analyze()
        return MepaGenerator().generate(ast)

    def test_simple_loop_and_print(self):
        code = (
            "x=1\n"
            "y=2\n"
            "while x<y:\n"
            "    x=x+1\n"
            "print(x)\n"
        )
        instructions = self.compile_source(code)
        self.assertEqual(
            instructions,
            [
                "INPP",
                "AMEM 2",
                "CRCT 1",
                "ARMZ 0 # x",
                "CRCT 2",
                "ARMZ 1 # y",
                "L1: NADA",
                "CRVL 0 # x",
                "CRVL 1 # y",
                "CMME",
                "DSVF L2",
                "CRVL 0 # x",
                "CRCT 1",
                "SOMA",
                "ARMZ 0 # x",
                "DSVS L1",
                "L2: NADA",
                "CRVL 0 # x",
                "IMPR",
                "DSVS LEND_3",
                "LEND_3: NADA",
                "PARA",
            ],
        )

    def test_print_requires_call(self):
        code = (
            "x=1\n"
            "print(x)\n"
            "x\n"
        )
        with self.assertRaises(CodeGenerationError):
            self.compile_source(code)

    def test_for_range_loop(self):
        code = (
            "x=0\n"
            "for i in range(3):\n"
            "    x=x+1\n"
            "print(x)\n"
        )
        instructions = self.compile_source(code)
        self.assertEqual(
            instructions,
            [
                "INPP",
                "AMEM 3",
                "CRCT 0",
                "ARMZ 0 # x",
                "CRCT 0",
                "ARMZ 1 # i",
                "CRCT 3",
                "ARMZ 2 # i_limite",
                "L1: NADA",
                "CRVL 1 # i",
                "CRVL 2 # i_limite",
                "CMME",
                "DSVF L2",
                "CRVL 0 # x",
                "CRCT 1",
                "SOMA",
                "ARMZ 0 # x",
                "L3: NADA",
                "CRVL 1 # i",
                "CRCT 1",
                "SOMA",
                "ARMZ 1 # i",
                "DSVS L1",
                "L2: NADA",
                "CRVL 0 # x",
                "IMPR",
                "DSVS LEND_4",
                "LEND_4: NADA",
                "PARA",
            ],
        )

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
        self.assertEqual(
            instructions,
            [
                "INPP",
                "AMEM 6",
                "CRCT 0",
                "ARMZ 4 # x",
                "CRCT 1",
                "ARMZ 0 # a",
                "CRCT 2",
                "ARMZ 1 # b",
                "CHPR F_soma_1",
                "CRVL 2 # soma_ret",
                "ARMZ 5 # y",
                "CRVL 5 # y",
                "IMPR",
                "DSVS LEND_3",
                "F_soma_1: NADA",
                "CRCT 0",
                "ARMZ 2 # soma_ret",
                "CRVL 0 # a",
                "CRVL 1 # b",
                "SOMA",
                "ARMZ 3 # r",
                "CRVL 3 # r",
                "ARMZ 2 # soma_ret",
                "DSVS F_soma_END_2",
                "F_soma_END_2: RTPR",
                "LEND_3: NADA",
                "PARA",
            ],
        )

    def test_break_and_continue_in_while(self):
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
        self.assertIn("DSVS L2", instructions)  # break direciona ao fim do while
        self.assertTrue(any(instr == "DSVS L1" for instr in instructions))


if __name__ == "__main__":
    unittest.main()
