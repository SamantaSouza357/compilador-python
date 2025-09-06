import re
from tokens import TokenType, Token, KEYWORDS, SIMBOLOS
from syntax_analyzer import SyntaxAnalyzer


# ====================================
# Analisador Léxico para Python
# ====================================
class LexerPython:
    TOKEN_REGEX = [
        (r"[ \t]+", None),              # espaços ignorados (não no início da linha)
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
        indent_stack = [0]

        # Percorre linha a linha, preservando finais \n
        lines = self.codigo.splitlines(keepends=True)
        for raw in lines:
            # Detecta fim de linha e conteúdo sem CRLF
            line = raw.rstrip("\r\n")

            # Verifica linha em branco ou apenas comentário
            stripped = line.lstrip(" \t")
            is_blank = stripped == "" or stripped.startswith("#")

            # Se não é linha em branco, calcula indentação e emite INDENT/DEDENT
            if not is_blank:
                # Conta espaços/tabs do início
                i = 0
                indent_count = 0
                while i < len(line) and line[i] in (" ", "\t"):
                    indent_count += 4 if line[i] == "\t" else 1
                    i += 1

                # Ajuste da pilha
                if indent_count > indent_stack[-1]:
                    indent_stack.append(indent_count)
                    tokens.append(Token(TokenType.INDENT, "INDENT", self.linha))
                else:
                    while indent_count < indent_stack[-1]:
                        indent_stack.pop()
                        tokens.append(Token(TokenType.DEDENT, "DEDENT", self.linha))
                    if indent_count != indent_stack[-1]:
                        raise Exception(f"Erro léxico na linha {self.linha}: indentação inconsistente")

                # Tokeniza o restante da linha a partir de i
                self._tokenize_segment(line[i:], tokens)
            # Mesmo em linha em branco/comentário, emitimos NEWLINE
            tokens.append(Token(TokenType.NEWLINE, "\n", self.linha))
            self.linha += 1

        # Fecha indentação restante no EOF
        while len(indent_stack) > 1:
            indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, "DEDENT", self.linha))

        tokens.append(Token(TokenType.EOF, "EOF", self.linha))
        return tokens

    def _tokenize_segment(self, segment, out_tokens):
        # Tokeniza um trecho de linha sem nova linha
        pos = 0
        n = len(segment)
        while pos < n:
            match = None
            for regex, tipo in self.TOKEN_REGEX:
                if tipo == TokenType.NEWLINE:
                    continue  # não quebramos aqui
                pattern = re.compile(regex)
                match = pattern.match(segment, pos)
                if match:
                    lexema = match.group(0)
                    if tipo:
                        if tipo == TokenType.IDENTIFIER:
                            if lexema in KEYWORDS:
                                out_tokens.append(Token(TokenType.KEYWORD, lexema, self.linha))
                            else:
                                if len(lexema) > 20:
                                    raise Exception(
                                        f"Erro léxico na linha {self.linha}: identificador com mais de 20 caracteres"
                                    )
                                out_tokens.append(Token(tipo, lexema, self.linha))
                        elif tipo == TokenType.NUMBER:
                            out_tokens.append(Token(tipo, lexema, self.linha))
                        else:
                            out_tokens.append(Token(tipo, lexema, self.linha))
                    pos = match.end(0)
                    if tipo == TokenType.NUMBER and pos < n:
                        prox = segment[pos]
                        if prox.isalpha() or prox == "_":
                            raise Exception(
                                f"Erro léxico na linha {self.linha}: identificador iniciando com número"
                            )
                    break
            if not match:
                raise Exception(
                    f"Erro léxico na linha {self.linha}: caractere inesperado '{segment[pos]}'"
                )

__all__ = [
    "LexerPython",
    "SyntaxAnalyzer",
]
