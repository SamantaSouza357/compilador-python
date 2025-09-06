import re
from tokens import TokenType, Token, KEYWORDS, SIMBOLOS


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
        (r"\r?\n", TokenType.NEWLINE),                    # quebra de linha (suporta CRLF)
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
                        if tipo == TokenType.IDENTIFIER:
                            if lexema in KEYWORDS:
                                tokens.append(Token(TokenType.KEYWORD, lexema, self.linha))
                            else:
                                # Regra: identificadores com no máximo 20 caracteres
                                if len(lexema) > 20:
                                    raise Exception(
                                        f"Erro léxico na linha {self.linha}: identificador com mais de 20 caracteres"
                                    )
                                tokens.append(Token(tipo, lexema, self.linha))
                        elif tipo == TokenType.NUMBER:
                            tokens.append(Token(tipo, lexema, self.linha))
                        else:
                            tokens.append(Token(tipo, lexema, self.linha))
                    self.pos = match.end(0)
                    # Regra adicional: número não pode ser seguido imediatamente por letra ou '_'
                    if tipo == TokenType.NUMBER and self.pos < len(self.codigo):
                        prox = self.codigo[self.pos]
                        if prox.isalpha() or prox == "_":
                            raise Exception(
                                f"Erro léxico na linha {self.linha}: identificador iniciando com número"
                            )
                    if "\n" in lexema:
                        self.linha += lexema.count("\n")
                    break
            if not match:
                raise Exception(f"Erro léxico na linha {self.linha}: caractere inesperado '{self.codigo[self.pos]}'")
        tokens.append(Token(TokenType.EOF, "EOF", self.linha))
        return tokens
