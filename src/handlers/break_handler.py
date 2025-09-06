from tokens import TokenType
from .base import StatementHandler
from ast_nodes import BreakStatement
from errors import SyntaxErrorCompilador


class BreakHandler(StatementHandler):
    def can_handle(self, parser, ctx=None) -> bool:
        return parser.check(TokenType.KEYWORD, "break")

    def parse(self, parser, ctx=None):
        if ctx is not None and not ctx.in_loop:
            t = parser.current
            raise SyntaxErrorCompilador(t.linha, "'break' fora de loop")
        parser.consume(TokenType.KEYWORD, "break")
        return BreakStatement()

__all__ = ["BreakHandler"]
