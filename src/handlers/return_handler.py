from tokens import TokenType
from .base import StatementHandler
from ast_nodes import ReturnStatement


class ReturnHandler(StatementHandler):
    def can_handle(self, parser, ctx=None) -> bool:
        return parser.check(TokenType.KEYWORD, "return")

    def parse(self, parser, ctx=None):
        parser.consume(TokenType.KEYWORD, "return")
        # Optional expression: if the next token can start an expression, parse it; otherwise return None
        if parser.expr_parser._can_start_expression(parser):
            expr = parser.expr_parser.parse_expression(parser)
        else:
            expr = None
        return ReturnStatement(expr)

__all__ = ["ReturnHandler"]
