"""Analisador sintático de alto nível que orquestra o parsing de comandos e a construção da AST."""

from __future__ import annotations

from typing import List, Optional

from lexer.tokens import TokenType, Token
from syntax.ast_nodes import (
    ASTNode,
    Program,
    Block,
    FunctionDeclaration,
    VarAssign,
    IfStatement,
    WhileStatement,
    ForStatement,
    ReturnStatement,
    BreakStatement,
    ContinueStatement,
    BinaryOperation,
    UnaryOp,
    Literal,
    Identifier,
    Call,
)
from syntax.handlers import (
    DefHandler,
    IfHandler,
    WhileHandler,
    ForHandler,
    ReturnHandler,
    BreakHandler,
    ContinueHandler,
    AssignHandler,
    ExprHandler,
)
from syntax.block_parser import BlockParser
from syntax.handlers.base import StatementHandler
from syntax.parse_context import ParseContext
from syntax.errors import SyntaxErrorCompilador
from syntax.expression_parser import ExpressionParser
from syntax.token_stream import TokenStream


class SyntaxAnalyzer:
    """Converte uma lista de tokens em um Program (AST) usando uma cadeia de handlers."""

    def __init__(self, tokens: List[Token]) -> None:
        """Cria o estado do parser e componentes auxiliares para comandos e expressões."""
        self.ts = TokenStream(tokens)
        self._handlers = self._init_statement_chain()
        self.block_parser = BlockParser()
        self.expr_parser = ExpressionParser()

    def _init_statement_chain(self) -> List[StatementHandler]:
        """Retorna a lista ordenada de handlers consultados para cada comando.

        A ordem importa: construções mais específicas (por exemplo, 'def', 'if')
        são testadas antes do handler genérico de expressão. Cada handler usa
        o token atual para decidir se pode analisar; o primeiro que corresponder
        é responsável por consumir os tokens apropriados.
        """
        return [
            DefHandler(),
            IfHandler(),
            WhileHandler(),
            ForHandler(),
            ReturnHandler(),
            BreakHandler(),
            ContinueHandler(),
            AssignHandler(),
            ExprHandler(),
        ]
    
    # Entry point --------------------------------------
    def parse(self) -> Program:
        """Analisa todo o fluxo de tokens em um nó Program.

        Pulamos NEWLINEs iniciais (linhas em branco) e, em seguida, delegamos
        repetidamente para 'parse_one' até encontrar EOF, pulando NEWLINEs
        após cada comando para permitir espaçamento vertical entre comandos.
        """
        stmts: List[ASTNode] = []
        self.ts.skip_newlines()
        ctx = ParseContext()
        while not self.ts.check(TokenType.EOF):
            stmt = self.parse_one(ctx)
            stmts.append(stmt)
            self.ts.skip_newlines()
        return Program(stmts)

    # Declarations and Statements ---------------------------------
    def parse_one(self, ctx: ParseContext) -> ASTNode:
        """Analisa um único comando usando o primeiro handler que corresponder.

        O token atual é inspecionado por cada handler em sequência. O handler
        que reivindica o token consome todos os tokens daquele comando e
        retorna um nó da AST. Se nenhum corresponder, um erro de sintaxe é lançado.
        """
        for h in self._handlers:
            if h.can_handle(self, ctx):
                return h.parse(self, ctx)
        t = self.ts.current
        raise SyntaxErrorCompilador(t.linha, f"comando inesperado '{t.lexema}'")

__all__ = [
    "SyntaxAnalyzer",
    "SyntaxErrorCompilador",
    "Program",
    "Block",
    "FunctionDeclaration",
    "VarAssign",
    "IfStatement",
    "WhileStatement",
    "ForStatement",
    "ReturnStatement",
    "BreakStatement",
    "ContinueStatement",
    "BinaryOperation",
    "UnaryOp",
    "Literal",
    "Identifier",
    "Call",
]
