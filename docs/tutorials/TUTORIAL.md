# 🚀 Minipar Compiler - Complete Tutorial

**A Step-by-Step Guide to Building and Running Your First Minipar Programs — on Windows and Linux**

---

## 📋 Table of Contents

1. [Cross-Platform Conventions](#cross-platform-conventions)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Tutorial 1: Hello World](#tutorial-1-hello-world)
6. [Tutorial 2: Variables and Functions](#tutorial-2-variables-and-functions)
7. [Tutorial 3: Control Flow](#tutorial-3-control-flow)
8. [Tutorial 4: Recursive Functions](#tutorial-4-recursive-functions)
9. [Tutorial 5: Complete Compilation Pipeline](#tutorial-5-complete-compilation-pipeline)
10. [Advanced Features](#advanced-features)
11. [Troubleshooting](#troubleshooting)

---

## Cross-Platform Conventions

Every command in this tutorial works on **both Windows and Linux/macOS**. The only
differences are the interpreter name, how you run the produced program, and a couple
of shell built-ins. Use the column that matches your system:

| Action | Linux / macOS | Windows |
|--------|---------------|---------|
| Run Python | `python3` (or `python`) | `py` (or `python`) |
| Path separator | `/` (e.g. `src/compiler.py`) | `\` or `/` — Python accepts both |
| Run the built program | `./output` | `.\output.exe` |
| View a text file | `cat output.c` | `type output.c` |
| List files | `ls` | `dir` |
| Activate virtualenv | `source .venv/bin/activate` | `.venv\Scripts\activate` |

> 💡 **Tip:** Forward slashes (`/`) work in paths on Windows too, so most commands are
> identical across platforms — only the interpreter name and the *run* step really differ.
> Where a command differs, this tutorial shows a **Linux/macOS** block and a **Windows** block.

---

## Prerequisites

### Required Software
1. **Python 3.7+** - [Download](https://www.python.org/downloads/)
2. **GCC Compiler** - For generating native executables (the `--exe` step)
   - **Linux (Debian/Ubuntu)**: `sudo apt-get install gcc`
   - **Linux (Fedora/RHEL)**: `sudo dnf install gcc`
   - **Linux (Arch)**: `sudo pacman -S gcc`
   - **macOS**: `xcode-select --install`
   - **Windows**: [MSYS2](https://www.msys2.org/) (recommended) or [MinGW](http://www.mingw.org/)

> GCC is only required for the `--exe` (native executable) step. Tokenizing, parsing,
> semantic analysis, TAC, C generation and ARM generation all work without GCC.

### Verify Installation

**Linux/macOS:**
```bash
python3 --version
gcc --version
```

**Windows:**
```bat
py --version
gcc --version
```

Expected output (versions may differ):
```
Python 3.10.0 (or higher)
gcc (GCC) 12.2.0 (or similar)
```

---

## Installation

### Step 1: Navigate to the Project Directory

**Linux/macOS:**
```bash
cd ~/path/to/projeto_compiladores
```

**Windows:**
```bat
cd C:\path\to\projeto_compiladores
```

### Step 2: (Optional) Create a Virtual Environment

The compiler itself uses only the Python standard library, but the web interface and
the test suite need a few packages. A virtualenv keeps them isolated.

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install flask pytest
```

**Windows:**
```bat
py -m venv .venv
.venv\Scripts\activate
pip install flask pytest
```

### Step 3: Verify the Project Structure

**Linux/macOS:**
```bash
ls -la
```

**Windows:**
```bat
dir
```

You should see:
- `src/` folder (compiler source code)
- `examples/` folder (example programs)
- `compile.py`, `run_tests.py`, `README.md`
- Other documentation files

### Step 4: Test the Compiler

**Linux/macOS:**
```bash
python3 compile.py
```

**Windows:**
```bat
py compile.py
```

Expected output: usage information and the list of available flags.

---

## Quick Start

### Compile Your First Program (One Command)

**Linux/macOS:**
```bash
python3 compile.py examples/ex5.minipar --exe
```

**Windows:**
```bat
py compile.py examples\ex5.minipar --exe
```

This will:
1. ✅ Tokenize the source code
2. ✅ Parse and build the AST
3. ✅ Perform semantic analysis
4. ✅ Generate TAC (Three-Address Code)
5. ✅ Generate ARM assembly (`output.s`) — skip with `--no-asm`
6. ✅ Generate C code (`output.c`)
7. ✅ Compile with GCC into a native executable

### Run the Program

**Linux/macOS:**
```bash
./output
```

**Windows:**
```bat
.\output.exe
```

Expected output:
```
10
9
8
7
6
5
4
3
2
1
0
```

**Congratulations! You've just compiled and run your first Minipar program!** 🎉

---

## Tutorial 1: Hello World

### Step 1: Create Your First Program

Create a new file called `hello.minipar`:

```minipar
# hello.minipar - My first Minipar program

func greet() -> void {
    print("Hello, Minipar!")
    print("Welcome to compiler design!")
}

greet()
```

> ⚠️ **Note:** Avoid naming a function `main` — it collides with C's `main()` in the
> generated code. Use any other name (like `greet`) and call it at the top level.

### Step 2: Compile It

**Linux/macOS:**
```bash
python3 compile.py hello.minipar --exe --output hello
```

**Windows:**
```bat
py compile.py hello.minipar --exe --output hello
```

### Step 3: Run It

**Linux/macOS:**
```bash
./hello
```

**Windows:**
```bat
.\hello.exe
```

Expected output:
```
Hello, Minipar!
Welcome to compiler design!
```

### Step 4: See the Intermediate Steps

**Linux/macOS:**
```bash
python3 compile.py hello.minipar --tokens --ast --generate-c
```

**Windows:**
```bat
py compile.py hello.minipar --tokens --ast --generate-c
```

This shows you:
- **Tokens**: How the lexer breaks down your code
- **AST**: The parse tree structure
- **C Code**: The generated C source (saved to `output.c`)

---

## Tutorial 2: Variables and Functions

### Step 1: Write a Calculator Program

Create `calculator.minipar`:

```minipar
# calculator.minipar - Simple calculator

func add(a: number, b: number) -> number {
    return a + b
}

func multiply(a: number, b: number) -> number {
    return a * b
}

func calculate() -> void {
    var x: number = 10
    var y: number = 5

    var sum: number = add(x, y)
    var product: number = multiply(x, y)

    print("Sum:", sum)
    print("Product:", product)
}

calculate()
```

### Step 2: Compile and Run

**Linux/macOS:**
```bash
python3 compile.py calculator.minipar --exe --output calculator
./calculator
```

**Windows:**
```bat
py compile.py calculator.minipar --exe --output calculator
.\calculator.exe
```

Expected output:
```
Sum: 15
Product: 50
```

### Step 3: Inspect the Semantic Phase

**Linux/macOS:**
```bash
python3 compile.py calculator.minipar --semantic
```

**Windows:**
```bat
py compile.py calculator.minipar --semantic
```

This shows type checking, the symbol table, and scope validation.

---

## Tutorial 3: Control Flow

### Step 1: Create a Loop Example

Create `loops.minipar`:

```minipar
# loops.minipar - Demonstrating control flow

func countdown(n: number) -> void {
    print("Starting countdown from", n)

    while (n >= 0) {
        print(n)
        n = n - 1
    }

    print("Liftoff!")
}

func count_even(limit: number) -> void {
    var i: number = 0

    while (i <= limit) {
        if (i % 2 == 0) {
            print("Even:", i)
        }
        i = i + 1
    }
}

countdown(5)
print("---")
count_even(10)
```

### Step 2: Compile and Test

**Linux/macOS:**
```bash
python3 compile.py loops.minipar --exe --output loops
./loops
```

**Windows:**
```bat
py compile.py loops.minipar --exe --output loops
.\loops.exe
```

Expected output:
```
Starting countdown from 5
5
4
3
2
1
0
Liftoff!
---
Even: 0
Even: 2
Even: 4
Even: 6
Even: 8
Even: 10
```

---

## Tutorial 4: Recursive Functions

### Step 1: Implement Factorial

Create `factorial.minipar`:

```minipar
# factorial.minipar - Recursive factorial

func factorial(n: number) -> number {
    if (n == 0 || n == 1) {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}

func test_factorial() -> void {
    var i: number = 0

    print("Factorial Table:")
    print("----------------")

    while (i <= 10) {
        var result: number = factorial(i)
        print("factorial(", i, ") =", result)
        i = i + 1
    }
}

test_factorial()
```

### Step 2: Compile and Run

**Linux/macOS:**
```bash
python3 compile.py factorial.minipar --exe --output factorial
./factorial
```

**Windows:**
```bat
py compile.py factorial.minipar --exe --output factorial
.\factorial.exe
```

Expected output:
```
Factorial Table:
----------------
factorial( 0 ) = 1
factorial( 1 ) = 1
factorial( 2 ) = 2
factorial( 3 ) = 6
factorial( 4 ) = 24
factorial( 5 ) = 120
factorial( 6 ) = 720
factorial( 7 ) = 5040
factorial( 8 ) = 40320
factorial( 9 ) = 362880
factorial( 10 ) = 3628800
```

---

## Tutorial 5: Complete Compilation Pipeline

### Understanding All Stages

Let's compile a program and see every step at once:

**Linux/macOS:**
```bash
python3 compile.py examples/ex1.minipar --tokens --ast --semantic --generate-c --exe --output complete_demo
```

**Windows:**
```bat
py compile.py examples\ex1.minipar --tokens --ast --semantic --generate-c --exe --output complete_demo
```

This performs:

#### Phase 1: Lexical Analysis
```
✓ Tokenization complete
```
Converts source code into tokens.

#### Phase 2: Syntax Analysis
```
✓ Parsing complete: AST with declarations
```
Builds the Abstract Syntax Tree.

#### Phase 3: Semantic Analysis
```
✓ Semantic analysis complete: No errors
```
Validates types, scopes, and semantics.

#### Phase 4: TAC Generation
```
✓ Code generation complete
```
Generates Three-Address Code.

#### Phase 5: ARM Assembly Generation
```
✓ ARM assembly saved to: complete_demo.s
```
Generates ARMv7 assembly (for CPUlator). Add `--no-asm` to skip this phase.

#### Phase 6: C Code Generation
```
✓ C code saved to: complete_demo.c
```
Translates TAC to C source.

#### Phase 7: Executable Generation
```
✓ Executable generated: complete_demo
```
GCC compiles the C source into a native binary.

### Run the Complete Demo

**Linux/macOS:**
```bash
./complete_demo
```

**Windows:**
```bat
.\complete_demo.exe
```

---

## Advanced Features

### 1. Inspect the Generated C Code

**Linux/macOS:**
```bash
python3 compile.py examples/ex5.minipar --generate-c --output program
cat program.c
```

**Windows:**
```bat
py compile.py examples\ex5.minipar --generate-c --output program
type program.c
```

### 2. Inspect the Generated ARM Assembly

ARM assembly (`.s`) is generated **by default** alongside `--exe`/`--generate-c`.
To view it:

**Linux/macOS:**
```bash
python3 compile.py examples/ex5.minipar --generate-c --output program
cat program.s
```

**Windows:**
```bat
py compile.py examples\ex5.minipar --generate-c --output program
type program.s
```

To **skip** ARM generation, add `--no-asm`:

```bash
python3 compile.py examples/ex5.minipar --exe --no-asm
```

> The ARM backend targets [CPUlator](https://cpulator.01xz.net/). For details, see
> [ARM_COMPILATION_GUIDE.md](ARM_COMPILATION_GUIDE.md).

### 3. The Modern Subcommand CLI (`minipar_cli.py`)

In addition to `compile.py`, the project ships a subcommand-based CLI. It works
identically on both platforms (only the interpreter name changes):

**Linux/macOS:**
```bash
python3 src/minipar_cli.py compile examples/ex1.minipar      # TAC
python3 src/minipar_cli.py ast examples/fatorial_rec.minipar # AST
python3 src/minipar_cli.py tac examples/ex5.minipar          # Three-Address Code
python3 src/minipar_cli.py generate-c examples/ex5.minipar --out /tmp/ex5.c
python3 src/minipar_cli.py generate-arm examples/ex5.minipar
python3 src/minipar_cli.py test                              # full test suite
```

**Windows:**
```bat
py src\minipar_cli.py compile examples\ex1.minipar
py src\minipar_cli.py ast examples\fatorial_rec.minipar
py src\minipar_cli.py tac examples\ex5.minipar
py src\minipar_cli.py generate-c examples\ex5.minipar --out %TEMP%\ex5.c
py src\minipar_cli.py generate-arm examples\ex5.minipar
py src\minipar_cli.py test
```

### 4. Run a Program Directly (Runtime Executor)

To execute a program without producing a binary (and to use channels), use the runner:

**Linux/macOS:**
```bash
python3 src/runner.py examples/ex5.minipar
```

**Windows:**
```bat
py src\runner.py examples\ex5.minipar
```

See [QUICK_START_CHANNELS.md](QUICK_START_CHANNELS.md) and
[CHANNEL_TUTORIAL.md](CHANNEL_TUTORIAL.md) for client/server channel programs.

### 5. Debug Mode (All Intermediate Steps)

**Linux/macOS:**
```bash
python3 compile.py examples/ex1.minipar --tokens --ast --semantic --exe
```

**Windows:**
```bat
py compile.py examples\ex1.minipar --tokens --ast --semantic --exe
```

---

## Testing All Examples

### Test Suite

Run all examples to verify everything works:

**Linux/macOS:**
```bash
python3 compile.py examples/ex1.minipar --exe --output test_ex1 && ./test_ex1
python3 compile.py examples/ex5.minipar --exe --output test_ex5 && ./test_ex5
python3 compile.py examples/fatorial_rec.minipar --exe --output test_factorial && ./test_factorial
```

**Windows:**
```bat
py compile.py examples\ex1.minipar --exe --output test_ex1 && .\test_ex1.exe
py compile.py examples\ex5.minipar --exe --output test_ex5 && .\test_ex5.exe
py compile.py examples\fatorial_rec.minipar --exe --output test_factorial && .\test_factorial.exe
```

### Expected Results

**ex1.minipar:**
```
11
12
13
14
15
15
```

**ex5.minipar:**
```
10
9
8
7
6
5
4
3
2
1
0
```

**fatorial_rec.minipar:**
```
CALCULA O FATORIAL RECURSIVO
Fatorial:  3628800
```

### Run the Automated Test Suite

**Linux/macOS:**
```bash
python3 run_tests.py
# or, with pytest:
python3 -m pytest -q
```

**Windows:**
```bat
py run_tests.py
py -m pytest -q
```

---

## Command-Line Reference

### Basic Commands

```bash
# Compile to a native executable (also writes output.c and output.s)
python3 compile.py <file.minipar> --exe        # Windows: py compile.py ...

# Generate C code only
python3 compile.py <file.minipar> --generate-c
```

### Complete Flag List

```
Usage: python3 compile.py <source_file> [options]    (Windows: py compile.py ...)

Options:
  --tokens          Show token stream
  --ast             Show abstract syntax tree
  --semantic        Show semantic analysis details
  --generate-c      Generate C code (output.c)
  --output <name>   Base name for generated files (default: output)
  --exe             Compile to a native executable via GCC
  --no-asm          Skip ARM assembly generation (ARM is generated by default)
```

> ℹ️ The older `--asm` and `--arch` flags have been **removed**. ARM assembly is now
> emitted automatically (unless you pass `--no-asm`), and native executables are built
> for your current machine via GCC.

---

## Project Structure Explained

```
projeto_compiladores/
├── src/                      # Compiler source code
│   ├── lexer.py             # Lexical analyzer
│   ├── parser.py            # Syntax analyzer
│   ├── ast_nodes.py         # AST definitions
│   ├── semantic.py          # Semantic analyzer
│   ├── symbol_table.py      # Symbol table
│   ├── codegen.py           # TAC generator
│   ├── c_codegen.py         # C code generator
│   ├── arm_codegen.py       # ARMv7 (CPUlator) generator
│   ├── backend.py           # GCC integration
│   ├── runner.py            # Runtime executor (channels)
│   ├── minipar_cli.py       # Subcommand CLI
│   └── compiler.py          # Main driver
│
├── examples/                 # Example programs (.minipar)
├── compile.py                # Convenience wrapper around src/compiler.py
├── run_tests.py              # Test runner
└── docs/                     # Documentation
```

---

## Troubleshooting

### Problem: "gcc not found"

**Solution:** Install GCC (see Prerequisites), then make sure it's on your `PATH` and
restart the terminal.

**Windows (MSYS2 / MinGW example):**
```bat
set PATH=%PATH%;C:\msys64\mingw64\bin
```

**Linux:**
```bash
sudo apt-get install gcc   # Debian/Ubuntu
```

> You only need GCC for the `--exe` step. Without it, `--tokens`, `--ast`,
> `--semantic`, `--generate-c`, and ARM generation still work.

### Problem: "Python not found"

**Windows:** Use `py` instead of `python`:
```bat
py compile.py program.minipar --exe
```

**Linux/macOS:** Use `python3`:
```bash
python3 compile.py program.minipar --exe
```

### Problem: Compilation errors

**Check:**
1. Syntax errors in your `.minipar` file
2. Run with `--semantic` to see detailed errors
3. Review the example programs for correct syntax
4. Don't name a function `main` (it collides with C's `main()`)

### Problem: "Module not found"

**Solution:** Make sure you're in the project root directory:

**Linux/macOS:**
```bash
cd projeto_compiladores
python3 compile.py examples/ex5.minipar --exe
```

**Windows:**
```bat
cd projeto_compiladores
py compile.py examples\ex5.minipar --exe
```

### Problem: Executable won't run

**Linux/macOS:**
```bash
ls output           # confirm it exists
chmod +x output     # ensure it's executable
./output            # run with explicit ./ prefix
```

**Windows:**
```bat
dir output.exe
.\output.exe
```

---

## Language Reference Quick Guide

### Variable Declaration
```minipar
var name: type = value
```

### Function Declaration
```minipar
func name(param1: type1, param2: type2) -> return_type {
    # body
    return value
}
```

### Control Flow
```minipar
if (condition) {
    # code
} else {
    # code
}

while (condition) {
    # code
    break      # exit loop
    continue   # next iteration
}
```

### Types
- `number` - Integers and floats
- `string` - Text strings
- `bool` - true/false
- `void` - No return value

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Relational: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `&&`, `||`, `!`

### Built-in Functions
- `print(...)` - Print values to console
- `input(...)` - Read input

---

## Next Steps

1. **Read the docs:** See [README.md](../../README.md) for the full feature list.
2. **Study examples:** All example programs live in the `examples/` folder.
3. **Try channels:** [QUICK_START_CHANNELS.md](QUICK_START_CHANNELS.md) walks through a
   client/server program across two terminals.
4. **Explore ARM:** [ARM_COMPILATION_GUIDE.md](ARM_COMPILATION_GUIDE.md) covers the
   CPUlator workflow.

---

## Useful Commands Summary

**Linux/macOS:**
```bash
# Quick compile and run
python3 compile.py examples/ex5.minipar --exe && ./output

# See all compilation stages
python3 compile.py program.minipar --tokens --ast --semantic --exe

# View generated C code
python3 compile.py program.minipar --generate-c && cat output.c

# Run all examples
for f in examples/*.minipar; do
    python3 compile.py "$f" --exe --output "test_$(basename "$f" .minipar)"
done
```

**Windows (cmd):**
```bat
:: Quick compile and run
py compile.py examples\ex5.minipar --exe && .\output.exe

:: See all compilation stages
py compile.py program.minipar --tokens --ast --semantic --exe

:: View generated C code
py compile.py program.minipar --generate-c && type output.c

:: Run all examples
for %f in (examples\*.minipar) do py compile.py %f --exe --output test_%~nf
```

---

## Success Checklist

After completing this tutorial, you should be able to:

- [ ] Compile a Minipar program to an executable on Windows **and** Linux
- [ ] Create your own Minipar programs
- [ ] Understand the compilation pipeline
- [ ] Use all compiler flags effectively
- [ ] Debug compilation errors
- [ ] View intermediate representations (tokens, AST, C, ARM)
- [ ] Run programs directly with the runtime executor

---

## Conclusion

You now have a complete, cross-platform understanding of how to use the Minipar Compiler!

**Key Takeaways:**
- ✅ Complete compilation pipeline working on Windows and Linux
- ✅ Multiple output formats (C, ARM assembly, native executable)
- ✅ Comprehensive debugging options
- ✅ Two CLIs (`compile.py` and `src/minipar_cli.py`) plus a runtime executor

Happy compiling! 🎉

---

**Tutorial Version:** 2.0
**Last Updated:** 2026-06-14
**Tested On:** Linux (Python 3.14, GCC 16) and Windows 10/11 (Python 3.13, MinGW GCC)
**Project Status:** Production Ready ✅
