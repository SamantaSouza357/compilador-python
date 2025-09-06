import re
from tokens import TokenType, Token, KEYWORDS, SIMBOLOS
from syntax_analyzer import SyntaxAnalyzer


# ====================================
# Python Lexical Analyzer
# ====================================
class LexerPython:
    TOKEN_REGEX = [
        (r"[ \t]+", None),              # ignore spaces/tabs (not at line start)
        (r"#.*", None),                 # comments
        (r"\"[^\"]*\"|\'[^\']*\'", TokenType.STRING),  # strings
        (r"[0-9]+(\.[0-9]+)?", TokenType.NUMBER),      # numbers
        (r"[A-Za-z_][A-Za-z0-9_]*", TokenType.IDENTIFIER), # identifiers and keywords
        (r"[+\-*/%//<>!]+", TokenType.OPERATOR),      # operators
        (r"[=]+", TokenType.ASSIGN),   
        (r"[\(\)\[\]\{\},.:]", TokenType.DELIMITER),   # delimiters
        (r"\r?\n", TokenType.NEWLINE),                    # line break (supports CRLF)
    ]

    def __init__(self, source):
        self.source = source
        self.line = 1
        self.pos = 0

    def get_tokens(self):
        tokens = []
        indent_stack = [0]

        # Iterate line by line, preserving line endings ("\n")
        lines = self.source.splitlines(keepends=True)
        for raw in lines:
            # Strip trailing CR/LF to get logical content
            line = raw.rstrip("\r\n")

            # Blank line or comment-only line?
            stripped = line.lstrip(" \t")
            is_blank = stripped == "" or stripped.startswith("#")

            # If not blank, compute indentation and emit INDENT/DEDENT
            if not is_blank:
                # Count leading spaces/tabs
                i = 0
                indent_count = 0
                while i < len(line) and line[i] in (" ", "\t"):
                    indent_count += 4 if line[i] == "\t" else 1
                    i += 1

                # Adjust indentation stack
                if indent_count > indent_stack[-1]:
                    indent_stack.append(indent_count)
                    tokens.append(Token(TokenType.INDENT, "INDENT", self.line))
                else:
                    while indent_count < indent_stack[-1]:
                        indent_stack.pop()
                        tokens.append(Token(TokenType.DEDENT, "DEDENT", self.line))
                    if indent_count != indent_stack[-1]:
                        raise Exception(f"Erro léxico na linha {self.line}: indentação inconsistente")

                # Tokenize the rest of the line starting at i
                self._tokenize_segment(line[i:], tokens)
            # Even for blank/comment-only lines, emit NEWLINE
            tokens.append(Token(TokenType.NEWLINE, "\n", self.line))
            self.line += 1

        # Close remaining indentation at EOF
        while len(indent_stack) > 1:
            indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, "DEDENT", self.line))

        tokens.append(Token(TokenType.EOF, "EOF", self.line))
        return tokens

    def _tokenize_segment(self, segment, out_tokens):
        # Tokenize a slice of a line (no newline here)
        pos = 0
        n = len(segment)
        while pos < n:
            match = None
            for regex, tipo in self.TOKEN_REGEX:
                if tipo == TokenType.NEWLINE:
                    continue  # do not split here
                pattern = re.compile(regex)
                match = pattern.match(segment, pos)
                if match:
                    lexeme = match.group(0)
                    if tipo:
                        if tipo == TokenType.IDENTIFIER:
                            if lexeme in KEYWORDS:
                                out_tokens.append(Token(TokenType.KEYWORD, lexeme, self.line))
                            else:
                                if len(lexeme) > 20:
                                    raise Exception(
                                        f"Erro léxico na linha {self.line}: identificador com mais de 20 caracteres"
                                    )
                                out_tokens.append(Token(tipo, lexeme, self.line))
                        elif tipo == TokenType.NUMBER:
                            out_tokens.append(Token(tipo, lexeme, self.line))
                        else:
                            out_tokens.append(Token(tipo, lexeme, self.line))
                    pos = match.end(0)
                    if tipo == TokenType.NUMBER and pos < n:
                        nxt = segment[pos]
                        if nxt.isalpha() or nxt == "_":
                            raise Exception(
                                f"Erro léxico na linha {self.line}: identificador iniciando com número"
                            )
                    break
            if not match:
                raise Exception(
                    f"Erro léxico na linha {self.line}: caractere inesperado '{segment[pos]}'"
                )

__all__ = [
    "LexerPython",
    "SyntaxAnalyzer",
]
