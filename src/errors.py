class SyntaxErrorCompilador(Exception):
    def __init__(self, linha, detalhe):
        self.linha = linha
        super().__init__(f"Erro de sintaxe na linha {linha}: {detalhe}")


class LexicalError(Exception):
    def __init__(self, linha: int, detalhe: str):
        self.linha = linha
        super().__init__(f"Erro léxico na linha {linha}: {detalhe}")

__all__ = ["SyntaxErrorCompilador", "LexicalError"]
