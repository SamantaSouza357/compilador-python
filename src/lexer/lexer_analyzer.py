"""Um analisador léxico que produz tokens e marcações de indentação.

Reconhece identificadores, números, strings, operadores, delimitadores, NEWLINE
e emite INDENT/DEDENT com base no espaço em branco no início de cada linha.
"""

from __future__ import annotations

import re
from typing import List

from lexer.tokens import TokenType, Token, KEYWORDS, SIMBOLOS
from lexer.errors import LexicalError


class LexerPython:
    """Converte o código-fonte em uma lista plana de tokens, incluindo INDENT/DEDENT."""
    TOKEN_REGEX = [
        # A ordem importa: padrões mais específicos/com vários caracteres primeiro
        (r"[ \t]+", None),              # ignora espaços/tabs (não no início da linha)
        (r"#.*", None),                 # comentários
        (r"\"[^\"]*\"|\'[^\']*\'", TokenType.STRING),  # strings
        (r"[0-9]+(\.[0-9]+)?", TokenType.NUMBER),      # números
        (r"[A-Za-z_][A-Za-z0-9_]*", TokenType.IDENTIFIER), # identificadores e palavras-chave
        # operadores com mais de um caractere primeiro
        (r"(//|==|!=|>=|<=)", TokenType.OPERATOR),
        # operadores de um caractere
        (r"[+\-*/%<>]", TokenType.OPERATOR),
        # atribuição '='
        (r"=", TokenType.ASSIGN),
        (r"[\(\)\[\]\{\},.:]", TokenType.DELIMITER),   # delimitadores
        (r"\r?\n", TokenType.NEWLINE),                    # quebra de linha (suporta CRLF)
    ]

    def __init__(self, source: str) -> None:
        """Inicializa um novo léxico com o texto completo do código-fonte."""
        self.source: str = source
        self.line: int = 1
        self.pos: int = 0
        # State for triple-quoted block comments
        self._in_block_comment: bool = False
        self._block_comment_delim: str | None = None  # """ or '''

    def get_tokens(self) -> List[Token]:
        """Scan the input and return the list of tokens ending with EOF."""
        tokens: List[Token] = []
        indent_stack: List[int] = [0]

        # Itera linha a linha, preservando as quebras ("\n")
        lines = self.source.splitlines(keepends=True)
        for raw in lines:
            # Remove CR/LF do final para obter o conteúdo lógico
            line = raw.rstrip("\r\n")

            # Linha em branco ou apenas comentário?
            stripped = line.lstrip(" \t")
            is_blank = stripped == "" or stripped.startswith("#")

            # Tratamento de comentário em bloco com aspas triplas: ignora o conteúdo
            if self._in_block_comment:
                # Encerra o bloco se o delimitador de fechamento aparecer nesta linha
                if self._block_comment_delim and self._block_comment_delim in stripped:
                    self._in_block_comment = False
                    self._block_comment_delim = None
                # Mesmo assim emite NEWLINE para a linha
            # Se não for em branco e não estiver em comentário de bloco, calcula a indentação
            elif not is_blank:
                # Conta espaços/tabs iniciais
                i = 0
                indent_count = 0
                while i < len(line) and line[i] in (" ", "\t"):
                    indent_count += 4 if line[i] == "\t" else 1
                    i += 1

                # Ajusta a pilha de indentação
                if indent_count > indent_stack[-1]:
                    indent_stack.append(indent_count)
                    tokens.append(Token(TokenType.INDENT, "INDENT", self.line))
                else:
                    while indent_count < indent_stack[-1]:
                        indent_stack.pop()
                        tokens.append(Token(TokenType.DEDENT, "DEDENT", self.line))
                    if indent_count != indent_stack[-1]:
                        raise LexicalError(self.line, "indentação inconsistente")

                # Tokeniza o restante da linha a partir de i, ou detecta comentário em bloco
                segment = line[i:]
                # Início de comentário em bloco com aspas triplas usado como comentário/docstring
                if segment.startswith('"""') or segment.startswith("'''"):
                    delim = '"""' if segment.startswith('"""') else "'''"
                    self._in_block_comment = True
                    self._block_comment_delim = delim
                    # Se também terminar na mesma linha, encerra imediatamente
                    if segment.count(delim) >= 2:
                        self._in_block_comment = False
                        self._block_comment_delim = None
                    # Não emite tokens para este conteúdo (tratado como comentário)
                else:
                    self._tokenize_segment(segment, tokens)
            # Mesmo para linhas em branco/somente comentários, emite NEWLINE para o parser usar
            tokens.append(Token(TokenType.NEWLINE, "\n", self.line))
            self.line += 1

        # Fecha indentação restante no EOF
        while len(indent_stack) > 1:
            indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, "DEDENT", self.line))

        tokens.append(Token(TokenType.EOF, "EOF", self.line))
        return tokens

    def _tokenize_segment(self, segment: str, out_tokens: List[Token]) -> None:
        """Tokeniza um trecho de uma linha (sem caracteres de quebra de linha)."""
        pos = 0
        n = len(segment)
        while pos < n:
            match = None
            for regex, tipo in self.TOKEN_REGEX:
                if tipo == TokenType.NEWLINE:
                    continue  # não separar aqui
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
