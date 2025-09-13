from __future__ import annotations

from typing import Optional

from lexer.tokens import TokenType
from .base import StatementHandler
from syntax.ast_nodes import ASTNode
from syntax.parse_context import ParseContext


class ExprHandler(StatementHandler):
    def can_handle(self, parser: "SyntaxAnalyzer", ctx: Optional[ParseContext] = None) -> bool:
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

    def parse(self, parser: "SyntaxAnalyzer", ctx: Optional[ParseContext] = None) -> ASTNode:
        return parser.expr_parser.parse_expression(parser)

__all__ = ["ExprHandler"]

