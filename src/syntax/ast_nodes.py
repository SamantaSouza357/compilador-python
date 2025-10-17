"""Definições dos nós de AST usados pelo analisador sintático."""

from __future__ import annotations

from typing import List, Optional, Union


class ASTNode:
    """Classe base para todos os nós da AST."""
    pass


class Program(ASTNode):
    """Nó raiz contendo os comandos de alto nível."""
    def __init__(self, statements: List[ASTNode]) -> None:
        self.statements: List[ASTNode] = statements
    def __repr__(self) -> str:
        return f"Program(statements={self.statements!r})"


class Block(ASTNode):
    """Sequência de comandos com o mesmo nível de indentação."""
    def __init__(self, statements: List[ASTNode]) -> None:
        self.statements: List[ASTNode] = statements
    def __repr__(self) -> str:
        return f"Block(statements={self.statements!r})"


class FunctionDeclaration(ASTNode):
    """Declaração de função com nome, parâmetros e bloco do corpo."""
    def __init__(self, name: str, params: List[str], body: Block) -> None:
        self.name: str = name
        self.params: List[str] = params
        self.body: Block = body
    def __repr__(self) -> str:
        return f"FunctionDeclaration(name={self.name!r}, params={self.params!r}, body={self.body!r})"


class VarAssign(ASTNode):
    """Atribuição de variável: name = expr."""
    def __init__(self, name: str, expr: ASTNode, line: Optional[int] = None) -> None:
        self.name: str = name
        self.expr: ASTNode = expr
        self.line: Optional[int] = line
    def __repr__(self) -> str:
        return f"VarAssign(name={self.name!r}, expr={self.expr!r})"


class IfStatement(ASTNode):
    """Condicional if/else com blocos then/else."""
    def __init__(self, cond: ASTNode, then_block: Block, else_block: Optional[Block] = None) -> None:
        self.cond: ASTNode = cond
        self.then_block: Block = then_block
        self.else_block: Optional[Block] = else_block
    def __repr__(self) -> str:
        return (
            f"IfStatement(cond={self.cond!r}, then_block={self.then_block!r}, "
            f"else_block={self.else_block!r})"
        )


class WhileStatement(ASTNode):
    """Laço while com condição e bloco de corpo."""
    def __init__(self, cond: ASTNode, body: Block) -> None:
        self.cond: ASTNode = cond
        self.body: Block = body
    def __repr__(self) -> str:
        return f"WhileStatement(cond={self.cond!r}, body={self.body!r})"


class ForStatement(ASTNode):
    """Laço for-in sobre um iterável com variável de laço e corpo."""
    def __init__(self, var_name: str, iterable: ASTNode, body: Block, line: Optional[int] = None) -> None:
        self.var_name: str = var_name
        self.iterable: ASTNode = iterable
        self.body: Block = body
        self.line: Optional[int] = line
    def __repr__(self) -> str:
        return (
            f"ForStatement(var_name={self.var_name!r}, iterable={self.iterable!r}, "
            f"body={self.body!r})"
        )


class ReturnStatement(ASTNode):
    """Comando return com expressão opcional."""
    def __init__(self, expr: Optional[ASTNode]) -> None:
        self.expr: Optional[ASTNode] = expr
    def __repr__(self) -> str:
        return f"ReturnStatement(expr={self.expr!r})"


class BreakStatement(ASTNode):
    """Interrompe o laço mais próximo."""
    pass


class ContinueStatement(ASTNode):
    """Continua para a próxima iteração do laço."""
    pass


class BinaryOperation(ASTNode):
    """Operação binária infixa: left <op> right."""
    def __init__(self, left: ASTNode, op: str, right: ASTNode) -> None:
        self.left: ASTNode = left
        self.op: str = op
        self.right: ASTNode = right
    def __repr__(self) -> str:
        return f"BinaryOperation(left={self.left!r}, op={self.op!r}, right={self.right!r})"


class UnaryOp(ASTNode):
    """Operação unária prefixa, por exemplo, -x."""
    def __init__(self, op: str, operand: ASTNode) -> None:
        self.op: str = op
        self.operand: ASTNode = operand
    def __repr__(self) -> str:
        return f"UnaryOp(op={self.op!r}, operand={self.operand!r})"


class Literal(ASTNode):
    """Valor literal: int, float, string ou boolean."""
    def __init__(self, value: Union[int, float, str, bool]) -> None:
        self.value: Union[int, float, str, bool] = value
    def __repr__(self) -> str:
        return f"Literal(value={self.value!r})"


class Identifier(ASTNode):
    """Referência de identificador pelo nome."""
    def __init__(self, name: str, line: Optional[int] = None) -> None:
        self.name: str = name
        self.line: Optional[int] = line
    def __repr__(self) -> str:
        return f"Identifier(name={self.name!r})"


class Call(ASTNode):
    """Chamada no estilo de função: callee(args...)."""
    def __init__(self, callee: ASTNode, args: List[ASTNode]) -> None:
        self.callee: ASTNode = callee
        self.args: List[ASTNode] = args
    def __repr__(self) -> str:
        return f"Call(callee={self.callee!r}, args={self.args!r})"


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
