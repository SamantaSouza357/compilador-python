"""Definições de erros específicos da análise semântica."""

from __future__ import annotations

from typing import Optional


class SemanticError(Exception):
    """Erro levantado quando uma verificação semântica falha."""

    def __init__(self, linha: Optional[int], detalhe: str) -> None:
        self.linha: Optional[int] = linha
        prefixo = "Erro semântico"
        if linha is not None:
            prefixo += f" na linha {linha}"
        super().__init__(f"{prefixo}: {detalhe}")


__all__ = ["SemanticError"]
