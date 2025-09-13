from __future__ import annotations

from typing import Optional

from lexer.tokens import TokenType
from .base import StatementHandler
from syntax.ast_nodes import IfStatement
from syntax.parse_context import ParseContext


class IfHandler(StatementHandler):
    def can_handle(self, parser: "SyntaxAnalyzer", ctx: Optional[ParseContext] = None) -> bool:
        return parser.check(TokenType.KEYWORD, "if")

    def parse(self, parser: "SyntaxAnalyzer", ctx: Optional[ParseContext] = None) -> IfStatement:
        # if <expr> : NEWLINE INDENT <stmts> DEDENT (else : NEWLINE INDENT <stmts> DEDENT)?
        parser.consume(TokenType.KEYWORD, "if", msg="Esperado 'if'")
        cond = parser.expr_parser.parse_expression(parser)
        parser.consume(TokenType.DELIMITER, ":", msg="Esperado ':' após condição do if")
        parser.consume(TokenType.NEWLINE, msg="Esperado nova linha após ':'")
        then_block = parser.block_parser.parse_block(parser, ctx, parser.parse_one)

        # Optional else branch
        parser.skip_newlines()
        else_block = None
        if parser.check(TokenType.KEYWORD, "else"):
            parser.consume(TokenType.KEYWORD, "else")
            parser.consume(TokenType.DELIMITER, ":", msg="Esperado ':' após 'else'")
            parser.consume(TokenType.NEWLINE, msg="Esperado nova linha após ':'")
            else_block = parser.block_parser.parse_block(parser, ctx, parser.parse_one)

        return IfStatement(cond, then_block, else_block)

__all__ = ["IfHandler"]

