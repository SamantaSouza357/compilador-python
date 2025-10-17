"""Verificações semânticas sobre a AST produzida pelo parser."""

from __future__ import annotations

from typing import Iterable, Optional, Set

from syntax.ast_nodes import (
    ASTNode,
    Program,
    FunctionDeclaration,
    VarAssign,
    IfStatement,
    WhileStatement,
    ForStatement,
    ReturnStatement,
    BreakStatement,
    ContinueStatement,
    BinaryOperation,
    UnaryOp,
    Literal,
    Identifier,
    Call,
)

from .errors import SemanticError
from .symbol_table import SymbolTable


class SemanticAnalyzer:
    """Executa a análise semântica garantindo consistência das variáveis."""

    BUILTIN_FUNCTIONS: Set[str] = {"print", "input", "range"}

    def __init__(self, program: Program) -> None:
        self.program = program
        self._declared_functions: Set[str] = set()

    def analyze(self) -> None:
        """Ponto de entrada público para validar o programa completo."""
        self._declared_functions = {
            stmt.name for stmt in self.program.statements if isinstance(stmt, FunctionDeclaration)
        }
        global_scope = SymbolTable()
        self._analyze_program(self.program, global_scope)

    # -- Program / Blocks -------------------------------------------------
    def _analyze_program(self, program: Program, scope: SymbolTable) -> None:
        """Processa declarações globais e o corpo do programa."""
        body_started = False
        declaration_started = False
        for stmt in program.statements:
            if isinstance(stmt, FunctionDeclaration):
                if declaration_started:
                    body_started = True
                self._analyze_function(stmt, scope)
            elif isinstance(stmt, VarAssign) and not body_started:
                declaration_started = True
                self._declare_variable(scope, stmt)
                self._analyze_expression(stmt.expr, scope)
            else:
                # Qualquer outro comando inicia o corpo do programa
                body_started = True
                self._analyze_statement(stmt, scope)

    def _analyze_block(
        self,
        statements: Iterable[ASTNode],
        scope: SymbolTable,
        *,
        allow_declarations: bool,
    ) -> None:
        """Analisa uma sequência de comandos dentro de um escopo."""
        body_started = not allow_declarations
        for stmt in statements:
            if isinstance(stmt, VarAssign) and not body_started:
                self._declare_variable(scope, stmt)
                self._analyze_expression(stmt.expr, scope)
            else:
                body_started = True
                self._analyze_statement(stmt, scope)

    # -- Statements -------------------------------------------------------
    def _analyze_function(self, func: FunctionDeclaration, parent_scope: SymbolTable) -> None:
        func_scope = parent_scope.child()
        for param in func.params:
            func_scope.declare(param, line=None)
        self._analyze_block(func.body.statements, func_scope, allow_declarations=True)

    def _analyze_statement(self, stmt: ASTNode, scope: SymbolTable) -> None:
        if isinstance(stmt, VarAssign):
            self._ensure_declared(scope, stmt.name, stmt.line)
            self._analyze_expression(stmt.expr, scope)
        elif isinstance(stmt, IfStatement):
            self._analyze_expression(stmt.cond, scope)
            self._analyze_block(stmt.then_block.statements, scope.child(), allow_declarations=False)
            if stmt.else_block is not None:
                self._analyze_block(
                    stmt.else_block.statements,
                    scope.child(),
                    allow_declarations=False,
                )
        elif isinstance(stmt, WhileStatement):
            self._analyze_expression(stmt.cond, scope)
            self._analyze_block(stmt.body.statements, scope.child(), allow_declarations=False)
        elif isinstance(stmt, ForStatement):
            self._analyze_expression(stmt.iterable, scope)
            loop_scope = scope.child()
            loop_scope.declare(stmt.var_name, stmt.line)
            self._analyze_block(stmt.body.statements, loop_scope, allow_declarations=False)
        elif isinstance(stmt, ReturnStatement):
            if stmt.expr is not None:
                self._analyze_expression(stmt.expr, scope)
        elif isinstance(stmt, (BreakStatement, ContinueStatement)):
            return
        else:
            # Expressões usadas como comando
            self._analyze_expression(stmt, scope)

    # -- Expressions ------------------------------------------------------
    def _analyze_expression(self, expr: ASTNode, scope: SymbolTable, *, context: str = "value") -> None:
        if isinstance(expr, Literal):
            return
        if isinstance(expr, Identifier):
            if context == "call_callee":
                return
            if expr.name in self.BUILTIN_FUNCTIONS or expr.name in self._declared_functions:
                return
            self._ensure_declared(scope, expr.name, expr.line)
            return
        if isinstance(expr, Call):
            callee_context = "call_callee" if context == "call_callee" else "value"
            self._analyze_expression(expr.callee, scope, context=callee_context)
            for arg in expr.args:
                self._analyze_expression(arg, scope)
            return
        if isinstance(expr, BinaryOperation):
            self._analyze_expression(expr.left, scope)
            self._analyze_expression(expr.right, scope)
            return
        if isinstance(expr, UnaryOp):
            self._analyze_expression(expr.operand, scope)
            return
        if isinstance(expr, VarAssign):
            # Não deve ocorrer em expressões, mas analisamos conservadoramente
            self._analyze_statement(expr, scope)
            return
        # Outros nós que não representam expressões válidas
        raise SemanticError(None, "nó de expressão desconhecido durante análise semântica")

    # -- Auxiliares -------------------------------------------------------
    def _declare_variable(self, scope: SymbolTable, assign: VarAssign) -> None:
        scope.declare(assign.name, assign.line)

    def _ensure_declared(self, scope: SymbolTable, name: str, line: Optional[int]) -> None:
        if scope.lookup(name) is None:
            raise SemanticError(line, f"variável '{name}' não declarada")


__all__ = ["SemanticAnalyzer"]
