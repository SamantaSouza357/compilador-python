import argparse
from compilador import LexerPython


def main():
    parser = argparse.ArgumentParser(
        description="Analisador léxico simples para Python."
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

    lexer = LexerPython(codigo)
    tokens = lexer.get_tokens()

    for t in tokens:
        print(t)

if __name__ == "__main__":
    main()
