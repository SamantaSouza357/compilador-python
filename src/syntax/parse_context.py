"""Flags contextuais simples para validar o posicionamento de comandos durante o parse."""

from __future__ import annotations

from typing import Optional


class ParseContext:
    """Indica se o parser está dentro de um laço ou de uma função."""

    def __init__(self, in_loop: bool = False, in_function: bool = False) -> None:
        self.in_loop: bool = in_loop
        self.in_function: bool = in_function

    def child(self, *, in_loop: Optional[bool] = None, in_function: Optional[bool] = None) -> "ParseContext":
        """Cria um contexto derivado, sobrescrevendo flags quando fornecidas."""
        return ParseContext(
            in_loop=self.in_loop if in_loop is None else in_loop,
            in_function=self.in_function if in_function is None else in_function,
        )

__all__ = ["ParseContext"]
