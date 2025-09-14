from __future__ import annotations

import re
from typing import List

from lexer.tokens import TokenType, Token, KEYWORDS, SIMBOLOS
from lexer.errors import LexicalError


class LexerPython:
    TOKEN_REGEX = [
        (r"[ \t]+", None),              # ignore spaces/tabs (not at line start)
        (r"#.*", None),                 # comments
        (r"\"[^\"]*\"|\'[^\']*\'", TokenType.STRING),  # strings
        (r"[0-9]+(\.[0-9]+)?", TokenType.NUMBER),      # numbers
        (r"[A-Za-z_][A-Za-z0-9_]*", TokenType.IDENTIFIER), # identifiers and keywords
        # multi-char operators first
        (r"(//|==|!=|>=|<=)", TokenType.OPERATOR),
        # single-char operators
        (r"[+\-*/%<>]", TokenType.OPERATOR),
        # assignment '='
        (r"=", TokenType.ASSIGN),
        (r"[\(\)\[\]\{\},.:]", TokenType.DELIMITER),   # delimiters
        (r"\r?\n", TokenType.NEWLINE),                    # line break (supports CRLF)
    ]

    def __init__(self, source: str) -> None:
        self.source: str = source
        self.line: int = 1
        self.pos: int = 0
        # State for triple-quoted block comments
        self._in_block_comment: bool = False
        self._block_comment_delim: str | None = None  # """ or '''

    def get_tokens(self) -> List[Token]:
        tokens: List[Token] = []
        indent_stack: List[int] = [0]

        # Iterate line by line, preserving line endings ("\n")
        lines = self.source.splitlines(keepends=True)
        for raw in lines:
            # Strip trailing CR/LF to get logical content
            line = raw.rstrip("\r\n")

            # Blank line or comment-only line?
            stripped = line.lstrip(" \t")
            is_blank = stripped == "" or stripped.startswith("#")

            # Handle ongoing triple-quoted block comment: ignore content
            if self._in_block_comment:
                # End block comment if the closing delimiter appears on this line
                if self._block_comment_delim and self._block_comment_delim in stripped:
                    self._in_block_comment = False
                    self._block_comment_delim = None
                # Still emit NEWLINE for the line below
            # If not blank and not in block comment start, compute indentation
            elif not is_blank:
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
                        raise LexicalError(self.line, "indentação inconsistente")

                # Tokenize the rest of the line starting at i, or detect block comment
                segment = line[i:]
                # Start of triple-quoted block comment used as comment/docstring
                if segment.startswith('"""') or segment.startswith("'''"):
                    delim = '"""' if segment.startswith('"""') else "'''"
                    self._in_block_comment = True
                    self._block_comment_delim = delim
                    # If it also ends on the same line, close immediately
                    if segment.count(delim) >= 2:
                        self._in_block_comment = False
                        self._block_comment_delim = None
                    # Do not emit any tokens for this content (treated as comment)
                else:
                    self._tokenize_segment(segment, tokens)
            # Even for blank/comment-only lines, emit NEWLINE
            tokens.append(Token(TokenType.NEWLINE, "\n", self.line))
            self.line += 1

        # Close remaining indentation at EOF
        while len(indent_stack) > 1:
            indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, "DEDENT", self.line))

        tokens.append(Token(TokenType.EOF, "EOF", self.line))
        return tokens

    def _tokenize_segment(self, segment: str, out_tokens: List[Token]) -> None:
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
                                    raise LexicalError(
                                        self.line, "identificador com mais de 20 caracteres"
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
                            raise LexicalError(self.line, "identificador iniciando com número")
                    break
            if not match:
                raise LexicalError(self.line, f"caractere inesperado '{segment[pos]}'")

__all__ = [
    "LexerPython",
]
