from __future__ import annotations

from typing import Optional

from lexer.tokens import TokenType
from .base import StatementHandler
from syntax.ast_nodes import ReturnStatement
from syntax.parse_context import ParseContext


class ReturnHandler(StatementHandler):
    def can_handle(self, parser: "SyntaxAnalyzer", ctx: Optional[ParseContext] = None) -> bool:
        return parser.check(TokenType.KEYWORD, "return")

    def parse(self, parser: "SyntaxAnalyzer", ctx: Optional[ParseContext] = None) -> ReturnStatement:
        parser.consume(TokenType.KEYWORD, "return")
        # Optional expression: if the next token can start an expression, parse it; otherwise return None
        if parser.expr_parser._can_start_expression(parser):
            expr = parser.expr_parser.parse_expression(parser)
        else:
            expr = None
        return ReturnStatement(expr)

__all__ = ["ReturnHandler"]

