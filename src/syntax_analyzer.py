from tokens import TokenType


class SyntaxErrorCompilador(Exception):
    def __init__(self, linha, detalhe):
        self.linha = linha
        super().__init__(f"Erro de sintaxe na linha {linha}: {detalhe}")


# ====================================
# Nós de AST simples
# ====================================
class ASTNode:
    pass


class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements


class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements


class FunctionDeclaration(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class VarAssign(ASTNode):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr


class IfStatement(ASTNode):
    def __init__(self, cond, then_block, else_block=None):
        self.cond = cond
        self.then_block = then_block
        self.else_block = else_block


class WhileStatement(ASTNode):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body


class ForStatement(ASTNode):
    def __init__(self, var_name, iterable, body):
        self.var_name = var_name
        self.iterable = iterable
        self.body = body


class ReturnStatement(ASTNode):
    def __init__(self, expr):
        self.expr = expr


class BreakStatement(ASTNode):
    pass


class ContinueStatement(ASTNode):
    pass


class BinaryOperation(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class UnaryOp(ASTNode):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand


class Literal(ASTNode):
    def __init__(self, value):
        self.value = value


class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name


class Call(ASTNode):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args


# ====================================
# Analisador Sintático (SyntaxAnalyzer)
# ====================================
class SyntaxAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current = self.tokens[self.pos] if self.tokens else None

    # Utilitários --------------------------------------------
    def at(self, offset=0):
        idx = self.pos + offset
        if 0 <= idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current = self.tokens[self.pos]
        return self.current

    def check(self, tipo=None, lexema=None):
        t = self.current
        if tipo is not None and t.tipo != tipo:
            return False
        if lexema is not None and t.lexema != lexema:
            return False
        return True

    def match(self, tipo=None, lexema=None):
        if self.check(tipo, lexema):
            tok = self.current
            self.advance()
            return tok
        return None

    def consume(self, tipo=None, lexema=None, msg="Erro de sintaxe"):
        if not self.check(tipo, lexema):
            t = self.current
            esperado = f"{tipo.name if tipo else ''} {lexema or ''}".strip()
            encontrado = f"{t.tipo.name} '{t.lexema}'"
            raise SyntaxErrorCompilador(t.linha, f"{msg}: esperado {esperado}, encontrado {encontrado}")
        tok = self.current
        self.advance()
        return tok

    def skip_newlines(self):
        while self.check(TokenType.NEWLINE):
            self.advance()

    # Entrada principal --------------------------------------
    def parse(self):
        stmts = []
        self.skip_newlines()
        while not self.check(TokenType.EOF):
            stmt = self.declaracao_ou_comando()
            stmts.append(stmt)
            # Consome novas linhas entre comandos de topo
            self.skip_newlines()
        return Program(stmts)

    # Declarações e Comandos ---------------------------------
    def declaracao_ou_comando(self):
        # def <id>([params]): <bloco>
        if self.check(TokenType.KEYWORD, "def"):
            return self.declaracao_funcao()

        # if/while/for/return/break/continue
        if self.check(TokenType.KEYWORD, "if"):
            return self.comando_if()
        if self.check(TokenType.KEYWORD, "while"):
            return self.comando_while()
        if self.check(TokenType.KEYWORD, "for"):
            return self.comando_for()
        if self.check(TokenType.KEYWORD, "return"):
            return self.comando_return()
        if self.check(TokenType.KEYWORD, "break"):
            self.consume(TokenType.KEYWORD, "break")
            return BreakStatement()
        if self.check(TokenType.KEYWORD, "continue"):
            self.consume(TokenType.KEYWORD, "continue")
            return ContinueStatement()

        # atribuição ou expressão simples
        if self.check(TokenType.IDENTIFIER) and self.at(1).tipo == TokenType.ASSIGN and self.at(1).lexema == "=":
            return self.declaracao_variavel()

        # expressão/ligação (ex: chamada de função)
        expr = self.expressao()
        return expr

    def declaracao_funcao(self):
        self.consume(TokenType.KEYWORD, "def", msg="Esperado 'def'")
        nome = self.consume(TokenType.IDENTIFIER, msg="Esperado identificador do nome da função").lexema
        self.consume(TokenType.DELIMITER, "(", msg="Esperado '('")
        params = []
        if self.check(TokenType.IDENTIFIER):
            params.append(self.consume(TokenType.IDENTIFIER).lexema)
            while self.match(TokenType.DELIMITER, ","):
                params.append(self.consume(TokenType.IDENTIFIER, msg="Esperado identificador de parâmetro").lexema)
        self.consume(TokenType.DELIMITER, ")", msg="Esperado ')'")
        self.consume(TokenType.DELIMITER, ":", msg="Esperado ':'")
        # Espera quebra de linha antes do bloco
        self.consume(TokenType.NEWLINE, msg="Esperado nova linha após ':'")
        corpo = self._bloco_indent()
        return FunctionDeclaration(nome, params, corpo)

    def declaracao_variavel(self):
        nome = self.consume(TokenType.IDENTIFIER, msg="Esperado identificador").lexema
        self.consume(TokenType.ASSIGN, "=", msg="Esperado '=' em atribuição")
        expr = self.expressao()
        return VarAssign(nome, expr)

    def comando_if(self):
        self.consume(TokenType.KEYWORD, "if")
        cond = self.expressao()
        self.consume(TokenType.DELIMITER, ":", msg="Esperado ':' após condição do if")
        self.consume(TokenType.NEWLINE, msg="Esperado nova linha após ':'")
        then_blk = self._bloco_indent()
        else_blk = None
        if self.check(TokenType.KEYWORD, "else"):
            self.consume(TokenType.KEYWORD, "else")
            self.consume(TokenType.DELIMITER, ":", msg="Esperado ':' após 'else'")
            self.consume(TokenType.NEWLINE, msg="Esperado nova linha após ':'")
            else_blk = self._bloco_indent()
        return IfStatement(cond, then_blk, else_blk)

    def comando_while(self):
        self.consume(TokenType.KEYWORD, "while")
        cond = self.expressao()
        self.consume(TokenType.DELIMITER, ":", msg="Esperado ':' após condição do while")
        self.consume(TokenType.NEWLINE, msg="Esperado nova linha após ':'")
        corpo = self._bloco_indent()
        return WhileStatement(cond, corpo)

    def comando_for(self):
        self.consume(TokenType.KEYWORD, "for")
        var_name = self.consume(TokenType.IDENTIFIER, msg="Esperado identificador do iterador").lexema
        self.consume(TokenType.KEYWORD, "in", msg="Esperado palavra-chave 'in'")
        iterable = self.expressao()
        self.consume(TokenType.DELIMITER, ":", msg="Esperado ':' após expressão do for")
        self.consume(TokenType.NEWLINE, msg="Esperado nova linha após ':'")
        corpo = self._bloco_indent()
        return ForStatement(var_name, iterable, corpo)

    def comando_return(self):
        self.consume(TokenType.KEYWORD, "return")
        expr = self.expressao()
        return ReturnStatement(expr)

    # Bloco ---------------------------------------------------
    def _bloco_indent(self):
        stmts = []
        self.consume(TokenType.INDENT, msg="Esperado INDENT para iniciar bloco")
        # Permite linhas em branco iniciais
        self.skip_newlines()
        while not self.check(TokenType.EOF) and not self.check(TokenType.DEDENT):
            stmt = self.declaracao_ou_comando()
            stmts.append(stmt)
            # Consome NEWLINEs entre comandos dentro do bloco
            self.skip_newlines()
        self.consume(TokenType.DEDENT, msg="Esperado DEDENT para finalizar bloco")
        # Pode haver NEWLINE após DEDENT; não consome aqui para manter consistência dos chamadores
        return Block(stmts)

    # Expressões ---------------------------------------------
    def expressao(self):
        left = self.expressao_simples()
        # operador de comparação opcional
        if self._is_operador_comparacao(self.current):
            op_tok = self.current
            self.advance()
            right = self.expressao_simples()
            return BinaryOperation(left, op_tok.lexema, right)
        return left

    def _is_operador_comparacao(self, tok):
        if tok.tipo == TokenType.OPERATOR and tok.lexema in ("==", "!=", ">", "<", ">=", "<="):
            return True
        # Nosso léxico classifica '==' como ASSIGN por usar [=]+; trate aqui
        if tok.tipo == TokenType.ASSIGN and tok.lexema in ("==", ">=", "<="):
            return True
        return False

    def expressao_simples(self):
        expr = self.termo()
        while self.check(TokenType.OPERATOR) and self.current.lexema in ("+", "-"):
            op = self.current.lexema
            self.advance()
            right = self.termo()
            expr = BinaryOperation(expr, op, right)
        return expr

    def termo(self):
        expr = self.fator()
        while self.check(TokenType.OPERATOR) and self.current.lexema in ("*", "/", "//", "%"):
            op = self.current.lexema
            self.advance()
            right = self.fator()
            expr = BinaryOperation(expr, op, right)
        return expr

    def fator(self):
        # Parênteses
        if self.match(TokenType.DELIMITER, "("):
            expr = self.expressao()
            self.consume(TokenType.DELIMITER, ")", msg="Esperado ')' após expressão")
            return expr

        # booleanos True | False (como KEYWORD)
        if self.check(TokenType.KEYWORD) and self.current.lexema in ("True", "False"):
            val = True if self.current.lexema == "True" else False
            self.advance()
            return Literal(val)

        # número
        if self.check(TokenType.NUMBER):
            val = self.current.lexema
            self.advance()
            return Literal(float(val) if "." in val else int(val))

        # string
        if self.check(TokenType.STRING):
            s = self.current.lexema
            self.advance()
            return Literal(s)

        # identificador ou chamada de função
        if self.check(TokenType.IDENTIFIER):
            ident = Identifier(self.current.lexema)
            self.advance()
            if self.match(TokenType.DELIMITER, "("):
                args = []
                if not self.check(TokenType.DELIMITER, ")"):
                    args.append(self.expressao())
                    while self.match(TokenType.DELIMITER, ","):
                        args.append(self.expressao())
                self.consume(TokenType.DELIMITER, ")", msg="Esperado ')' após argumentos")
                return Call(ident, args)
            return ident

        t = self.current
        raise SyntaxErrorCompilador(t.linha, f"fator inesperado '{t.lexema}'")


__all__ = [
    "SyntaxAnalyzer",
    "SyntaxErrorCompilador",
    "ASTNode",
    "Program",
    "Block",
    "FunctionDeclaration",
    "VarAssign",
    "IfStatement",
    "WhileStatement",
    "ForStatement",
    "ReturnStatement",
    "BreakStatement",
    "ContinueStatement",
    "BinaryOperation",
    "UnaryOp",
    "Literal",
    "Identifier",
    "Call",
]
