"""Ponto de entrada da linha de comando para executar o compilador (gera código MEPA)."""

import argparse
from lexer import LexerPython
from syntax import SyntaxAnalyzer
from semantic import SemanticAnalyzer
from codegen import MepaGenerator, CodeGenerationError


def main():
    """Executa as etapas do compilador e imprime apenas o código MEPA final."""
    parser = argparse.ArgumentParser(description="Compilador para Python → MEPA.")
    parser.add_argument(
        "--file", "-f",
        required=True,
        help="Caminho do arquivo fonte a ser compilado."
    )
    args = parser.parse_args()

    try:
        # Lê o código-fonte
        with open(args.file, "r", encoding="utf-8") as f:
            codigo = f.read()

        # Etapas do compilador (sem prints intermediários)
        lexer = LexerPython(codigo)
        tokens = lexer.get_tokens()
        syntax = SyntaxAnalyzer(tokens)
        ast = syntax.parse()
        semantic = SemanticAnalyzer(ast)
        semantic.analyze()

        # Geração de código MEPA
        generator = MepaGenerator()
        mepa_code = generator.generate(ast)

        # Exibe apenas o resultado final
        for instr in mepa_code:
            print(instr)

    except CodeGenerationError as e:
        print(f"Erro na geração de código: {e}")
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    main()
