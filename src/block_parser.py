from tokens import TokenType
from ast_nodes import Block


class BlockParser:
    def parse_block(self, parser, ctx, parse_one):
        # Allow leading blank lines (NEWLINE) and comment-only lines before INDENT
        parser.skip_newlines()
        # Consume required INDENT and then parse until DEDENT
        parser.consume(TokenType.INDENT, msg="Esperado INDENT para iniciar bloco")
        parser.skip_newlines()
        statements = []
        while not parser.check(TokenType.EOF) and not parser.check(TokenType.DEDENT):
            stmt = parse_one(ctx)
            statements.append(stmt)
            parser.skip_newlines()
        parser.consume(TokenType.DEDENT, msg="Esperado DEDENT para finalizar bloco")
        return Block(statements)

__all__ = ["BlockParser"]
