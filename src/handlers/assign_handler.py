from tokens import TokenType
from .base import StatementHandler
from ast_nodes import VarAssign


class AssignHandler(StatementHandler):
    def can_handle(self, parser, ctx=None) -> bool:
        return parser.check(TokenType.IDENTIFIER) and parser.at(1).tipo == TokenType.ASSIGN and parser.at(1).lexema == "="

    def parse(self, parser, ctx=None):
        name = parser.consume(TokenType.IDENTIFIER, msg="Esperado identificador").lexema
        parser.consume(TokenType.ASSIGN, "=", msg="Esperado '=' em atribuição")
        expr = parser.expr_parser.parse_expression(parser)
        return VarAssign(name, expr)

__all__ = ["AssignHandler"]
