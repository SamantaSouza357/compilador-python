from tokens import TokenType
from ast_nodes import (
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
from handlers import (
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
from block_parser import BlockParser
from parse_context import ParseContext
from errors import SyntaxErrorCompilador
from expression_parser import ExpressionParser


class SyntaxAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current = self.tokens[self.pos] if self.tokens else None
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
    def at(self, offset=0):
        idx = self.pos + offset
        if 0 <= idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current = self.tokens[self.pos]
        return self.current

    def check(self, token_type=None, lexeme=None):
        t = self.current
        if token_type is not None and t.tipo != token_type:
            return False
        if lexeme is not None and t.lexema != lexeme:
            return False
        return True

    def match(self, token_type=None, lexeme=None):
        if self.check(token_type, lexeme):
            tok = self.current
            self.advance()
            return tok
        return None

    def consume(self, token_type=None, lexeme=None, msg="Erro de sintaxe"):
        if not self.check(token_type, lexeme):
            t = self.current
            expected = f"{token_type.name if token_type else ''} {lexeme or ''}".strip()
            found = f"{t.tipo.name} '{t.lexema}'"
            raise SyntaxErrorCompilador(t.linha, f"{msg}: esperado {expected}, encontrado {found}")
        tok = self.current
        self.advance()
        return tok

    def skip_newlines(self):
        while self.check(TokenType.NEWLINE):
            self.advance()

    # Entry point --------------------------------------
    def parse(self):
        stmts = []
        self.skip_newlines()
        ctx = ParseContext()
        while not self.check(TokenType.EOF):
            stmt = self.parse_one(ctx)
            stmts.append(stmt)
            self.skip_newlines()
        return Program(stmts)

    # Declarations and Statements ---------------------------------
    def parse_one(self, ctx: ParseContext):
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
