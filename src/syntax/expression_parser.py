"""Parser de expressões no estilo Pratt com precedência e associatividade."""

from __future__ import annotations

from typing import Dict, Optional, Tuple, TYPE_CHECKING

from lexer.tokens import TokenType
from syntax.ast_nodes import ASTNode, BinaryOperation, Literal, Identifier, Call, UnaryOp
if TYPE_CHECKING:
    from syntax.syntax_analyzer import SyntaxAnalyzer
from syntax.errors import SyntaxErrorCompilador


class ExpressionParser:
    """Analisa expressões com precedência correta, chamadas e unário '-'.

    Implementação no estilo Pratt: 'parse_expression' analisa uma expressão
    primária e então itera enquanto houver um operador infixo forte o bastante,
    analisando recursivamente o lado direito usando a precedência e
    associatividade do operador.
    """
    # precedência (maior vence) e associatividade (L = esquerda)
    PRECEDENCE: Dict[str, Tuple[int, str]] = {
        # Números maiores ligam mais forte; associatividade "L" = esquerda-para-direita
        "*": (20, "L"),
        "/": (20, "L"),
        "//": (20, "L"),
        "%": (20, "L"),
        "+": (10, "L"),
        "-": (10, "L"),
        "==": (5, "L"),
        "!=": (5, "L"),
        ">": (5, "L"),
        "<": (5, "L"),
        ">=": (5, "L"),
        "<=": (5, "L"),
    }

    def parse_expression(self, parser: SyntaxAnalyzer, min_prec: int = 0) -> ASTNode:
        """Parse an expression with minimum precedence `min_prec`."""
        left = self.parse_primary(parser)
        # Loop para reduzir uma cadeia de operadores binários conforme a precedência
        while True:
            op = self._peek_operator(parser)
            if op is None:
                break
            prec, assoc = self.PRECEDENCE[op]
            if prec < min_prec:
                break
            # consome operador
            parser.ts.advance()
            next_min = prec + 1 if assoc == "L" else prec
            right = self.parse_expression(parser, next_min)
            left = BinaryOperation(left, op, right)
        return left

    def parse_primary(self, parser: SyntaxAnalyzer) -> ASTNode:
        """Parse literals, identifiers, parenthesized expressions, and calls."""
        # Unário menos (prefixo)
        if parser.ts.check(TokenType.OPERATOR) and parser.ts.current.lexema == "-":
            parser.ts.advance()
            # Usa alta precedência para ligar fortemente (maior que a multiplicativa)
            operand = self.parse_expression(parser, 25)
            return UnaryOp("-", operand)

        # Parênteses
        if parser.ts.match(TokenType.DELIMITER, "("):
            expr = self.parse_expression(parser, 0)
            parser.ts.consume(TokenType.DELIMITER, ")", msg="Esperado ')' após expressão")
            return expr

        # booleanos
        if parser.ts.check(TokenType.KEYWORD) and parser.ts.current.lexema in ("True", "False"):
            val = True if parser.ts.current.lexema == "True" else False
            parser.ts.advance()
            return Literal(val)

        # número
        if parser.ts.check(TokenType.NUMBER):
            val = parser.ts.current.lexema
            parser.ts.advance()
            return Literal(float(val) if "." in val else int(val))

        # string
        if parser.ts.check(TokenType.STRING):
            s = parser.ts.current.lexema
            parser.ts.advance()
            return Literal(s)

        # identificador ou chamada
        if parser.ts.check(TokenType.IDENTIFIER):
            current = parser.ts.current
            ident: ASTNode = Identifier(current.lexema, line=current.linha)
            parser.ts.advance()
            # chamadas encadeadas: f(x)(y)
            while parser.ts.match(TokenType.DELIMITER, "("):
                args = []
                if not parser.ts.check(TokenType.DELIMITER, ")"):
                    args.append(self.parse_expression(parser, 0))
                    while parser.ts.match(TokenType.DELIMITER, ","):
                        args.append(self.parse_expression(parser, 0))
                parser.ts.consume(TokenType.DELIMITER, ")", msg="Esperado ')' após argumentos")
                ident = Call(ident, args)
            return ident

        t = parser.ts.current
        raise SyntaxErrorCompilador(t.linha, f"Esperado uma expressão e foi encontrado '{t.tipo}'")

    def _peek_operator(self, parser: SyntaxAnalyzer) -> Optional[str]:
        """Return the next infix operator's lexeme, if any, without consuming."""
        t = parser.ts.current
        if t is None:
            return None
        # operadores mapeados como OPERATOR
        if t.tipo == TokenType.OPERATOR and t.lexema in self.PRECEDENCE:
            return t.lexema
        # alguns comparadores podem vir como ASSIGN: '==', '>=', '<='
        if t.tipo == TokenType.ASSIGN and t.lexema in self.PRECEDENCE:
            return t.lexema
        return None

    def _can_start_expression(self, parser: SyntaxAnalyzer) -> bool:
        """Return True if the current token can start a primary expression."""
        t = parser.ts.current
        if t is None:
            return False
        if t.tipo == TokenType.OPERATOR and t.lexema == "-":
            return True
        if t.tipo in (TokenType.IDENTIFIER, TokenType.NUMBER, TokenType.STRING):
            return True
        if t.tipo == TokenType.KEYWORD and t.lexema in ("True", "False"):
            return True
        if t.tipo == TokenType.DELIMITER and t.lexema == "(":
            return True
        return False


__all__ = ["ExpressionParser"]
