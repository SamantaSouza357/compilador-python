from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from lexer.tokens import TokenType
from .base import StatementHandler
from syntax.ast_nodes import ContinueStatement
if TYPE_CHECKING:
    from syntax.syntax_analyzer import SyntaxAnalyzer
from syntax.errors import SyntaxErrorCompilador
from syntax.parse_context import ParseContext


class ContinueHandler(StatementHandler):
    def can_handle(self, parser: SyntaxAnalyzer, ctx: Optional[ParseContext] = None) -> bool:
        return parser.ts.check(TokenType.KEYWORD, "continue")

    def parse(self, parser: SyntaxAnalyzer, ctx: Optional[ParseContext] = None) -> ContinueStatement:
        if ctx is not None and not ctx.in_loop:
            t = parser.ts.current
            raise SyntaxErrorCompilador(t.linha, "'continue' fora de loop")
        parser.ts.consume(TokenType.KEYWORD, "continue")
        return ContinueStatement()

__all__ = ["ContinueHandler"]
