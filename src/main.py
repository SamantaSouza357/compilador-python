"""Ponto de entrada da linha de comando para executar o léxico, parser e semântica."""

import argparse
from lexer import LexerPython
from syntax import SyntaxAnalyzer
from semantic import SemanticAnalyzer
from codegen import MepaGenerator, CodeGenerationError

def main():
    """Lê os argumentos, realiza a análise léxica e sintática e imprime os resultados."""
    parser = argparse.ArgumentParser(
        description="Compilador para Python."
    )
    parser.add_argument(
        "--file",
        "-f",
        required=True,
        help="Caminho do arquivo fonte a ser analisado",
    )
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        codigo = f.read()

    try:
        lexer = LexerPython(codigo)
        tokens = lexer.get_tokens()

        for t in tokens:
            print(t)

        syntax = SyntaxAnalyzer(tokens)
        ast = syntax.parse()
        print("Programa sintaticamente correto.")
        semantic = SemanticAnalyzer(ast)
        semantic.analyze()
        print("Programa semanticamente correto.")
        generator = MepaGenerator()
        mepa_code = generator.generate(ast)
        print("Código MEPA gerado:")
        for instr in mepa_code:
            print(instr)
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    main()
