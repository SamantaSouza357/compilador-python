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
    def __init__(self, tokens: List[Token]) -> None:
        self.ts = TokenStream(tokens)
        self._handlers = self._init_statement_chain()
        self.block_parser = BlockParser()
        self.expr_parser = ExpressionParser()

    def _init_statement_chain(self) -> List[StatementHandler]:
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
