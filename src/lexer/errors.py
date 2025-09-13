from __future__ import annotations


class LexicalError(Exception):
    def __init__(self, linha: int, detalhe: str) -> None:
        self.linha: int = linha
        super().__init__(f"Erro léxico na linha {linha}: {detalhe}")


__all__ = ["LexicalError"]

