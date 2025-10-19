# Compilador Python — Léxico e Sintaxe (pt-BR)

Projeto didático de um mini “compilador”/analisador para uma linguagem estilo Python:
- Léxico: transforma código-fonte em tokens (incluindo INDENT/DEDENT por indentação)
- Sintaxe: monta AST com cadeia de handlers (def, if/else, for/while, return, atribuição, break/continue, expressões)
- Testes: suíte cobrindo léxico, sintaxe, precedência, unário, contexto e arquivos de exemplo

Os comentários e docstrings estão em português; os identificadores do código permanecem em inglês para clareza técnica.

## Requisitos

- Python 3.9+ (testado com 3.9)

## Estrutura do projeto (resumo)

- `src/lexer/lexer_analyzer.py`: Léxico (gera tokens, INDENT/DEDENT)
- `src/lexer/tokens.py`: Tipos de token, palavras‑chave, símbolos
- `src/lexer/errors.py`: `LexicalError`
- `src/syntax/token_stream.py`: Cursor leve sobre tokens (peek/advance/consume)
- `src/syntax/syntax_analyzer.py`: Parser principal (cadeia de handlers → AST)
- `src/syntax/ast_nodes.py`: Nós da AST (Program, Block, IfStatement, etc.)
- `src/syntax/expression_parser.py`: Parser de expressões (estilo Pratt)
- `src/syntax/block_parser.py`: Parsing de blocos por indentação
- `src/syntax/errors.py`: `SyntaxErrorCompilador`
- `src/syntax/handlers/*.py`: Handlers para cada comando
- `tests/`: suíte de testes e arquivos de exemplo em `tests/files`

## Novas etapas: semântica e MEPA

Para além da análise léxica e sintática, o compilador agora valida regras semânticas e gera código intermediário na Máquina Didática MEPA.

### Análise Semântica

- Localização: `src/semantic/semantic_analyzer.py`
- Objetivo: garantir a consistência básica do programa antes da execução ou geração de código.
  - Cada variável deve ser declarada antes de ser usada.
  - Variáveis não podem ser redeclaradas no mesmo escopo.
  - Comandos `break`/`continue` só são válidos dentro de laços (while / for).
  - Expressões devem conter apenas identificadores válidos e tipos compatíveis (números, strings, booleanos, etc.).
- Fluxo:
  1. `SemanticAnalyzer` recebe a AST (`Program`) e percorre comandos.
  2. Usa a `SymbolTable` para registrar variáveis por escopo e verificar se já foram declaradas (com endereço incremental).
  3. Diferencia fase de **declaração** (atribuições iniciais) e **corpo** (demais comandos).
  4. Cria escopos filhos para blocos (`if`, `while`, `for`), herdando variáveis do escopo pai.
  5. Aceita funções definidas e built-ins (`print`, `input`, `range`). Em caso de erro, lança `SemanticError` com a linha.
  6. Em caso de uso indevido (break fora de laço, variável não declarada, operação inválida), lança SemanticError indicando a linha e a causa.
- Estruturas principais:
  - `SymbolTable`: lookup e controle de endereços por escopo (`src/semantic/symbol_table.py`).
  - Métodos `_analyze_statement` e `_analyze_expression`: aplicam as regras em cada nó da AST.

### Geração de Código MEPA

- Localização: `src/codegen/mepa_generator.py`
- Objetivo: converter a AST validada em instruções MEPA (máquina de pilha).
  - Sequência típica: `INPP`, `AMEM n`, `CRVL`, `SOMA`, `DSVF`, `CHPR`, `RTPR`, `PARA`.
- Estrutura:
  - Classe `MepaGenerator.generate(program)` cria rótulos, endereços e gerencia escopos.
  - Mantém mapas de variáveis para gerar comentários (`ARMZ 0 # x`) e pilhas para laços.
  - Antes do corpo principal, registra cada função (`FunctionDeclaration`), criando rótulos `F_nome_X` e `F_nome_END_Y`.
  - Atualiza `AMEM` ao final com o total de variáveis/temporários.
- Destaques:
  - `while`: rótulos de entrada/fim (`L1`, `L2`), suporte a `break`/`continue` via `LoopContext`.
  - `for` com `range(...)`: traduzido para laço com limite armazenado em temporário e label específico para o incremento.
  - `return`: avalia a expressão, guarda em endereço reservado e salta para o label de saída.
  - Chamadas: `input()` → `LEIT`; `print(...)` → avalia argumentos + `IMPR`; funções usuais usam `CHPR` / `RTPR`.
  - Em caso de construções ainda não suportadas (ex.: `range` com passo), lança `CodeGenerationError`.

### Fluxo completo
1. Lexer → tokens.
2. Parser → AST.
3. `SemanticAnalyzer` valida escopos e variáveis.
4. `MepaGenerator` produz lista de instruções MEPA, impressa pelo CLI (`src/main.py`), após as mensagens “Programa sintaticamente correto.” e “Programa semanticamente correto.”.

## Como rodar (exemplos com os arquivos em `tests/files`)

1) Análise léxica e sintática via CLI

```bash
python3 src/main.py -f tests/files/exemplo_valido.txt
```

Saída esperada (resumo):
- Impressão dos tokens, um por linha (com linha/átomo/lexema)
- Mensagem “Programa sintaticamente correto.” seguida de uma representação da AST

2) Arquivo com linhas em branco e comentários

```bash
python3 src/main.py -f tests/files/exemplo_linhas_em_branco.txt
```

O parser ignora NEWLINEs iniciais dentro de blocos; o programa ainda é válido.

3) Erro léxico (caractere inesperado)

```bash
python3 src/main.py -f tests/files/exemplo_erro_lexico.txt
```

Saída (exemplo):

```
Erro léxico na linha 2: caractere inesperado '$'
```

4) Erro sintático (faltando dois‑pontos)

```bash
python3 src/main.py -f tests/files/exemplo_erro_sintatico.txt
```

Saída (exemplo):

```
Erro de sintaxe na linha 1: Esperado ':' …
```

## Rodando a suíte de testes

- Todos os testes (rápido):

```bash
python3 -m unittest discover -s tests -q
```

- Teste único:

```bash
python3 -m unittest tests/test_lexer.py -q
```

## Como funciona (visão rápida)

1. O Léxico lê o texto e gera uma lista de tokens, com controle de indentação (INDENT/DEDENT) por nível de espaços/tabs no início de cada linha.
2. O `TokenStream` centraliza a navegação nos tokens (peek/advance/consume/skip_newlines).
3. O `SyntaxAnalyzer.parse()` percorre os tokens e, para cada comando, consulta a cadeia de handlers. O primeiro que “casa” consome os tokens daquele comando e devolve um nó de AST.
4. Expressões são analisadas por `ExpressionParser` (Pratt), respeitando precedência/associatividade e chamadas encadeadas.

## Estendendo

- Para suportar um novo comando, crie um handler em `src/syntax/handlers/novo_handler.py` e registre-o na lista em `src/syntax/syntax_analyzer.py` (ordem importa).
- Para novos operadores de expressão, ajuste a tabela `PRECEDENCE` em `src/syntax/expression_parser.py` e garanta que o léxico reconheça o token.

## Licença

Uso educacional. Adapte conforme necessário.
