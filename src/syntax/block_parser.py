"""Utilitários para analisar blocos de comandos baseados em indentação."""

from __future__ import annotations

from typing import Callable, Optional

from lexer.tokens import TokenType
from syntax.ast_nodes import Block, ASTNode
from syntax.parse_context import ParseContext
from typing import TYPE_CHECKING
if TYPE_CHECKING:  # avoid circular import at runtime
    from syntax.syntax_analyzer import SyntaxAnalyzer


class BlockParser:
    """Analisa um bloco delimitado por INDENT/DEDENT, pulando linhas em branco."""

    def parse_block(
        self,
        parser: SyntaxAnalyzer,
        ctx: Optional[ParseContext],
        parse_one: Callable[[ParseContext], ASTNode],
    ) -> Block:
        """Consome INDENT, analisa comandos até DEDENT e retorna um Block.

        NEWLINEs iniciais dentro do bloco são ignorados para permitir
        comentários e linhas em branco antes do primeiro comando. Os comandos
        terminam quando um token DEDENT é encontrado no nível de indentação atual.
        """
        # Allow leading blank lines (NEWLINE) and comment-only lines before INDENT
        parser.ts.skip_newlines()
        # Consume required INDENT and then parse until DEDENT
        parser.ts.consume(TokenType.INDENT, msg="Esperado INDENT para iniciar bloco")
        parser.ts.skip_newlines()
        statements: list[ASTNode] = []
        # Continua analisando comandos até encontrar um DEDENT deste bloco
        while not parser.ts.check(TokenType.EOF) and not parser.ts.check(TokenType.DEDENT):
            stmt = parse_one(ctx)
            statements.append(stmt)
            parser.ts.skip_newlines()
        parser.ts.consume(TokenType.DEDENT, msg="Esperado DEDENT para finalizar bloco")
        return Block(statements)

__all__ = ["BlockParser"]
