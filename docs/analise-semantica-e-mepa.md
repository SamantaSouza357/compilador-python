# Análise Semântica e Geração MEPA

Este documento resume  como o compilador faz a verificação semântica e como gera o código intermediário  MEPA.

## 1. Análise Semântica (`src/semantic/semantic_analyzer.py`)

### Objetivo
Garantir que o programa siga regras de consistência antes da geração de código:
- Cada variável é declarada apenas uma vez na seção de declarações.
- Toda variável usada no corpo foi declarada.
- Parâmetros de função ficam disponíveis dentro da função.
- `break`/`continue` são permitidos apenas dentro de laços.

### Fluxo geral
1. A classe `SemanticAnalyzer` recebe o nó `Program` (AST) produzido pelo parser.
2. `analyze()` cria uma tabela de símbolos global (`SymbolTable`) e percorre os comandos.
3. O arquivo diferencia duas fases dentro de cada escopo:
   - **Declaração**: sequência inicial de atribuições, usadas para cadastrar variáveis (endereço crescente e tipo “inteiro”).
   - **Corpo**: a partir do primeiro comando que não é declaração, cada atribuição exige que a variável já exista.
4. Blocos (`if`, `while`, `for`, corpo de função) criam escopos filhos com `SymbolTable.child()`.
5. Ao encontrar um identificador, a análise verifica se ele está na tabela (levando em conta escopos pais). Funções definidas no arquivo e built-ins (`print`, `input`, `range`) são aceitas diretamente.
6. Se houver violação, é lançado `SemanticError` com a linha do problema.

### Estruturas principais
- `SymbolTable` (`src/semantic/symbol_table.py`): armazena nome → endereço/tipo e permite lookup em escopos pais.
- `SemanticAnalyzer._analyze_statement`: despacha cada nó da AST e aplica as regras. Para `ForStatement`, declara o iterador em um escopo próprio. Para `Return`, valida a expressão.
- `BUILTIN_FUNCTIONS`: lista simples das funções que não precisam de declaração (`print`, `input`, `range`).

## 2. Geração de Código MEPA (`src/codegen/mepa_generator.py`)

### Objetivo
Transformar a mesma AST, já validada, em uma sequência de instruções MEPA (máquina de pilha). O resultado é uma lista de strings com comandos como `INPP`, `CRVL`, `SOMA`, `DSVF`, etc.

### Estrutura do gerador
- Classe `MepaGenerator` com método `generate(program)`.
- Mantém estado para rótulos, endereços de variáveis, pilha de escopos e contexto de laços/funções.
- Inicia com `INPP` e `AMEM 0` (o número do `AMEM` é atualizado ao final com a quantidade total de variáveis alocadas).

### Gestão de escopos e endereços
- `_Scope`: armazena o mapa nome → endereço dentro do escopo atual.
- `_declare_variable` e `_lookup`: controlam endereços sequenciais (0, 1, 2, ...). Nomes são guardados em `_address_names` para comentários (`ARMZ 0 # x`).
- `_enter_scope` / `_exit_scope`: criam/removem escopos aninhados.

### Funções
- Antes de processar o corpo principal, `_generate_program` registra todas as `FunctionDeclaration`.
- Cada função recebe um rótulo `F_nome_X` e um rótulo de saída `F_nome_END_Y`.
- Parâmetros viram variáveis locais com endereços fixos; o retorno usa um endereço reservado (`return_addr`).
- Durante o corpo, `return expr` gera código para avaliar a expressão, armazená-la no endereço de retorno e saltar para o label final da função (`DSVS F_nome_END_Y`).
- No fim do arquivo, o gerador emite `DSVS LEND` para pular o código das funções, depois anexa os segmentos de cada função e, por fim, coloca `LEND: NADA` / `PARA`.

### Laços e controle
- `while`: cria rótulos de início/fim, empilha um `LoopContext` para suportar `break` (salta para o label de fim) e `continue` (salta para o label de início).
- `for`: atualmente traduz apenas `for <id> in range(...)`. Armazena o limite em uma variável temporária e gera um loop semelhante ao `while`, usando um label extra para o incremento. `continue` cai nesse label de incremento.

### Expressões e comandos
- Literais → `CRCT` (números/booleanos) ou `CRCS` (strings).
- Identificadores → `CRVL endereço` (carrega valor na pilha).
- Atribuições → avaliam a expressão e usam `ARMZ endereço`.
- Operadores binários → instruções MEPA (`SOMA`, `SUBT`, `MULT`, comparadores `CMIG`, `CMEG` etc.).
- Chamadas:
  - `input()` → `LEIT`.
  - `print(args…)` → avalia cada argumento e emite `IMPR` (como comando isolado).
  - Funções definidas pelo usuário → gera código para cada argumento (armazenando nos endereços dos parâmetros), chama `CHPR label` e carrega o valor de retorno com `_load(return_addr)`.

### Tratamento de erros
- Casos ainda não suportados (por exemplo, `for` com `range` e passo customizado) levantam `NotImplementedError` que vira `CodeGenerationError`.
- Se `break`/`continue` aparecerem fora de laço ou `return` fora de função, o gerador lança `CodeGenerationError` explicativo.

### Exemplo de fluxo
1. Lexer e parser produzem a AST.
2. `SemanticAnalyzer` valida declarações/uso de variáveis.
3. `MepaGenerator.generate(ast)` retorna algo como:
   ```
   INPP
   AMEM 2
   CRCT 1
   ARMZ 0 # x
   ...
   PARA
   ```
4. O CLI (`src/main.py`) imprime essas instruções após as mensagens de sucesso das fases anteriores.

## 3. Testes principais
- `tests/test_semantic_analyzer.py`: cobre erros de declaração duplicada, uso antes de declarar, escopos de função e casos válidos.
- `tests/test_codegen_mepa.py`: garante o formato das instruções para `while`, `for range`, funções com retorno e a interação de `break`/`continue`.