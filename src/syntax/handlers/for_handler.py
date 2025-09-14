from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from lexer.tokens import TokenType
from .base import StatementHandler
from syntax.ast_nodes import ForStatement
if TYPE_CHECKING:
    from syntax.syntax_analyzer import SyntaxAnalyzer
from syntax.parse_context import ParseContext


class ForHandler(StatementHandler):
    def can_handle(self, parser: SyntaxAnalyzer, ctx: Optional[ParseContext] = None) -> bool:
        return parser.ts.check(TokenType.KEYWORD, "for")

    def parse(self, parser: SyntaxAnalyzer, ctx: Optional[ParseContext] = None) -> ForStatement:
        parser.ts.consume(TokenType.KEYWORD, "for")
        var_name = parser.ts.consume(
            TokenType.IDENTIFIER, msg="Esperado identificador do iterador"
        ).lexema
        parser.ts.consume(TokenType.KEYWORD, "in", msg="Esperado palavra-chave 'in'")
        iterable = parser.expr_parser.parse_expression(parser)
        parser.ts.consume(TokenType.DELIMITER, ":", msg="Esperado ':' após expressão do for")
        parser.ts.consume(TokenType.NEWLINE, msg="Esperado nova linha após ':'")
        child_ctx = ctx.child(in_loop=True) if ctx is not None else None
        body = parser.block_parser.parse_block(parser, child_ctx, parser.parse_one)
        return ForStatement(var_name, iterable, body)

__all__ = ["ForHandler"]
