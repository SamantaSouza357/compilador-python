"""Definições de tokens para o léxico (tipos, palavras-chave, símbolos e classe Token)."""

from __future__ import annotations

from enum import Enum


class TokenType(Enum):
    """Todos os tipos de token produzidos pelo léxico."""
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    OPERATOR = "OPERATOR"
    DELIMITER = "DELIMITER"
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    EOF = "EOF"
    ASSIGN = "ASSIGN"


# Python reserved keywords
KEYWORDS = {
    "def",
    "class",
    "if",
    "else",
    "elif",
    "while",
    "for",
    "in",
    "return",
    "import",
    "from",
    "as",
    "try",
    "except",
    "finally",
    "with",
    "pass",
    "break",
    "continue",
    "and",
    "or",
    "not",
    "is",
    "lambda",
    "yield",
    "global",
    "nonlocal",
    "assert",
    "raise",
    "del",
    "True",
    "False",
    "None",
}


# Symbol table (delimiters)
SIMBOLOS = {
    "(": "ABRE_PARENTESES",
    ")": "FECHA_PARENTESES",
    "[": "ABRE_COL",
    "]": "FECHA_COL",
    "{": "ABRE_CH",
    "}": "FECHA_CH",
    ":": "DOIS_PONTOS",
    ",": "VIRG",
    ".": "PONTO",
    "=": "ATRIB",
}


class Token:
    """Um token léxico com tipo, lexema original e linha de origem."""

    def __init__(self, tipo: TokenType, lexema: str, linha: int) -> None:
        self.tipo: TokenType = tipo
        self.lexema: str = lexema
        self.linha: int = linha

    def __str__(self) -> str:
        nome = self.tipo.value

        if self.tipo == TokenType.DELIMITER and self.lexema in SIMBOLOS:
            nome = SIMBOLOS[self.lexema]

        elif self.tipo == TokenType.KEYWORD:
            nome = self.lexema.upper()

        elif self.tipo == TokenType.IDENTIFIER:
            nome = "IDENTIF"

        elif self.tipo == TokenType.ASSIGN:
            nome = "ATRIBUICAO"

        elif self.tipo == TokenType.NEWLINE:
            return f"Linha: {self.linha} – atomo: NEWLINE"

        return f"Linha: {self.linha} – atomo: {nome:<15} lexema: {self.lexema}"


__all__ = [
    "TokenType",
    "Token",
    "KEYWORDS",
    "SIMBOLOS",
]
