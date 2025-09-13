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
from syntax.parse_context import ParseContext
from syntax.errors import SyntaxErrorCompilador
from syntax.expression_parser import ExpressionParser


class SyntaxAnalyzer:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens: List[Token] = tokens
        self.pos: int = 0
        self.current: Optional[Token] = self.tokens[self.pos] if self.tokens else None
        self._handlers = self._init_statement_chain()
        self.block_parser = BlockParser()
        self.expr_parser = ExpressionParser()

    def _init_statement_chain(self):
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

    # Utilities --------------------------------------------
    def at(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if 0 <= idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def advance(self) -> Optional[Token]:
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current = self.tokens[self.pos]
        return self.current

    def check(self, token_type: Optional[TokenType] = None, lexeme: Optional[str] = None) -> bool:
        t = self.current
        if token_type is not None and t.tipo != token_type:
            return False
        if lexeme is not None and t.lexema != lexeme:
            return False
        return True

    def match(self, token_type: Optional[TokenType] = None, lexeme: Optional[str] = None) -> Optional[Token]:
        if self.check(token_type, lexeme):
            tok = self.current
            self.advance()
            return tok
        return None

    def consume(
        self,
        token_type: Optional[TokenType] = None,
        lexeme: Optional[str] = None,
        msg: str = "Erro de sintaxe",
    ) -> Token:
        if not self.check(token_type, lexeme):
            t = self.current
            expected = f"{token_type.name if token_type else ''} {lexeme or ''}".strip()
            found = f"{t.tipo.name} '{t.lexema}'"
            raise SyntaxErrorCompilador(t.linha, f"{msg}: esperado {expected}, encontrado {found}")
        tok = self.current
        self.advance()
        return tok

    def skip_newlines(self) -> None:
        while self.check(TokenType.NEWLINE):
            self.advance()

    # Entry point --------------------------------------
    def parse(self) -> Program:
        stmts: List[ASTNode] = []
        self.skip_newlines()
        ctx = ParseContext()
        while not self.check(TokenType.EOF):
            stmt = self.parse_one(ctx)
            stmts.append(stmt)
            self.skip_newlines()
        return Program(stmts)

    # Declarations and Statements ---------------------------------
    def parse_one(self, ctx: ParseContext) -> ASTNode:
        for h in self._handlers:
            if h.can_handle(self, ctx):
                return h.parse(self, ctx)
        t = self.current
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
