"""Tipo de erro léxico levantado pelo léxico com informação de linha."""

from __future__ import annotations


class LexicalError(Exception):
    """Levantado quando o léxico encontra caracteres ou estrutura inválidos."""
    def __init__(self, linha: int, detalhe: str) -> None:
        self.linha: int = linha
        super().__init__(f"Erro léxico na linha {linha}: {detalhe}")


__all__ = ["LexicalError"]
