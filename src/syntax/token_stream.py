from __future__ import annotations

from typing import List, Optional

from lexer.tokens import TokenType, Token
from syntax.errors import SyntaxErrorCompilador


class TokenStream:
    """Cursor leve sobre uma lista de tokens.

    Centraliza as operações de navegação de tokens usadas pelo parser:
    olhar adiante, avançar, consumir condicionalmente e pular quebras de linha.
    """

    def __init__(self, tokens: List[Token]) -> None:
        """Inicializa o fluxo no primeiro token.

        - tokens: sequência completa produzida pelo léxico, terminando com EOF.
        - current: aponta para o token na posição interna `pos`.
        """
        self.tokens: List[Token] = tokens
        self.pos: int = 0
        self.current: Optional[Token] = self.tokens[self.pos] if self.tokens else None

    def at(self, offset: int = 0) -> Token:
        """Espia o token em `pos + offset` sem mover o cursor.

        Retorna o último token (tipicamente EOF) se o índice sair dos limites,
        oferecendo um sentinela seguro para inspeção.
        """
        idx = self.pos + offset
        if 0 <= idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def advance(self) -> Optional[Token]:
        """Avança o cursor em um token e retorna o novo atual.

        Se já estiver no último token, mantém a posição e o retorna.
        """
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current = self.tokens[self.pos]
        return self.current

    def check(self, token_type: Optional[TokenType] = None, lexeme: Optional[str] = None) -> bool:
        """Verifica se o token atual corresponde às restrições informadas.

        - token_type: TokenType exigido, se fornecido.
        - lexeme: lexema/string exatos exigidos, se fornecido.
        Retorna True se todas as restrições corresponderem ao token atual.
        """
        t = self.current
        if t is None:
            return False
        if token_type is not None and t.tipo != token_type:
            return False
        if lexeme is not None and t.lexema != lexeme:
            return False
        return True

    def match(self, token_type: Optional[TokenType] = None, lexeme: Optional[str] = None) -> Optional[Token]:
        """Consome e retorna o token atual se ele corresponder; caso contrário None.

        Atalho para o padrão `if check(...): tok=current; advance(); return tok`.
        """
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
        """Exige que o token atual corresponda e avança; caso contrário lança erro.

        - token_type / lexeme: restrições para validar contra o token atual.
        - msg: mensagem base a ser incluída no diagnóstico.
        Em sucesso retorna o token consumido. Em falha lança SyntaxErrorCompilador
        com o número da linha e detalhes.
        """
        if not self.check(token_type, lexeme):
            t = self.current or self.tokens[-1]
            expected = f"{token_type.name if token_type else ''} {lexeme or ''}".strip()
            found = f"{t.tipo.name} '{t.lexema}'"
            raise SyntaxErrorCompilador(t.linha, f"{msg}: esperado {expected}, encontrado {found}")
        tok = self.current 
        self.advance()
        return tok

    def skip_newlines(self) -> None:
        """Avança por quaisquer tokens NEWLINE contíguos."""
        while self.check(TokenType.NEWLINE):
            self.advance()


__all__ = ["TokenStream"]
