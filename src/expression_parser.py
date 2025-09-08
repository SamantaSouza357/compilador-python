from tokens import TokenType
from ast_nodes import BinaryOperation, Literal, Identifier, Call, UnaryOp
from errors import SyntaxErrorCompilador


class ExpressionParser:
    # precedência (maior vence) e associatividade (L = esquerda)
    PRECEDENCE = {
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

    def parse_expression(self, parser, min_prec: int = 0):
        left = self.parse_primary(parser)
        while True:
            op = self._peek_operator(parser)
            if op is None:
                break
            prec, assoc = self.PRECEDENCE[op]
            if prec < min_prec:
                break
            # consome operador
            parser.advance()
            next_min = prec + 1 if assoc == "L" else prec
            right = self.parse_expression(parser, next_min)
            left = BinaryOperation(left, op, right)
        return left

    def parse_primary(self, parser):
        # Unary minus (prefix)
        if parser.check(TokenType.OPERATOR) and parser.current.lexema == "-":
            parser.advance()
            # Use a high precedence to bind tightly (higher than multiplicative)
            operand = self.parse_expression(parser, 25)
            return UnaryOp("-", operand)

        # Parênteses
        if parser.match(TokenType.DELIMITER, "("):
            expr = self.parse_expression(parser, 0)
            parser.consume(TokenType.DELIMITER, ")", msg="Esperado ')' após expressão")
            return expr

        # booleanos
        if parser.check(TokenType.KEYWORD) and parser.current.lexema in ("True", "False"):
            val = True if parser.current.lexema == "True" else False
            parser.advance()
            return Literal(val)

        # número
        if parser.check(TokenType.NUMBER):
            val = parser.current.lexema
            parser.advance()
            return Literal(float(val) if "." in val else int(val))

        # string
        if parser.check(TokenType.STRING):
            s = parser.current.lexema
            parser.advance()
            return Literal(s)

        # identificador ou chamada
        if parser.check(TokenType.IDENTIFIER):
            ident = Identifier(parser.current.lexema)
            parser.advance()
            # chamadas encadeadas: f(x)(y)
            while parser.match(TokenType.DELIMITER, "("):
                args = []
                if not parser.check(TokenType.DELIMITER, ")"):
                    args.append(self.parse_expression(parser, 0))
                    while parser.match(TokenType.DELIMITER, ","):
                        args.append(self.parse_expression(parser, 0))
                parser.consume(TokenType.DELIMITER, ")", msg="Esperado ')' após argumentos")
                ident = Call(ident, args)
            return ident

        t = parser.current
        raise SyntaxErrorCompilador(t.linha, f"Esperado uma expressão e foi encontrado '{t.tipo}'")

    def _peek_operator(self, parser):
        t = parser.current
        if t is None:
            return None
        # operadores mapeados como OPERATOR
        if t.tipo == TokenType.OPERATOR and t.lexema in self.PRECEDENCE:
            return t.lexema
        # alguns comparadores podem vir como ASSIGN: '==', '>=', '<='
        if t.tipo == TokenType.ASSIGN and t.lexema in self.PRECEDENCE:
            return t.lexema
        return None

    def _can_start_expression(self, parser) -> bool:
        t = parser.current
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
