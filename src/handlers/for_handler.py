from tokens import TokenType
from .base import StatementHandler
from ast_nodes import ForStatement


class ForHandler(StatementHandler):
    def can_handle(self, parser, ctx=None) -> bool:
        return parser.check(TokenType.KEYWORD, "for")

    def parse(self, parser, ctx=None):
        parser.consume(TokenType.KEYWORD, "for")
        var_name = parser.consume(
            TokenType.IDENTIFIER, msg="Esperado identificador do iterador"
        ).lexema
        parser.consume(TokenType.KEYWORD, "in", msg="Esperado palavra-chave 'in'")
        iterable = parser.expr_parser.parse_expression(parser)
        parser.consume(TokenType.DELIMITER, ":", msg="Esperado ':' após expressão do for")
        parser.consume(TokenType.NEWLINE, msg="Esperado nova linha após ':'")
        child_ctx = ctx.child(in_loop=True) if ctx is not None else None
        body = parser.block_parser.parse_block(parser, child_ctx, parser.parse_one)
        return ForStatement(var_name, iterable, body)

__all__ = ["ForHandler"]
