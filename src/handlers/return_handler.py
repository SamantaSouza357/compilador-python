from tokens import TokenType
from .base import StatementHandler
from ast_nodes import ReturnStatement


class ReturnHandler(StatementHandler):
    def can_handle(self, parser, ctx=None) -> bool:
        return parser.check(TokenType.KEYWORD, "return")

    def parse(self, parser, ctx=None):
        parser.consume(TokenType.KEYWORD, "return")
        expr = parser.expr_parser.parse_expression(parser)
        return ReturnStatement(expr)

__all__ = ["ReturnHandler"]
