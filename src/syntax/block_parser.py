from __future__ import annotations

from typing import Callable, Optional

from lexer.tokens import TokenType
from syntax.ast_nodes import Block, ASTNode
from syntax.parse_context import ParseContext
from typing import TYPE_CHECKING
if TYPE_CHECKING:  # avoid circular import at runtime
    from syntax.syntax_analyzer import SyntaxAnalyzer


class BlockParser:
    def parse_block(
        self,
        parser: SyntaxAnalyzer,
        ctx: Optional[ParseContext],
        parse_one: Callable[[ParseContext], ASTNode],
    ) -> Block:
        # Allow leading blank lines (NEWLINE) and comment-only lines before INDENT
        parser.skip_newlines()
        # Consume required INDENT and then parse until DEDENT
        parser.consume(TokenType.INDENT, msg="Esperado INDENT para iniciar bloco")
        parser.skip_newlines()
        statements: list[ASTNode] = []
        while not parser.check(TokenType.EOF) and not parser.check(TokenType.DEDENT):
            stmt = parse_one(ctx)
            statements.append(stmt)
            parser.skip_newlines()
        parser.consume(TokenType.DEDENT, msg="Esperado DEDENT para finalizar bloco")
        return Block(statements)

__all__ = ["BlockParser"]
