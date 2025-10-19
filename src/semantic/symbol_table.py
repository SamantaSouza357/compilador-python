"""Tabela de símbolos aprimorada com suporte a escopos e endereços relativos."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
from .errors import SemanticError


@dataclass
class SymbolInfo:
    """Metadados de uma variável declarada."""
    name: str
    address: int            # Endereço relativo ao escopo atual
    tipo: str
    line: Optional[int]


class SymbolTable:
    """Tabela de símbolos hierárquica (com suporte a escopos aninhados)."""

    def __init__(self, parent: Optional["SymbolTable"] = None) -> None:
        self.parent: Optional["SymbolTable"] = parent
        self.symbols: Dict[str, SymbolInfo] = {}
        self._next_address: int = 0  # contador local de endereços dentro do escopo

    # ----------------------------------------------------------
    # Declaração de variáveis
    # ----------------------------------------------------------
    def declare(self, name: str, line: Optional[int], tipo: str = "inteiro") -> SymbolInfo:
        """Declara uma nova variável no escopo atual."""
        if name in self.symbols:
            raise SemanticError(line, f"variável '{name}' já declarada neste escopo")
        info = SymbolInfo(name=name, address=self._next_address, tipo=tipo, line=line)
        self.symbols[name] = info
        self._next_address += 1
        return info

    # ----------------------------------------------------------
    # Consulta de símbolos
    # ----------------------------------------------------------
    def lookup(self, name: str) -> Optional[SymbolInfo]:
        """
        Procura uma variável neste escopo ou em escopos pais.
        Retorna o primeiro símbolo encontrado de acordo com a hierarquia.
        """
        scope: Optional["SymbolTable"] = self
        while scope is not None:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent
        return None

    def lookup_local(self, name: str) -> Optional[SymbolInfo]:
        """Procura uma variável apenas no escopo atual (sem olhar escopos pais)."""
        return self.symbols.get(name)

    # ----------------------------------------------------------
    # Endereçamento e hierarquia
    # ----------------------------------------------------------
    def get_full_address(self, name: str) -> Optional[int]:
        """
        Retorna o endereço absoluto de uma variável considerando
        todos os deslocamentos de escopos pais.

        Exemplo:
            Escopo global: 3 variáveis  -> endereços 0, 1, 2
            Escopo interno: 2 variáveis -> endereços relativos 0, 1 (absolutos 3, 4)
        """
        offset = 0
        scope = self
        # acumula deslocamento de todos os escopos acima
        while scope.parent is not None:
            offset += scope.parent._next_address
            scope = scope.parent

        # volta a procurar o símbolo real
        scope = self
        while scope is not None:
            if name in scope.symbols:
                return scope.symbols[name].address + offset
            scope = scope.parent
        return None

    # ----------------------------------------------------------
    # Utilidades de escopo
    # ----------------------------------------------------------
    def var_count(self) -> int:
        """Número de variáveis declaradas neste escopo."""
        return len(self.symbols)

    def child(self) -> "SymbolTable":
        """Cria um escopo filho ligado a este."""
        return SymbolTable(parent=self)

    def all_symbols(self) -> Dict[str, SymbolInfo]:
        """Retorna todos os símbolos visíveis neste escopo (incluindo pais)."""
        result: Dict[str, SymbolInfo] = {}
        scope = self
        while scope is not None:
            result.update(scope.symbols)
            scope = scope.parent
        return result


__all__ = ["SymbolTable", "SymbolInfo"]