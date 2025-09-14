from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from syntax.parse_context import ParseContext
from syntax.ast_nodes import ASTNode
if TYPE_CHECKING:
    from syntax.syntax_analyzer import SyntaxAnalyzer


class StatementHandler:
    def can_handle(self, parser: SyntaxAnalyzer, ctx: Optional[ParseContext] = None) -> bool:
        raise NotImplementedError

    def parse(self, parser: SyntaxAnalyzer, ctx: Optional[ParseContext] = None) -> ASTNode:
        raise NotImplementedError


__all__ = ["StatementHandler"]
