"""Gerador de código intermediário no formato MEPA."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from semantic.errors import SemanticError
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


class CodeGenerationError(Exception):
    """Erro genérico de geração de código."""


@dataclass
class _Scope:
    """Representa um escopo de variáveis com encadeamento."""

    parent: Optional["_Scope"]
    symbols: Dict[str, int]


@dataclass
class LoopContext:
    """Mantém os rótulos de controle para break/continue."""

    break_label: str
    continue_label: str


@dataclass
class FunctionInfo:
    """Metadados de função necessários para geração de chamadas."""

    name: str
    label: str
    end_label: str
    return_addr: int
    param_addresses: List[int] = field(default_factory=list)
    instructions: List[str] = field(default_factory=list)


@dataclass
class FunctionContext:
    """Contexto ativo durante a geração do corpo de uma função."""

    info: FunctionInfo


class MepaGenerator:
    """Converte a AST em uma sequência de instruções MEPA."""

    def __init__(self) -> None:
        self.instructions: List[str] = []
        self._current_output: List[str] = self.instructions
        self._label_counter: int = 0
        self._next_address: int = 0
        self._temp_counter: int = 0
        self._current_scope: _Scope = _Scope(parent=None, symbols={})
        self._loop_stack: List[LoopContext] = []
        self._function_stack: List[FunctionContext] = []
        self._function_infos: Dict[str, FunctionInfo] = {}
        self._function_segments: List[List[str]] = []
        self._address_names: Dict[int, str] = {}
        self._program_end_label: Optional[str] = None

    # API pública ---------------------------------------------------------
    def generate(self, program: Program) -> List[str]:
        """Gera instruções MEPA para um Program."""
        self.instructions = ["INPP", "AMEM 0"]
        self._current_output = self.instructions
        self._label_counter = 0
        self._next_address = 0
        self._temp_counter = 0
        self._current_scope = _Scope(parent=None, symbols={})
        self._loop_stack = []
        self._function_stack = []
        self._function_infos = {}
        self._function_segments = []
        self._address_names = {}
        self._program_end_label = None

        try:
            self._generate_program(program)
        except SemanticError as exc:
            raise CodeGenerationError(str(exc)) from exc
        except NotImplementedError as exc:
            raise CodeGenerationError(str(exc)) from exc

        if self._program_end_label is None:
            self._program_end_label = self._new_label()
        self._emit(f"DSVS {self._program_end_label}")

        for segment in self._function_segments:
            self.instructions.extend(segment)

        self.instructions.append(f"{self._program_end_label}: NADA")
        self.instructions.append("PARA")

        self.instructions[1] = f"AMEM {self._next_address}"
        return self.instructions

    # Geração por nó ------------------------------------------------------
    def _generate_program(self, program: Program) -> None:
        """Processa declarações globais e o corpo do programa."""
        for stmt in program.statements:
            if isinstance(stmt, FunctionDeclaration):
                self._generate_function(stmt)

        body_started = False
        for stmt in program.statements:
            if isinstance(stmt, FunctionDeclaration):
                continue
            if isinstance(stmt, VarAssign) and not body_started:
                addr = self._declare_variable(stmt.name)
                self._generate_expression(stmt.expr)
                self._store(addr)
            else:
                body_started = True
                self._generate_statement(stmt)

        if self._program_end_label is None:
            self._program_end_label = self._new_label(prefix="LEND_")

    def _generate_function(self, func: FunctionDeclaration) -> None:
        label = self._new_label(prefix=f"F_{func.name}_")
        end_label = self._new_label(prefix=f"F_{func.name}_END_")
        info = FunctionInfo(name=func.name, label=label, end_label=end_label, return_addr=-1)
        self._function_infos[func.name] = info
        instructions: List[str] = []
        info.instructions = instructions
        self._function_segments.append(instructions)

        with self._using_output(instructions):
            self._emit(f"{label}: NADA")
            self._enter_scope()
            for param in func.params:
                addr = self._declare_variable(param)
                info.param_addresses.append(addr)
            info.return_addr = self._allocate_temp(f"{func.name}_ret")
            self._emit("CRCT 0")
            self._store(info.return_addr)
            self._function_stack.append(FunctionContext(info=info))
            self._generate_statements_in_current_scope(func.body.statements, allow_declarations=True)
            self._function_stack.pop()
            self._emit(f"{end_label}: RTPR")
            self._exit_scope()

    def _generate_block(
        self,
        statements: Iterable[ASTNode],
        *,
        allow_declarations: bool,
    ) -> None:
        """Analisa um bloco delimitado por escopo próprio."""
        self._enter_scope()
        self._generate_statements_in_current_scope(statements, allow_declarations=allow_declarations)
        self._exit_scope()

    def _generate_statements_in_current_scope(
        self,
        statements: Iterable[ASTNode],
        *,
        allow_declarations: bool,
    ) -> None:
        body_started = not allow_declarations
        for stmt in statements:
            if isinstance(stmt, VarAssign) and not body_started:
                addr = self._declare_variable(stmt.name)
                self._generate_expression(stmt.expr)
                self._store(addr)
            else:
                body_started = True
                self._generate_statement(stmt)

    def _generate_statement(self, stmt: ASTNode) -> None:
        if isinstance(stmt, VarAssign):
            addr = self._lookup(stmt.name)
            if addr is None:
                raise SemanticError(stmt.line or 0, f"variável '{stmt.name}' não declarada")
            self._generate_expression(stmt.expr)
            self._store(addr)
            return

        if isinstance(stmt, IfStatement):
            self._generate_expression(stmt.cond)
            label_else = self._new_label()
            label_end = self._new_label()
            self._emit(f"DSVF {label_else}")
            self._generate_block(stmt.then_block.statements, allow_declarations=False)
            self._emit(f"DSVS {label_end}")
            self._emit(f"{label_else}: NADA")
            if stmt.else_block is not None:
                self._generate_block(stmt.else_block.statements, allow_declarations=False)
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
            self._generate_block(stmt.body.statements, allow_declarations=False)
            self._loop_stack.pop()
            self._emit(f"DSVS {label_start}")
            self._emit(f"{label_end}: NADA")
            return

        if isinstance(stmt, ForStatement):
            self._generate_for(stmt)
            return

        if isinstance(stmt, BreakStatement):
            if not self._loop_stack:
                raise CodeGenerationError("break fora de laço não é suportado")
            self._emit(f"DSVS {self._loop_stack[-1].break_label}")
            return

        if isinstance(stmt, ContinueStatement):
            if not self._loop_stack:
                raise CodeGenerationError("continue fora de laço não é suportado")
            self._emit(f"DSVS {self._loop_stack[-1].continue_label}")
            return

        if isinstance(stmt, ReturnStatement):
            if not self._function_stack:
                raise CodeGenerationError("return fora de função não é permitido")
            ctx = self._function_stack[-1]
            if stmt.expr is not None:
                self._generate_expression(stmt.expr)
                self._store(ctx.info.return_addr)
            self._emit(f"DSVS {ctx.info.end_label}")
            return

        self._generate_expression_statement(stmt)

    def _generate_for(self, stmt: ForStatement) -> None:
        iterable = stmt.iterable
        if not (
            isinstance(iterable, Call)
            and isinstance(iterable.callee, Identifier)
            and iterable.callee.name == "range"
        ):
            raise NotImplementedError("Somente for com range(...) é suportado na geração de código")

        args = iterable.args
        if len(args) == 1:
            start_expr = Literal(0)
            end_expr = args[0]
        elif len(args) == 2:
            start_expr, end_expr = args
        else:
            raise NotImplementedError("range() com step ainda não é suportado na geração de código")

        self._enter_scope()
        loop_var_addr = self._declare_variable(stmt.var_name)
        limit_addr = self._allocate_temp(f"{stmt.var_name}_limite")

        self._generate_expression(start_expr)
        self._store(loop_var_addr)
        self._generate_expression(end_expr)
        self._store(limit_addr)

        label_start = self._new_label()
        label_end = self._new_label()
        label_increment = self._new_label()

        self._emit(f"{label_start}: NADA")
        self._load(loop_var_addr)
        self._load(limit_addr)
        self._emit("CMME")
        self._emit(f"DSVF {label_end}")

        loop_ctx = LoopContext(break_label=label_end, continue_label=label_increment)
        self._loop_stack.append(loop_ctx)
        self._generate_statements_in_current_scope(stmt.body.statements, allow_declarations=False)
        self._loop_stack.pop()

        self._emit(f"{label_increment}: NADA")
        self._load(loop_var_addr)
        self._emit("CRCT 1")
        self._emit("SOMA")
        self._store(loop_var_addr)
        self._emit(f"DSVS {label_start}")
        self._emit(f"{label_end}: NADA")

        self._exit_scope()

    def _generate_expression_statement(self, expr: ASTNode) -> None:
        if isinstance(expr, Call):
            if isinstance(expr.callee, Identifier) and expr.callee.name == "print":
                for arg in expr.args:
                    self._generate_expression(arg)
                    self._emit("IMPR")
                return
        raise NotImplementedError("Expressão usada como comando não suportada (exceto print())")

    # Expressões ----------------------------------------------------------
    def _generate_expression(self, expr: ASTNode) -> None:
        if isinstance(expr, Literal):
            self._emit(self._literal_instruction(expr.value))
            return

        if isinstance(expr, Identifier):
            addr = self._lookup(expr.name)
            if addr is None:
                raise SemanticError(expr.line or 0, f"variável '{expr.name}' não declarada")
            self._load(addr)
            return

        if isinstance(expr, UnaryOp):
            if expr.op != "-":
                raise NotImplementedError(f"Operador unário '{expr.op}' não suportado")
            self._generate_expression(expr.operand)
            self._emit("NEGA")
            return

        if isinstance(expr, BinaryOperation):
            self._generate_expression(expr.left)
            self._generate_expression(expr.right)
            op = self._binary_instruction(expr.op)
            self._emit(op)
            return

        if isinstance(expr, Call):
            if isinstance(expr.callee, Identifier):
                name = expr.callee.name
                if name == "input":
                    if expr.args:
                        raise NotImplementedError("input() não aceita argumentos")
                    self._emit("LEIT")
                    return
                if name in self._function_infos:
                    info = self._function_infos[name]
                    if len(expr.args) != len(info.param_addresses):
                        raise CodeGenerationError(
                            f"Quantidade de argumentos inválida ao chamar '{name}'"
                        )
                    for arg, addr in zip(expr.args, info.param_addresses):
                        self._generate_expression(arg)
                        self._store(addr)
                    self._emit(f"CHPR {info.label}")
                    self._load(info.return_addr)
                    return
            raise NotImplementedError("Chamadas de função não suportadas para este callee")

        if isinstance(expr, VarAssign):
            self._generate_statement(expr)
            return

        raise NotImplementedError(f"Nó de expressão '{expr.__class__.__name__}' não suportado")

    # Auxiliares -----------------------------------------------------------
    def _declare_variable(self, name: str) -> int:
        if name in self._current_scope.symbols:
            raise SemanticError(None, f"variável '{name}' já declarada neste escopo")
        addr = self._next_address
        self._current_scope.symbols[name] = addr
        self._address_names[addr] = name
        self._next_address += 1
        return addr

    def _allocate_temp(self, hint: str) -> int:
        addr = self._next_address
        self._next_address += 1
        label = hint or f"temp_{self._temp_counter}"
        self._temp_counter += 1
        self._address_names[addr] = label
        return addr

    def _lookup(self, name: str) -> Optional[int]:
        scope = self._current_scope
        while scope is not None:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent
        return None

    def _enter_scope(self) -> None:
        self._current_scope = _Scope(parent=self._current_scope, symbols={})

    def _exit_scope(self) -> None:
        if self._current_scope.parent is None:
            raise CodeGenerationError("Tentativa de sair do escopo global")
        self._current_scope = self._current_scope.parent

    def _new_label(self, prefix: str = "L") -> str:
        self._label_counter += 1
        return f"{prefix}{self._label_counter}"

    def _emit(self, instruction: str) -> None:
        self._current_output.append(instruction)

    def _load(self, addr: int) -> None:
        comment = self._address_names.get(addr)
        suffix = f" # {comment}" if comment else ""
        self._emit(f"CRVL {addr}{suffix}")

    def _store(self, addr: int) -> None:
        comment = self._address_names.get(addr)
        suffix = f" # {comment}" if comment else ""
        self._emit(f"ARMZ {addr}{suffix}")

    def _literal_instruction(self, value: object) -> str:
        if isinstance(value, bool):
            return f"CRCT {1 if value else 0}"
        if isinstance(value, (int, float)):
            return f"CRCT {value}"
        if isinstance(value, str):
            escaped = value.replace('"', '\\"')
            return f'CRCS "{escaped}"'
        raise NotImplementedError(f"Literal do tipo '{type(value).__name__}' não suportado")

    @staticmethod
    def _binary_instruction(op: str) -> str:
        mapping = {
            "+": "SOMA",
            "-": "SUBT",
            "*": "MULT",
            "/": "DIVI",
            "//": "DIVI",
            "%": "MOD",
            "==": "CMIG",
            "!=": "CMDG",
            ">": "CMMA",
            "<": "CMME",
            ">=": "CMAG",
            "<=": "CMEG",
        }
        if op not in mapping:
            raise NotImplementedError(f"Operador binário '{op}' não suportado")
        return mapping[op]

    @contextmanager
    def _using_output(self, output: List[str]):
        previous = self._current_output
        self._current_output = output
        try:
            yield
        finally:
            self._current_output = previous


__all__ = ["MepaGenerator", "CodeGenerationError"]
