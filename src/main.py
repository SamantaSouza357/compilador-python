import argparse
from lexer import LexerPython
from syntax import SyntaxAnalyzer

def main():
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
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    main()
