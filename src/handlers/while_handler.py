from tokens import TokenType
from .base import StatementHandler
from ast_nodes import WhileStatement


class WhileHandler(StatementHandler):
    def can_handle(self, parser, ctx=None) -> bool:
        return parser.check(TokenType.KEYWORD, "while")

    def parse(self, parser, ctx=None):
        parser.consume(TokenType.KEYWORD, "while")
        cond = parser.expr_parser.parse_expression(parser)
        parser.consume(TokenType.DELIMITER, ":", msg="Esperado ':' após condição do while")
        parser.consume(TokenType.NEWLINE, msg="Esperado nova linha após ':'")
        child_ctx = ctx.child(in_loop=True) if ctx is not None else None
        body = parser.block_parser.parse_block(parser, child_ctx, parser.parse_one)
        return WhileStatement(cond, body)

__all__ = ["WhileHandler"]
