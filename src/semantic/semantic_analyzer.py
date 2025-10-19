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
    """Executa a análise semântica garantindo consistência das variáveis e escopos aninhados."""

    # Funções nativas que não precisam ser declaradas
    BUILTIN_FUNCTIONS: Set[str] = {"print", "input", "range"}

    def __init__(self, program: Program) -> None:
        self.program = program
        self._declared_functions: Set[str] = set()

    # ---------------------------------------------------------------
    def analyze(self) -> None:
        """Inicia a verificação semântica de todo o programa."""
        self._declared_functions = {
            stmt.name for stmt in self.program.statements if isinstance(stmt, FunctionDeclaration)
        }

        global_scope = SymbolTable()
        self._analyze_program(self.program, global_scope)

    # ---------------------------------------------------------------
    def _analyze_program(self, program: Program, scope: SymbolTable) -> None:
        """Analisa as declarações globais e o corpo principal."""
        for stmt in program.statements:
            if isinstance(stmt, FunctionDeclaration):
                self._analyze_function(stmt, scope)
            else:
                self._analyze_statement(stmt, scope)

    # ---------------------------------------------------------------
    def _analyze_function(self, func: FunctionDeclaration, parent_scope: SymbolTable) -> None:
        """Analisa uma função (cria novo escopo)."""
        func_scope = parent_scope.child()

        # Declara parâmetros
        for param in func.params:
            func_scope.declare(param, line=None)

        # Analisa corpo da função
        self._analyze_block(func.body.statements, func_scope, allow_declarations=True)

    # ---------------------------------------------------------------
    def _analyze_block(
        self,
        statements: Iterable[ASTNode],
        scope: SymbolTable,
        *,
        allow_declarations: bool,
    ) -> None:
        """Analisa um bloco de comandos, criando um escopo local."""
        local_scope = scope.child()
        body_started = not allow_declarations

        for stmt in statements:
            if isinstance(stmt, VarAssign) and not body_started:
                self._declare_variable(local_scope, stmt)
                self._analyze_expression(stmt.expr, local_scope)
            else:
                body_started = True
                self._analyze_statement(stmt, local_scope)

    # ---------------------------------------------------------------
    def _analyze_statement(self, stmt: ASTNode, scope: SymbolTable) -> None:
        """Analisa uma instrução de alto nível."""
        if isinstance(stmt, VarAssign):
            # Declara variável se não existir ainda no escopo atual
            if scope.lookup_local(stmt.name) is None:
                self._declare_variable(scope, stmt)
            self._analyze_expression(stmt.expr, scope)

        elif isinstance(stmt, IfStatement):
            self._analyze_expression(stmt.cond, scope)
            # Novo escopo para o bloco do IF
            self._analyze_block(stmt.then_block.statements, scope, allow_declarations=True)
            if stmt.else_block is not None:
                # Novo escopo separado para o ELSE
                self._analyze_block(stmt.else_block.statements, scope, allow_declarations=True)

        elif isinstance(stmt, WhileStatement):
            self._analyze_expression(stmt.cond, scope)
            self._analyze_block(stmt.body.statements, scope, allow_declarations=True)

        elif isinstance(stmt, ForStatement):
            # Verifica o iterável (ex: range(...))
            self._analyze_expression(stmt.iterable, scope)
            loop_scope = scope.child()
            loop_scope.declare(stmt.var_name, stmt.line)
            self._analyze_block(stmt.body.statements, loop_scope, allow_declarations=True)

        elif isinstance(stmt, ReturnStatement):
            if stmt.expr is not None:
                self._analyze_expression(stmt.expr, scope)

        elif isinstance(stmt, (BreakStatement, ContinueStatement)):
            # Verificados dentro de laços em nível sintático
            return

        else:
            # Expressões como chamadas de função ou literais soltos
            self._analyze_expression(stmt, scope)

    # ---------------------------------------------------------------
    def _analyze_expression(
        self, expr: ASTNode, scope: SymbolTable, *, context: str = "value"
    ) -> None:
        """Analisa expressões recursivamente."""
        if isinstance(expr, Literal):
            return

        if isinstance(expr, Identifier):
            # Funções builtin ou declaradas globalmente
            if expr.name in self.BUILTIN_FUNCTIONS or expr.name in self._declared_functions:
                return
            self._ensure_declared(scope, expr.name, expr.line)
            return

        if isinstance(expr, Call):
            # Analisa chamada de função
            if isinstance(expr.callee, Identifier):
                callee_name = expr.callee.name
                if (
                    callee_name not in self.BUILTIN_FUNCTIONS
                    and callee_name not in self._declared_functions
                ):
                    raise SemanticError(
                        expr.line, f"função '{callee_name}' não declarada"
                    )
            else:
                self._analyze_expression(expr.callee, scope, context="call_callee")

            # Analisa argumentos
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
            self._analyze_statement(expr, scope)
            return

        raise SemanticError(None, f"nó de expressão desconhecido: {type(expr).__name__}")

    # ---------------------------------------------------------------
    def _declare_variable(self, scope: SymbolTable, assign: VarAssign) -> None:
        """Declara uma variável no escopo atual."""
        scope.declare(assign.name, assign.line)

    def _ensure_declared(self, scope: SymbolTable, name: str, line: Optional[int]) -> None:
        """Verifica se a variável foi declarada em algum escopo pai."""
        if scope.lookup(name) is None:
            raise SemanticError(line, f"variável '{name}' não declarada")


__all__ = ["SemanticAnalyzer"]
