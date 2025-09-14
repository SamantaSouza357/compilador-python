from __future__ import annotations

from typing import List, Optional

from lexer.tokens import TokenType, Token
from syntax.errors import SyntaxErrorCompilador


class TokenStream:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens: List[Token] = tokens
        self.pos: int = 0
        self.current: Optional[Token] = self.tokens[self.pos] if self.tokens else None

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
        if t is None:
            return False
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
            t = self.current or self.tokens[-1]
            expected = f"{token_type.name if token_type else ''} {lexeme or ''}".strip()
            found = f"{t.tipo.name} '{t.lexema}'"
            raise SyntaxErrorCompilador(t.linha, f"{msg}: esperado {expected}, encontrado {found}")
        tok = self.current  # type: ignore[assignment]
        self.advance()
        return tok  # type: ignore[return-value]

    def skip_newlines(self) -> None:
        while self.check(TokenType.NEWLINE):
            self.advance()


__all__ = ["TokenStream"]

