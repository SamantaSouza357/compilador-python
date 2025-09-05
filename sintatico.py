import sys
import ast
import json
import argparse
from typing import List, Dict, Optional

def _extract_expected(msg: str) -> Optional[str]:
    """
    Heurística para extrair 'retorno esperado' (token/construct esperado) da mensagem.
    Funciona para mensagens comuns do parser do Python 3.10+.
    """
    if not msg:
        return None

    lower = msg.lower()

    if "expected" in lower:
        # pegue substring depois de "expected"
        try:
            after = msg[msg.lower().index("expected") + len("expected"):].strip()
            return after.strip(". ")
        except Exception:
            pass

    if "was never closed" in lower:
        # exemplo: "'(' was never closed"
        return "fechamento de delimitador (parêntese/colchete/chave ou string)"

    if "unexpected eof while parsing" in lower or "end-of-file" in lower:
        return "algum fechamento antes do fim do arquivo (ex.: ')', ']', '}', '\"', \"'\")"

    if "did you mean" in lower:
        # Retorne a sugestão inteira
        try:
            after = msg[msg.lower().index("did you mean") :].strip()
            return after
        except Exception:
            pass

    if "indentation" in lower or "indented block" in lower:
        return "bloco indentado (ex.: após ':')"

    if "cannot assign to" in lower and "maybe you meant" in lower:
        try:
            after = msg[msg.lower().index("maybe you meant") :].strip()
            return after
        except Exception:
            pass

    return None

def _format_line_pointer(line: str, col: int) -> str:
    if line is None:
        return ""
    caret = " " * max(col - 1, 0) + "^"
    return f"{line.rstrip()}\n{caret}"

def analyze_source(src: str, filename: str = "<stdin>") -> List[Dict]:
    """
    Tenta parsear `src` e retorna uma lista de diagnósticos de erro sintático.
    """
    diagnostics: List[Dict] = []
    try:
        ast.parse(src, filename=filename, mode="exec")
    except (SyntaxError, IndentationError) as e:
        # e.lineno, e.offset, e.text, e.msg, e.end_lineno (3.11+), e.end_offset
        line = e.text if isinstance(e.text, str) else None
        col = int(e.offset) if e.offset is not None else 1
        expected = _extract_expected(e.msg or "")
        diag = {
            "file": filename,
            "type": e.__class__.__name__,
            "message": e.msg or str(e),
            "expected": expected,
            "line": int(e.lineno) if e.lineno else None,
            "col": col,
            "end_line": int(getattr(e, "end_lineno", 0)) or None,
            "end_col": int(getattr(e, "end_offset", 0)) or None,
            "snippet": line.rstrip("\n") if isinstance(line, str) else None,
            "pointer": _format_line_pointer(line, col) if line else None,
        }
        diagnostics.append(diag)
    except Exception as e:
        diagnostics.append({
            "file": filename,
            "type": "InternalError",
            "message": f"{type(e).__name__}: {e}",
            "expected": None,
            "line": None,
            "col": None,
            "end_line": None,
            "end_col": None,
            "snippet": None,
            "pointer": None,
        })
    return diagnostics

def load_source_from_path(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="py_syntax_checker",
        description="Validador sintático de arquivos Python (usa o parser do CPython)",
    )
    parser.add_argument("paths", nargs="+", help="Arquivos .py a verificar (ou '-' para ler do STDIN)")
    parser.add_argument("--json", action="store_true", help="Saída em JSON (máquinas)")
    args = parser.parse_args(argv)

    all_diags: List[Dict] = []
    exit_code = 0

    for p in args.paths:
        try:
            src = load_source_from_path(p)
        except FileNotFoundError:
            print(f"[ERRO] Arquivo não encontrado: {p}", file=sys.stderr)
            exit_code = 2
            continue
        except Exception as e:
            print(f"[ERRO] Falha ao ler {p}: {e}", file=sys.stderr)
            exit_code = 2
            continue

        diags = analyze_source(src, filename=p if p != "-" else "<stdin>")
        all_diags.extend(diags)

    if args.json:
        print(json.dumps(all_diags, ensure_ascii=False, indent=2))
    else:
        if not all_diags:
            print("✔ Sem erros sintáticos")
        else:
            for d in all_diags:
                print(f"\nArquivo: {d['file']}")
                print(f"Tipo: {d['type']}")
                if d['line'] is not None and d['col'] is not None:
                    pos = f"L{d['line']}:C{d['col']}"
                    print(f"Posição: {pos}")
                print(f"Mensagem: {d['message']}")
                if d['expected']:
                    print(f"Esperado: {d['expected']}")
                if d['pointer']:
                    print(d['pointer'])
            exit_code = 1

    return exit_code

if __name__ == "__main__":
    raise SystemExit(main())
