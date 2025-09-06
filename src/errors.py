class SyntaxErrorCompilador(Exception):
    def __init__(self, linha, detalhe):
        self.linha = linha
        super().__init__(f"Erro de sintaxe na linha {linha}: {detalhe}")

__all__ = ["SyntaxErrorCompilador"]

