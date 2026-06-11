# Compilador Minipar

Um compilador completo para a linguagem **Minipar 2026.1** com suporte a **orientação a objetos**, **execução paralela**, **canais de comunicação**, geração de **código intermediário TAC**, código **C**, assembly **ARMv7** (CPUlator Web) e executáveis nativos.

## 🎯 Principais Recursos

✅ **Orientação a Objetos** - Classes, campos, métodos, construtores, herança (`extends`), `this`, `super`  
✅ **Web Interface** - Interface gráfica com Gradio  
✅ **Compilador Frontend** - Lexer, Parser, Análise Semântica, Geração de Código  
✅ **Runtime Executor** - Execute programas Minipar diretamente  
✅ **Canais de Comunicação** - Cliente-servidor com sockets  
✅ **Backend ARMv7** - Assembly para CPUlator Web com alocador de heap estático  
✅ **Backend C** - Código C com structs, `malloc`, e acesso via `->` para validação semântica  
✅ **Backend Executável** - Compile para binário nativo via GCC  
✅ **Documentação Completa** - Tutoriais e guias técnicos  

## 📋 Estrutura do Projeto

```
projeto_compiladores/
├── interface/               # Web Interface
│   ├── app.py                # Gradio frontend (full-featured)
│   ├── compiler_api.py       # Flask HTTP API + Gradio backend
│   ├── static/index.html     # Minimal plain-HTML web UI
│   ├── start.bat             # Windows launcher
│   ├── start.sh              # Linux/Mac launcher
│   ├── test_setup.py         # Setup verification
│   ├── requirements.txt      # Dependencies
│   ├── README.md             # Interface guide
│   ├── INSTALLATION.md       # Setup guide
│   └── QUICKSTART.md         # Quick start
│
├── src/                      # Código fonte do compilador
│   ├── minipar_cli.py       # CLI com subcomandos (compile, ast, tac, …)
│   ├── __init__.py          # Inicialização do pacote
│   ├── lexer.py             # Análise Léxica
│   ├── parser.py            # Análise Sintática
│   ├── ast_nodes.py         # Definições da AST
│   ├── semantic.py          # Análise Semântica
│   ├── symbol_table.py      # Tabela de Símbolos
│   ├── codegen.py           # Geração TAC
│   ├── c_codegen.py         # Geração C
│   ├── backend.py           # Backend GCC
│   ├── compiler.py          # Driver principal
│   ├── runner.py            # Runtime Executor
│   └── RUNNER_README.md     # Documentação do runner
│
├── examples/                 # Programas exemplo
│   ├── ex1.minipar          # Básico: variáveis e funções
│   ├── ex2.minipar          # Canais de servidor
│   ├── ex3.minipar          # Loops e entrada
│   ├── ex4.minipar          # Funções aninhadas
│   ├── ex5.minipar          # Funções simples
│   ├── fatorial_rec.minipar # Recursão
│   ├── quicksort.minipar    # Ordenação
│   ├── recomendacao.minipar # Sistema recomendação
│   └── README.md            # Documentação exemplos
│
├── tests/                    # Testes
│   ├── test_compilerok.py   # Suite testes compilador
│   ├── run_program_tests.py # Testes programa 1-4
│   ├── program_test_*.minipar  # Programas teste
│   └── program_test_*.txt   # Especificações
│
├── docs/                     # Documentação ⭐ ORGANIZADA
│   ├── tutorials/           # Tutoriais passo-a-passo
│   │   ├── QUICK_START_CHANNELS.md    # Início rápido
│   │   ├── CHANNEL_TUTORIAL.md        # Tutorial completo
│   │   ├── TUTORIAL.md                # Tutorial geral
│   │   ├── ARM_COMPILATION_GUIDE.md   # Guia ARM
│   │   └── RUNNING_ASSEMBLY_GUIDE.md  # Guia Assembly
│   ├── technical/           # Documentação técnica
│   │   ├── CHANNELS_INDEX.md          # Índice canais
│   │   ├── RUNTIME_IMPLEMENTATION_SUMMARY.md
│   │   ├── COMPLETE_PROJECT_ANALYSIS.md
│   │   ├── COMPREHENSIVE_ANALYSIS.md
│   │   ├── REQUIREMENTS_ANALYSIS.md
│   │   └── IMPLEMENTATION_PLAN.md
│   └── archive/             # Histórico desenvolvimento
│       ├── CHANGELOG.md
│       ├── BUGS_FOUND.md
│       ├── PHASE*.md
│       └── ...
│
├── bin/                      # Scripts utilitários ⭐ NEW
│   ├── minipar.bat          # Wrapper compilador
│   ├── run.bat              # Wrapper runner
│   └── test.bat             # Wrapper testes
│
├── generated/                # Arquivos gerados
│   ├── *.c                  # Código C gerado
│   ├── *.exe                # Executáveis
│   └── *.s                  # Assembly
│
├── calc_server.minipar       # Exemplo servidor ⭐
├── calc_client.minipar       # Exemplo cliente ⭐
├── test_runner_simple.minipar # Teste básico runner
│
├── compile.py                # Script compilação
├── run_tests.py              # Script testes
├── minipar.py                # Ponto entrada
├── pyproject.toml            # Configuração projeto
└── README.md                 # Este arquivo
```

## 🌐 Quick Start

### Setup (one-time)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install flask pytest
```

---

### Option 1: CLI (recommended)

```bash
# Compile a file (prints TAC)
python src/minipar_cli.py compile examples/ex1.minipar

# Show AST
python src/minipar_cli.py ast examples/fatorial_rec.minipar

# Generate C code
python src/minipar_cli.py generate-c examples/ex5.minipar --out /tmp/ex5.c

# Generate ARM assembly
python src/minipar_cli.py generate-arm examples/ex5.minipar

# Run all tests
python src/minipar_cli.py test
```

See `docs/INTEGRATION.md` for the full command reference.

---

### Option 2: HTTP API + minimal Web UI

```bash
python interface/compiler_api.py
# → http://127.0.0.1:8000   (web UI)
# → http://127.0.0.1:8000/health
# → POST http://127.0.0.1:8000/compile
# → POST http://127.0.0.1:8000/generate
```

Example with curl:

```bash
curl -s http://127.0.0.1:8000/compile \
  -H 'Content-Type: application/json' \
  -d '{"source": "print(\"Hello!\")", "show_tac": true}' | python -m json.tool
```

---

### Option 3: Gradio Web Interface (full-featured)

```bash
cd interface
python app.py
# → http://localhost:7860
```

Includes interactive code editor, execution tab, and example programs.

---

### Run tests

```bash
# All tests
.venv/bin/python -m pytest -q

# Unit tests only
.venv/bin/python -m pytest tests/test_compilerok.py -q

# API integration tests
.venv/bin/python -m pytest tests/test_integration_api.py -q
```

## 🔧 Componentes Principais

### 1. Compilador (src/)
- **lexer.py** - Análise léxica (tokenização)
- **parser.py** - Análise sintática (AST)
- **semantic.py** - Análise semântica
- **codegen.py** - Geração TAC
- **c_codegen.py** - Geração código C
- **backend.py** - Compilação GCC

### 2. Runtime Executor (src/runner.py) ⭐ NEW
- **Execução direta** de programas Minipar
- **Canais de comunicação** (s_channel, c_channel)
- **Socket networking** real
- **Multi-threading** para clientes concorrentes

## 📦 Instalação

### Pré-requisitos
- Python 3.7+
- GCC (opcional, para compilação nativa)

### Instalação Rápida

```bash
# Clonar ou baixar o projeto
cd projeto_compiladores

# Não há dependências externas! 
# Usa apenas biblioteca padrão Python
```

## 🎮 Uso

### Modo 1: Runtime Executor (Novo! ⭐)

Execute programas Minipar diretamente:

```bash
# Programa básico
py src\runner.py test_runner_simple.minipar

# Servidor de calculadora (Terminal 1)
py src\runner.py calc_server.minipar

# Cliente calculadora (Terminal 2)
py src\runner.py calc_client.minipar
```

**Tutorial completo**: [docs/tutorials/QUICK_START_CHANNELS.md](docs/tutorials/QUICK_START_CHANNELS.md)

### Modo 2: Compilador Tradicional

```bash
# Compilar para TAC (Three-Address Code)
py compile.py examples\ex1.minipar

# Ver tokens
py compile.py examples\ex1.minipar --tokens

# Ver AST
py compile.py examples\ex1.minipar --ast

# Gerar código C
py compile.py examples\ex1.minipar --generate-c

# Compilar para executável
py compile.py examples\ex1.minipar --exe
```

### Modo 3: Testes

```bash
# Todos os testes
py run_tests.py

# Testes específicos dos programas 1-4
py tests\run_program_tests.py
```

### Scripts Convenientes (bin/)

```bash
# Usar wrappers (Windows)
bin\minipar examples\ex1.minipar
bin\run calc_server.minipar
bin\test
```

## 📝 Exemplos

### Exemplo 1: Hello World
```minipar
print("Hello, Minipar!")

var nome: string = "Alice"
print("Olá,", nome)
```

### Exemplo 2: Função com Loop
```minipar
func fatorial(n: number) -> number {
    var result: number = 1
    var i: number = 1
    
    while(i <= n) {
        result = result * i
        i = i + 1
    }
    
    return result
}

print("5! =", fatorial(5))
```

### Exemplo 3: Canais Cliente-Servidor ⭐ NEW

**Servidor** (Terminal 1):
```minipar
func calcular(op: string, a: number, b: number) -> number {
    if (op == "+") { return a + b }
    if (op == "-") { return a - b }
    if (op == "*") { return a * b }
    return a / b
}

s_channel server {calcular, "Calculator", "localhost", 5000}
```

**Cliente** (Terminal 2):
```minipar
c_channel client {"localhost", 5000}
client.send("+", 10, 5)  # Resultado: 15
client.close()
```

**Mais exemplos**: Veja pasta `examples/` e `docs/tutorials/`

## 📚 Documentação

### 🚀 Tutoriais (Comece Aqui!)
- **[Quick Start Channels](docs/tutorials/QUICK_START_CHANNELS.md)** - 5 minutos para rodar servidor/cliente
- **[Channel Tutorial](docs/tutorials/CHANNEL_TUTORIAL.md)** - Guia completo de canais
- **[Tutorial Geral](docs/tutorials/TUTORIAL.md)** - Introdução ao Minipar
- **[ARM Compilation](docs/tutorials/ARM_COMPILATION_GUIDE.md)** - Compilar para ARM
- **[Running Assembly](docs/tutorials/RUNNING_ASSEMBLY_GUIDE.md)** - Executar assembly

### 🔧 Documentação Técnica
- **[Channels Index](docs/technical/CHANNELS_INDEX.md)** - Índice completo de canais
- **[Runtime Implementation](docs/technical/RUNTIME_IMPLEMENTATION_SUMMARY.md)** - Detalhes do runtime
- **[Project Analysis](docs/technical/COMPLETE_PROJECT_ANALYSIS.md)** - Análise completa
- **[Requirements](docs/technical/REQUIREMENTS_ANALYSIS.md)** - Análise de requisitos

### 📦 Código e Exemplos
- **[Runner README](src/RUNNER_README.md)** - Documentação do executor
- **[Examples README](examples/README.md)** - Exemplos comentados
- **[Test Programs](tests/)** - Programas de teste

### 📖 Arquivo
- **[Changelog](docs/archive/CHANGELOG.md)** - Histórico de mudanças
- **[Development Phases](docs/archive/)** - Fases de desenvolvimento

## 🎯 Características da Linguagem

### Tipos de Dados
- `number` - Números inteiros e reais
- `string` - Strings
- `bool` - Booleanos (true/false)
- `void` - Sem retorno
- `s_channel` - Canal servidor (socket)
- `c_channel` - Canal cliente (socket)

### Palavras-chave
```
var  func  if  else  while  break  continue  return  
par  true  false  print  input
```

### Sintaxe Básica

```minipar
# Variáveis
var x: number = 10
var nome: string = "Alice"
var flag: bool = true

# Funções
func add(a: number, b: number) -> number {
    return a + b
}

# Controle de fluxo
if (x > 0) {
    print("positivo")
}

while (i < 10) {
    i = i + 1
}

# Canais
s_channel server {handler, "desc", "localhost", 5000}
c_channel client {"localhost", 5000}
client.send(data)
client.close()

# Comentários
# Linha única
/* Multi-linha */
```

### Classes e Objetos (OO)

```minipar
# Declaração de classe
class Counter {
    var value: number = 0

    constructor(start: number) {
        value = start
    }

    func inc() -> number {
        value = value + 1
        return value
    }

    func get() -> number {
        return value
    }
}

# Criação de objeto
var c: Counter = new Counter(0)

# Chamada de método
c.inc()
c.get()

# Acesso e escrita de campo
c.value = 10

# Herança
class Animal {
    func speak() -> string { return "..." }
}

class Dog extends Animal {
    func fetch() -> string { return "fetching!" }
}

var d: Dog = new Dog()
d.speak()    # método herdado de Animal
d.fetch()    # método próprio de Dog
```

### Operadores
- **Aritméticos**: `+` `-` `*` `/` `%`
- **Comparação**: `==` `!=` `<` `>` `<=` `>=`
- **Lógicos**: `&&` `||` `!`

## 🏗️ Arquitetura

```
Código Minipar (.minipar)
         ↓
    Lexer → Tokens
         ↓
    Parser → AST  (classes, campos, métodos, herança)
         ↓
  Semantic → AST validado (tipos OO, herança, arity)
         ↓
   Codegen → TAC  (CLASS_BEGIN, FIELD, NEW_OBJECT,
         ↓         MEMBER_ACCESS, MEMBER_STORE, METHOD_CALL)
   ┌──────┼──────┐
   ↓      ↓     ↓
ARM     C Gen  Runner
(CPUlator)  (structs) (Execute)
output.s  output.c  Results
   ↓
Backend/GCC → Executável
```

### Componentes

| Módulo | Responsabilidade |
|--------|-----------------|
| **lexer.py** | Tokenização (inclui `class`, `new`, `this`, `super`, `extends`, `constructor`) |
| **parser.py** | Análise sintática (declarações OO, `new`, acesso de membro) |
| **ast_nodes.py** | Nós AST OO: `ClassDecl`, `FieldDecl`, `MethodDecl`, `ObjectCreation`, `MemberAccess` |
| **semantic.py** | Análise semântica com escopo de classe, herança, checagem de arity |
| **symbol_table.py** | Símbolos OO: class, field, method, constructor, object instance |
| **codegen.py** | Geração TAC com opcodes OO |
| **c_codegen.py** | Geração C: structs, `malloc`, `this->field`, funções com receptor |
| **arm_codegen.py** | Geração ARMv7 para CPUlator: alocador bump, offsets de campo, `ldr`/`str` |
| **backend.py** | Compilação GCC |
| **runner.py** | Execução runtime |

## 🧪 Testes

```bash
# Todos os testes
py run_tests.py

# Testes específicos
py tests\run_program_tests.py

# Teste individual
py src\runner.py test_runner_simple.minipar
```

**Cobertura**:
- ✅ Lexer (tokenização + keywords OO)
- ✅ Parser (AST + declarações OO)
- ✅ Semantic (tipos, escopo, validação OO)
- ✅ Codegen (TAC + opcodes OO)
- ✅ C Codegen (structs, malloc, acesso de campo)
- ✅ ARM Codegen (CPUlator: alocador, offsets, dispatch)
- ✅ Runner (execução)
- ✅ Canais (networking)
- ✅ Testes de aceitação OO (fixture + erros semânticos)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Add feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## 📄 Licença

Projeto educacional - Curso de Compiladores

## 🙏 Créditos

- **Runtime Executor**: Implementado com suporte a canais e sockets
- **Documentação**: Tutoriais completos e guias técnicos
- **Exemplos**: Programas demonstrativos incluídos

---

**Status**: ✅ Produção  
**Versão**: 2.0  
**Última Atualização**: 2025-10-23
