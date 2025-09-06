from tokens import TokenType
from .base import StatementHandler
from ast_nodes import FunctionDeclaration


class DefHandler(StatementHandler):
    def can_handle(self, parser, ctx=None) -> bool:
        return parser.check(TokenType.KEYWORD, "def")

    def parse(self, parser, ctx=None):
        parser.consume(TokenType.KEYWORD, "def", msg="Esperado 'def'")
        name = parser.consume(
            TokenType.IDENTIFIER, msg="Esperado identificador do nome da função"
        ).lexema
        parser.consume(TokenType.DELIMITER, "(", msg="Esperado '('")
        params = []
        if parser.check(TokenType.IDENTIFIER):
            params.append(parser.consume(TokenType.IDENTIFIER).lexema)
            while parser.match(TokenType.DELIMITER, ","):
                params.append(
                    parser.consume(
                        TokenType.IDENTIFIER, msg="Esperado identificador de parâmetro"
                    ).lexema
                )
        parser.consume(TokenType.DELIMITER, ")", msg="Esperado ')'")
        parser.consume(TokenType.DELIMITER, ":", msg="Esperado ':'")
        parser.consume(TokenType.NEWLINE, msg="Esperado nova linha após ':'")
        child_ctx = ctx.child(in_function=True) if ctx is not None else None
        body = parser.block_parser.parse_block(parser, child_ctx, parser.parse_one)
        return FunctionDeclaration(name, params, body)

__all__ = ["DefHandler"]
