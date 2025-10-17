"""Tabela de símbolos simples para controlar variáveis declaradas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .errors import SemanticError


@dataclass
class SymbolInfo:
    """Metadados mínimos de uma variável declarada."""

    name: str
    address: int
    tipo: str
    line: Optional[int]


class SymbolTable:
    """Tabela com escopos aninhados e controle de endereços."""

    def __init__(self, parent: Optional["SymbolTable"] = None) -> None:
        self.parent: Optional["SymbolTable"] = parent
        self.symbols: Dict[str, SymbolInfo] = {}
        self._next_address: int = 0

    def declare(self, name: str, line: Optional[int]) -> SymbolInfo:
        """Declara uma nova variável no escopo atual."""
        if name in self.symbols:
            raise SemanticError(line, f"variável '{name}' já declarada")
        info = SymbolInfo(name=name, address=self._next_address, tipo="inteiro", line=line)
        self.symbols[name] = info
        self._next_address += 1
        return info

    def lookup(self, name: str) -> Optional[SymbolInfo]:
        """Procura uma variável neste escopo ou em escopos pais."""
        scope: Optional["SymbolTable"] = self
        while scope is not None:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent
        return None

    def child(self) -> "SymbolTable":
        """Cria um escopo filho ligado a este."""
        return SymbolTable(parent=self)


__all__ = ["SymbolTable", "SymbolInfo"]
