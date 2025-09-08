from tokens import TokenType
from .base import StatementHandler


class ExprHandler(StatementHandler):
    def can_handle(self, parser, ctx=None) -> bool:
        t = parser.current
        if t is None:
            return False
        # allow leading unary '-' expressions
        if t.tipo == TokenType.OPERATOR and t.lexema == "-":
            return True
        if t.tipo in (TokenType.IDENTIFIER, TokenType.NUMBER, TokenType.STRING):
            return True
        if t.tipo == TokenType.KEYWORD and t.lexema in ("True", "False"):
            return True
        if t.tipo == TokenType.DELIMITER and t.lexema == "(":
            return True
        return False

    def parse(self, parser, ctx=None):
        return parser.expr_parser.parse_expression(parser)

__all__ = ["ExprHandler"]
