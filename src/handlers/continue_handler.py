from tokens import TokenType
from .base import StatementHandler
from ast_nodes import ContinueStatement
from errors import SyntaxErrorCompilador


class ContinueHandler(StatementHandler):
    def can_handle(self, parser, ctx=None) -> bool:
        return parser.check(TokenType.KEYWORD, "continue")

    def parse(self, parser, ctx=None):
        if ctx is not None and not ctx.in_loop:
            t = parser.current
            raise SyntaxErrorCompilador(t.linha, "'continue' fora de loop")
        parser.consume(TokenType.KEYWORD, "continue")
        return ContinueStatement()

__all__ = ["ContinueHandler"]
