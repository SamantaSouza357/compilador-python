"""Interface abstrata de manipuladores de comandos usada pelo parser."""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from syntax.parse_context import ParseContext
from syntax.ast_nodes import ASTNode
if TYPE_CHECKING:
    from syntax.syntax_analyzer import SyntaxAnalyzer


class StatementHandler:
    """Manipulador que reconhece e analisa um tipo específico de comando."""

    def can_handle(self, parser: SyntaxAnalyzer, ctx: Optional[ParseContext] = None) -> bool:
        """Retorna True se este manipulador puder analisar no token atual."""
        raise NotImplementedError

    def parse(self, parser: SyntaxAnalyzer, ctx: Optional[ParseContext] = None) -> ASTNode:
        """Analisa o comando e retorna seu nó de AST."""
        raise NotImplementedError


__all__ = ["StatementHandler"]
