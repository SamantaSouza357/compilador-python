from enum import Enum

# ====================================
# Token types and data definitions
# ====================================
class TokenType(Enum):
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
    def __init__(self, tipo, lexema, linha):
        self.tipo = tipo
        self.lexema = lexema
        self.linha = linha

    def __str__(self):
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
