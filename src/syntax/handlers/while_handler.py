from __future__ import annotations

from typing import Optional

from lexer.tokens import TokenType
from .base import StatementHandler
from syntax.ast_nodes import WhileStatement
from syntax.parse_context import ParseContext


class WhileHandler(StatementHandler):
    def can_handle(self, parser: "SyntaxAnalyzer", ctx: Optional[ParseContext] = None) -> bool:
        return parser.check(TokenType.KEYWORD, "while")

    def parse(self, parser: "SyntaxAnalyzer", ctx: Optional[ParseContext] = None) -> WhileStatement:
        parser.consume(TokenType.KEYWORD, "while")
        cond = parser.expr_parser.parse_expression(parser)
        parser.consume(TokenType.DELIMITER, ":", msg="Esperado ':' após condição do while")
        parser.consume(TokenType.NEWLINE, msg="Esperado nova linha após ':'")
        child_ctx = ctx.child(in_loop=True) if ctx is not None else None
        body = parser.block_parser.parse_block(parser, child_ctx, parser.parse_one)
        return WhileStatement(cond, body)

__all__ = ["WhileHandler"]

