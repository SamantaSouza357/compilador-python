from __future__ import annotations


class SyntaxErrorCompilador(Exception):
    def __init__(self, linha: int, detalhe: str) -> None:
        self.linha: int = linha
        super().__init__(f"Erro de sintaxe na linha {linha}: {detalhe}")


__all__ = ["SyntaxErrorCompilador"]

