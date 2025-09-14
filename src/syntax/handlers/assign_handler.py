from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from lexer.tokens import TokenType
from .base import StatementHandler
from syntax.ast_nodes import VarAssign
if TYPE_CHECKING:
    from syntax.syntax_analyzer import SyntaxAnalyzer
from syntax.parse_context import ParseContext


class AssignHandler(StatementHandler):
    """Analisa atribuições de variável no formato name = expression."""
    def can_handle(self, parser: SyntaxAnalyzer, ctx: Optional[ParseContext] = None) -> bool:
        return parser.ts.check(TokenType.IDENTIFIER) and parser.ts.at(1).tipo == TokenType.ASSIGN and parser.ts.at(1).lexema == "="

    def parse(self, parser: SyntaxAnalyzer, ctx: Optional[ParseContext] = None) -> VarAssign:
        name = parser.ts.consume(TokenType.IDENTIFIER, msg="Esperado identificador").lexema
        parser.ts.consume(TokenType.ASSIGN, "=", msg="Esperado '=' em atribuição")
        expr = parser.expr_parser.parse_expression(parser)
        return VarAssign(name, expr)

__all__ = ["AssignHandler"]
