import re
from enum import Enum

# ====================================
# Definição de tipos de tokens
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
    ASSIGN = 'ASSIGN'


# Palavras reservadas do Python
KEYWORDS = {
    "def", "class", "if", "else", "elif", "while", "for", "in",
    "return", "import", "from", "as", "try", "except", "finally",
    "with", "pass", "break", "continue", "and", "or", "not", "is",
    "lambda", "yield", "global", "nonlocal", "assert", "raise",
    "del", "True", "False", "None"
}

# Tabela de símbolos (delimitadores)
SIMBOLOS = {
    "(": "ABRE_PARENTESES", ")": "FECHA_PARENTESES",
    "[": "ABRE_COL", "]": "FECHA_COL",
    "{": "ABRE_CH", "}": "FECHA_CH",
    ":": "DOIS_PONTOS", ",": "VIRG",
    ".": "PONTO", "=": "ATRIB"
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


# ====================================
# Analisador Léxico para Python
# ====================================
class LexerPython:
    TOKEN_REGEX = [
        (r"[ \t]+", None),              # espaços ignorados
        (r"#.*", None),                 # comentários
        (r"\"[^\"]*\"|\'[^\']*\'", TokenType.STRING),  # strings
        (r"[0-9]+(\.[0-9]+)?", TokenType.NUMBER),      # números
        (r"[A-Za-z_][A-Za-z0-9_]*", TokenType.IDENTIFIER), # identificadores e keywords
        (r"[+\-*/%//<>!]+", TokenType.OPERATOR),      # operadores
        (r"[=]+", TokenType.ASSIGN),   
        (r"[\(\)\[\]\{\},.:]", TokenType.DELIMITER),   # delimitadores
        (r"\n", TokenType.NEWLINE),                    # quebra de linha
    ]

    def __init__(self, codigo):
        self.codigo = codigo
        self.linha = 1
        self.pos = 0

    def get_tokens(self):
        tokens = []
        while self.pos < len(self.codigo):
            match = None
            for regex, tipo in self.TOKEN_REGEX:
                pattern = re.compile(regex)
                match = pattern.match(self.codigo, self.pos)
                if match:
                    lexema = match.group(0)
                    if tipo:
                        if tipo == TokenType.IDENTIFIER and lexema in KEYWORDS:
                            tokens.append(Token(TokenType.KEYWORD, lexema, self.linha))
                        else:
                            tokens.append(Token(tipo, lexema, self.linha))
                    self.pos = match.end(0)
                    if "\n" in lexema:
                        self.linha += lexema.count("\n")
                    break
            if not match:
                raise Exception(f"Erro léxico na linha {self.linha}: caractere inesperado '{self.codigo[self.pos]}'")
        tokens.append(Token(TokenType.EOF, "EOF", self.linha))
        return tokens


# ====================================
# Exemplo de uso
# ====================================
if __name__ == "__main__":
    caminho = "exemplo.py"

    with open(caminho, "r", encoding="utf-8") as f:
        codigo = f.read()

    lexer = LexerPython(codigo)
    tokens = lexer.get_tokens()

    for t in tokens:
        print(t)
