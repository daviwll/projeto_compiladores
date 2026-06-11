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
├── interface/               # Web Interface ⭐ NEW
│   ├── app.py                # Gradio frontend
│   ├── compiler_api.py       # Backend API
│   ├── start.bat             # Windows launcher
│   ├── start.sh              # Linux/Mac launcher
│   ├── test_setup.py         # Setup verification
│   ├── requirements.txt      # Dependencies
│   ├── README.md             # Interface guide
│   ├── INSTALLATION.md       # Setup guide
│   └── QUICKSTART.md         # Quick start
│
├── src/                      # Código fonte do compilador
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

### 🚀 Option 1: Web Interface (Easiest!) ⭐ NEW

```bash
# Start web interface
cd interface
python app.py

# Or use launcher
# Windows: start.bat
# Linux/Mac: ./start.sh
```

**Browser opens to:** http://localhost:7860

**Features:**
- ✅ Interactive code editor
- ✅ Multiple compilation views
- ✅ Direct program execution
- ✅ One-click .exe download
- ✅ Built-in examples and help

### 📝 Option 2: Command Line (Traditional)

### 1. Executar Programa Diretamente (Runtime)
```bash
# Teste básico
py src\runner.py test_runner_simple.minipar

# Servidor (Terminal 1)
py src\runner.py calc_server.minipar

# Cliente (Terminal 2)
py src\runner.py calc_client.minipar
```

### 2. Compilar para TAC
```bash
py compile.py examples\ex1.minipar
```

### 3. Compilar para Executável
```bash
py compile.py examples\ex1.minipar --exe
```

### 4. Executar Testes
```bash
py run_tests.py
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
