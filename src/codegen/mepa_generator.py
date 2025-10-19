"""Gerador de código intermediário no formato MEPA."""

from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional
from semantic.errors import SemanticError
from syntax.ast_nodes import (
    ASTNode, Program, FunctionDeclaration, VarAssign, IfStatement, WhileStatement,
    ForStatement, ReturnStatement, BreakStatement, ContinueStatement,
    BinaryOperation, UnaryOp, Literal, Identifier, Call,
)


class CodeGenerationError(Exception):
    """Erro genérico de geração de código."""


# ================================================================
# Estruturas auxiliares
# ================================================================
@dataclass
class _Scope:
    """Escopo de variáveis com endereços relativos e suporte a deslocamento absoluto."""
    parent: Optional["_Scope"]
    symbols: Dict[str, int]
    next_addr: int = 0

    def declare(self, name: str) -> int:
        """Declara uma variável neste escopo."""
        if name in self.symbols:
            raise SemanticError(None, f"variável '{name}' já declarada neste escopo.")
        addr = self.next_addr
        self.symbols[name] = addr
        self.next_addr += 1
        return addr

    def abs_offset_from_root(self) -> int:
        """Soma quantos slots existem acima deste escopo."""
        offset = 0
        scope = self.parent
        while scope is not None:
            offset += scope.next_addr
            scope = scope.parent
        return offset

    def lookup_abs(self, name: str) -> Optional[int]:
        """Procura variável e retorna endereço absoluto (soma deslocamentos dos escopos pais)."""
        scope = self
        offset_below = 0
        while scope is not None:
            if name in scope.symbols:
                rel = scope.symbols[name]
                return scope.abs_offset_from_root() + rel + offset_below
            offset_below += scope.next_addr
            scope = scope.parent
        return None


@dataclass
class LoopContext:
    break_label: str
    continue_label: str


@dataclass
class FunctionInfo:
    name: str
    label: str
    end_label: str
    return_addr: int
    param_addresses: List[int] = field(default_factory=list)
    instructions: List[str] = field(default_factory=list)


@dataclass
class FunctionContext:
    info: FunctionInfo


# ================================================================
# Gerador de Código MEPA
# ================================================================
class MepaGenerator:
    """Converte a AST em uma sequência de instruções MEPA."""

    def __init__(self) -> None:
        self.instructions: List[str] = []
        self._current_output: List[str] = self.instructions
        self._label_counter: int = 0
        self._current_scope: _Scope = _Scope(parent=None, symbols={})
        self._loop_stack: List[LoopContext] = []
        self._function_stack: List[FunctionContext] = []
        self._function_infos: Dict[str, FunctionInfo] = {}
        self._function_segments: List[List[str]] = []
        self._address_names: Dict[int, str] = {}
        self._program_end_label: Optional[str] = None
        self._locals_count_stack: List[int] = []
        self._max_abs_addr: int = -1  # controla maior endereço usado

    # ----------------------------------------------------------
    def generate(self, program: Program) -> List[str]:
        """Gera as instruções MEPA para o programa completo."""
        self.instructions = ["INPP", "AMEM 0"]
        self._current_output = self.instructions
        self._label_counter = 0
        self._current_scope = _Scope(parent=None, symbols={})
        self._loop_stack = []
        self._function_stack = []
        self._function_infos = {}
        self._function_segments = []
        self._address_names = {}
        self._program_end_label = None
        self._locals_count_stack = []
        self._max_abs_addr = -1

        try:
            self._generate_program(program)
        except SemanticError as exc:
            raise CodeGenerationError(str(exc)) from exc
        except NotImplementedError as exc:
            raise CodeGenerationError(str(exc)) from exc

        if self._program_end_label is None:
            self._program_end_label = self._new_label("LEND_")

        self._emit(f"DSVS {self._program_end_label}")

        for segment in self._function_segments:
            self.instructions.extend(segment)

        self._emit(f"{self._program_end_label}: NADA")
        self._emit("PARA")

        # Corrige AMEM inicial
        total_mem = max(0, self._max_abs_addr + 1)
        self.instructions[1] = f"AMEM {total_mem}"

        return self.instructions

    # ----------------------------------------------------------
    def _generate_program(self, program: Program) -> None:
        """Processa funções e corpo principal."""
        for stmt in program.statements:
            if isinstance(stmt, FunctionDeclaration):
                self._generate_function(stmt)

        for stmt in program.statements:
            if not isinstance(stmt, FunctionDeclaration):
                self._generate_statement(stmt)

        if self._program_end_label is None:
            self._program_end_label = self._new_label("LEND_")

    # ----------------------------------------------------------
    def _generate_statement(self, stmt: ASTNode) -> None:
        """Gera código MEPA para uma instrução."""
        if isinstance(stmt, VarAssign):
            addr = self._lookup(stmt.name)
            if addr is None:
                addr = self._declare_variable(stmt.name)
            self._generate_expression(stmt.expr)
            self._store(addr)
            return

        if isinstance(stmt, IfStatement):
            self._generate_expression(stmt.cond)
            label_else = self._new_label()
            label_end = self._new_label()
            self._emit(f"DSVF {label_else}")
            self._generate_block(stmt.then_block.statements)
            self._emit(f"DSVS {label_end}")
            self._emit(f"{label_else}: NADA")
            if stmt.else_block:
                self._generate_block(stmt.else_block.statements)
            self._emit(f"{label_end}: NADA")
            return

        if isinstance(stmt, WhileStatement):
            label_start = self._new_label()
            label_end = self._new_label()
            self._emit(f"{label_start}: NADA")
            self._generate_expression(stmt.cond)
            self._emit(f"DSVF {label_end}")
            loop_ctx = LoopContext(break_label=label_end, continue_label=label_start)
            self._loop_stack.append(loop_ctx)
            self._generate_block(stmt.body.statements)
            self._loop_stack.pop()
            self._emit(f"DSVS {label_start}")
            self._emit(f"{label_end}: NADA")
            return

        if isinstance(stmt, BreakStatement):
            if not self._loop_stack:
                raise CodeGenerationError("Comando 'break' fora de laço.")
            self._emit(f"DSVS {self._loop_stack[-1].break_label}")
            return

        if isinstance(stmt, ContinueStatement):
            if not self._loop_stack:
                raise CodeGenerationError("Comando 'continue' fora de laço.")
            self._emit(f"DSVS {self._loop_stack[-1].continue_label}")
            return

        if isinstance(stmt, ReturnStatement):
            if not self._function_stack:
                raise CodeGenerationError("Comando 'return' fora de função.")
            ctx = self._function_stack[-1]
            if stmt.expr is not None:
                self._generate_expression(stmt.expr)
                self._store(ctx.info.return_addr)
            self._emit(f"DSVS {ctx.info.end_label}")
            return

        self._generate_expression_statement(stmt)

    # ----------------------------------------------------------
    def _generate_block(self, statements: Iterable[ASTNode]) -> None:
        """Cria um novo escopo para um bloco."""
        self._enter_scope()
        for stmt in statements:
            self._generate_statement(stmt)
        self._exit_scope()

    # ----------------------------------------------------------
    def _declare_variable(self, name: str) -> int:
        """Declara variável no escopo atual e retorna endereço absoluto."""
        _ = self._current_scope.declare(name)
        full_addr = self._lookup(name)
        self._address_names[full_addr] = name

        if self._locals_count_stack:
            self._locals_count_stack[-1] += 1
        return full_addr

    # ----------------------------------------------------------
    def _generate_expression(self, expr: ASTNode) -> None:
        if isinstance(expr, Literal):
            if isinstance(expr.value, bool):
                self._emit(f"CRCT {1 if expr.value else 0}")
            elif isinstance(expr.value, (int, float)):
                self._emit(f"CRCT {expr.value}")
            elif isinstance(expr.value, str):
                s = expr.value.replace('"', r'\"')
                self._emit(f'CRCS "{s}"')
            else:
                raise NotImplementedError(f"Literal {type(expr.value)} não suportado")
            return

        if isinstance(expr, Identifier):
            addr = self._lookup(expr.name)
            if addr is None:
                raise SemanticError(expr.line or 0, f"variável '{expr.name}' não declarada")
            self._load(addr)
            return

        if isinstance(expr, BinaryOperation):
            self._generate_expression(expr.left)
            self._generate_expression(expr.right)
            self._emit(self._binary_instruction(expr.op))
            return

        if isinstance(expr, UnaryOp):
            self._generate_expression(expr.operand)
            self._emit("NEGA")
            return

        if isinstance(expr, Call):
            if isinstance(expr.callee, Identifier) and expr.callee.name == "print":
                for arg in expr.args:
                    self._generate_expression(arg)
                    self._emit("IMPR")
                return
            raise NotImplementedError("Somente print() é suportado.")
        raise NotImplementedError(f"Nó de expressão {type(expr).__name__} não suportado.")

    # ----------------------------------------------------------
    def _generate_expression_statement(self, expr: ASTNode) -> None:
        if isinstance(expr, Call) and isinstance(expr.callee, Identifier) and expr.callee.name == "print":
            for arg in expr.args:
                self._generate_expression(arg)
                self._emit("IMPR")
            return
        raise NotImplementedError("Expressão usada como comando não suportada.")

    # ----------------------------------------------------------
    def _lookup(self, name: str) -> Optional[int]:
        return self._current_scope.lookup_abs(name)

    # ----------------------------------------------------------
    def _enter_scope(self) -> None:
        self._current_scope = _Scope(parent=self._current_scope, symbols={})
        self._locals_count_stack.append(0)
        self._emit("AMEM 0")

    def _exit_scope(self) -> None:
        if self._current_scope.parent is None:
            raise CodeGenerationError("Tentativa de sair do escopo global.")
        local_count = self._locals_count_stack.pop()
        if local_count > 0:
            self._emit(f"DMEM {local_count}")
        for i in range(len(self._current_output) - 1, -1, -1):
            if self._current_output[i].startswith("AMEM 0"):
                self._current_output[i] = f"AMEM {local_count}"
                break
        self._current_scope = self._current_scope.parent

    # ----------------------------------------------------------
    @staticmethod
    def _binary_instruction(op: str) -> str:
        mapping = {
            "+": "SOMA", "-": "SUBT", "*": "MULT", "/": "DIVI", "//": "DIVI",
            "==": "CMIG", "!=": "CMDG", ">": "CMMA", "<": "CMME",
            ">=": "CMAG", "<=": "CMEG",
        }
        if op not in mapping:
            raise NotImplementedError(f"Operador {op} não suportado.")
        return mapping[op]

    # ----------------------------------------------------------
    def _emit(self, instruction: str) -> None:
        self._current_output.append(instruction)

    def _new_label(self, prefix: str = "L") -> str:
        self._label_counter += 1
        return f"{prefix}{self._label_counter}"

    def _load(self, addr: int) -> None:
        self._max_abs_addr = max(self._max_abs_addr, addr)
        comment = self._address_names.get(addr)
        suffix = f" # {comment}" if comment else ""
        self._emit(f"CRVL {addr}{suffix}")

    def _store(self, addr: int) -> None:
        self._max_abs_addr = max(self._max_abs_addr, addr)
        comment = self._address_names.get(addr)
        suffix = f" # {comment}" if comment else ""
        self._emit(f"ARMZ {addr}{suffix}")

    @contextmanager
    def _using_output(self, output: List[str]):
        previous = self._current_output
        self._current_output = output
        try:
            yield
        finally:
            self._current_output = previous


__all__ = ["MepaGenerator", "CodeGenerationError"]
