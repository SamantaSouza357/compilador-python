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


__all__ = [
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

