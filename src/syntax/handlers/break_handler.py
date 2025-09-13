from __future__ import annotations

from typing import Optional

from lexer.tokens import TokenType
from .base import StatementHandler
from syntax.ast_nodes import BreakStatement
from syntax.errors import SyntaxErrorCompilador
from syntax.parse_context import ParseContext


class BreakHandler(StatementHandler):
    def can_handle(self, parser: "SyntaxAnalyzer", ctx: Optional[ParseContext] = None) -> bool:
        return parser.check(TokenType.KEYWORD, "break")

    def parse(self, parser: "SyntaxAnalyzer", ctx: Optional[ParseContext] = None) -> BreakStatement:
        if ctx is not None and not ctx.in_loop:
            t = parser.current
            raise SyntaxErrorCompilador(t.linha, "'break' fora de loop")
        parser.consume(TokenType.KEYWORD, "break")
        return BreakStatement()

__all__ = ["BreakHandler"]
