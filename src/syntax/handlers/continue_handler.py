from __future__ import annotations

from typing import Optional

from lexer.tokens import TokenType
from .base import StatementHandler
from syntax.ast_nodes import ContinueStatement
from syntax.errors import SyntaxErrorCompilador
from syntax.parse_context import ParseContext


class ContinueHandler(StatementHandler):
    def can_handle(self, parser: "SyntaxAnalyzer", ctx: Optional[ParseContext] = None) -> bool:
        return parser.check(TokenType.KEYWORD, "continue")

    def parse(self, parser: "SyntaxAnalyzer", ctx: Optional[ParseContext] = None) -> ContinueStatement:
        if ctx is not None and not ctx.in_loop:
            t = parser.current
            raise SyntaxErrorCompilador(t.linha, "'continue' fora de loop")
        parser.consume(TokenType.KEYWORD, "continue")
        return ContinueStatement()

__all__ = ["ContinueHandler"]
