from __future__ import annotations

from typing import Optional

from lexer.tokens import TokenType
from .base import StatementHandler
from syntax.ast_nodes import VarAssign
from syntax.parse_context import ParseContext


class AssignHandler(StatementHandler):
    def can_handle(self, parser: "SyntaxAnalyzer", ctx: Optional[ParseContext] = None) -> bool:
        return parser.check(TokenType.IDENTIFIER) and parser.at(1).tipo == TokenType.ASSIGN and parser.at(1).lexema == "="

    def parse(self, parser: "SyntaxAnalyzer", ctx: Optional[ParseContext] = None) -> VarAssign:
        name = parser.consume(TokenType.IDENTIFIER, msg="Esperado identificador").lexema
        parser.consume(TokenType.ASSIGN, "=", msg="Esperado '=' em atribuição")
        expr = parser.expr_parser.parse_expression(parser)
        return VarAssign(name, expr)

__all__ = ["AssignHandler"]

