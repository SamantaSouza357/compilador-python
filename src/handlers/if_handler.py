from tokens import TokenType
from .base import StatementHandler
from ast_nodes import IfStatement


class IfHandler(StatementHandler):
    def can_handle(self, parser, ctx=None) -> bool:
        return parser.check(TokenType.KEYWORD, "if")

    def parse(self, parser, ctx=None):
        parser.consume(TokenType.KEYWORD, "if")
        cond = parser.expr_parser.parse_expression(parser)
        parser.consume(TokenType.DELIMITER, ":", msg="Esperado ':' após condição do if")
        parser.consume(TokenType.NEWLINE, msg="Esperado nova linha após ':'")
        then_blk = parser.block_parser.parse_block(parser, ctx, parser.parse_one)
        else_blk = None
        if parser.check(TokenType.KEYWORD, "else"):
            parser.consume(TokenType.KEYWORD, "else")
            parser.consume(TokenType.DELIMITER, ":", msg="Esperado ':' após 'else'")
            parser.consume(TokenType.NEWLINE, msg="Esperado nova linha após ':'")
            else_blk = parser.block_parser.parse_block(parser, ctx, parser.parse_one)
        return IfStatement(cond, then_blk, else_blk)

__all__ = ["IfHandler"]
