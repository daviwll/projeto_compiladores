# 🚀 Minipar Compiler - Complete Tutorial

**A Step-by-Step Guide to Building and Running Your First Minipar Programs**

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Tutorial 1: Hello World](#tutorial-1-hello-world)
5. [Tutorial 2: Variables and Functions](#tutorial-2-variables-and-functions)
6. [Tutorial 3: Control Flow](#tutorial-3-control-flow)
7. [Tutorial 4: Recursive Functions](#tutorial-4-recursive-functions)
8. [Tutorial 5: Complete Compilation Pipeline](#tutorial-5-complete-compilation-pipeline)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
1. **Python 3.7+** - [Download](https://www.python.org/downloads/)
2. **GCC Compiler** - For generating executables
   - **Windows**: [MinGW](http://www.mingw.org/) or install via [MSYS2](https://www.msys2.org/)
   - **Linux**: `sudo apt-get install gcc`
   - **macOS**: Install Xcode Command Line Tools: `xcode-select --install`

### Verify Installation

```bash
# Check Python version
python --version
# or
py --version

# Check GCC installation
gcc --version
```

Expected output:
```
Python 3.7.0 (or higher)
gcc (MinGW.org GCC-6.3.0-1) 6.3.0 (or similar)
```

---

## Installation

### Step 1: Navigate to Project Directory

```bash
cd C:\Users\gui\Documents\code\compiladores\projeto_compiladores
```

Or wherever you have the project.

### Step 2: Verify Project Structure

```bash
# Windows
dir

# Linux/Mac
ls -la
```

You should see:
- `src/` folder (compiler source code)
- `examples/` folder (example programs)
- `README.md`
- Other documentation files

### Step 3: Test Compiler Installation

```bash
py src\compiler.py --help
```

Expected output: Usage information and available flags.

---

## Quick Start

### Compile Your First Program (One Command)

```bash
py src\compiler.py examples\ex5.minipar --exe
```

This will:
1. ✅ Tokenize the source code
2. ✅ Parse and build AST
3. ✅ Perform semantic analysis
4. ✅ Generate TAC (Three-Address Code)
5. ✅ Generate C code
6. ✅ Compile with GCC
7. ✅ Create executable

### Run the Program

```bash
# Windows
.\output.exe

# Linux/Mac
./output
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

func main() -> void {
    print("Hello, Minipar!")
    print("Welcome to compiler design!")
}

main()
```

### Step 2: Compile It

```bash
py src\compiler.py hello.minipar --exe --output hello
```

### Step 3: Run It

```bash
.\hello.exe
```

Expected output:
```
Hello, Minipar!
Welcome to compiler design!
```

### Step 4: See the Intermediate Steps

```bash
py src\compiler.py hello.minipar --tokens --ast --generate-c
```

This shows you:
- **Tokens**: How the lexer breaks down your code
- **AST**: The parse tree structure
- **C Code**: The generated C source

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

```bash
py src\compiler.py calculator.minipar --exe --output calculator
.\calculator.exe
```

Expected output:
```
Sum: 15
Product: 50
```

### Step 3: Understand the Compilation Phases

```bash
py src\compiler.py calculator.minipar --semantic
```

This shows:
- Type checking
- Symbol table
- Scope validation

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

```bash
py src\compiler.py loops.minipar --exe --output loops
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

### Step 2: Compile with Optimization

```bash
py src\compiler.py factorial.minipar --exe --output factorial
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

Let's compile a program and see every step:

```bash
py src\compiler.py examples\ex1.minipar --tokens --ast --semantic --generate-c --asm --exe --output complete_demo
```

This performs:

#### Phase 1: Lexical Analysis
```
✓ Tokenization complete: 75 tokens
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
✓ Code generation complete: 28 instructions
```
Generates Three-Address Code.

#### Phase 5: C Code Generation
```
✓ C code generated: complete_demo.c
```
Translates TAC to C code.

#### Phase 6: Assembly Generation
```
✓ Assembly generated: complete_demo.s
```
GCC generates assembly code.

#### Phase 7: Executable Generation
```
✓ Executable generated: complete_demo.exe
```
Final executable created.

### Run the Complete Demo

```bash
.\complete_demo.exe
```

---

## Advanced Features

### 1. Generate Only Assembly

```bash
py src\compiler.py examples\fatorial_rec.minipar --asm --output fatorial
```

This creates `fatorial.s` with optimized assembly code.

**View the assembly:**
```bash
# Windows
type fatorial.s

# Linux/Mac
cat fatorial.s
```

### 2. Inspect C Code

```bash
py src\compiler.py examples\ex5.minipar --generate-c --output program.c
```

**View the C code:**
```bash
# Windows
type program.c

# Linux/Mac
cat program.c
```

### 3. Target Different Architectures

```bash
# Native architecture (default)
py src\compiler.py program.minipar --asm --arch native

# ARM architecture (requires cross-compiler)
py src\compiler.py program.minipar --asm --arch armv7

# x86-64 architecture
py src\compiler.py program.minipar --asm --arch x86_64
```

### 4. Debug Mode (All Intermediate Steps)

```bash
py src\compiler.py examples\ex1.minipar --tokens --ast --semantic --exe
```

Shows:
- All tokens
- AST structure
- Symbol table
- Semantic validation
- Complete compilation

---

## Testing All Examples

### Test Suite

Run all examples to verify everything works:

```bash
# Test ex1
py src\compiler.py examples\ex1.minipar --exe --output test_ex1
.\test_ex1.exe

# Test ex5
py src\compiler.py examples\ex5.minipar --exe --output test_ex5
.\test_ex5.exe

# Test factorial
py src\compiler.py examples\fatorial_rec.minipar --exe --output test_factorial
.\test_factorial.exe
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

---

## Command-Line Reference

### Basic Commands

```bash
# Compile to executable
py compile.py <file.minipar> --exe

# Generate C code only
py compile.py <file.minipar> --generate-c
```

### Debug Flags

```bash
--tokens      # Show token stream
--ast         # Show abstract syntax tree
--semantic    # Show semantic analysis details
```

### Output Options

```bash
--output <name>    # Specify C output filename
```

### Complete Flag List

```
Usage: py compile.py <source_file> [options]

Options:
  --tokens              Show token stream
  --ast                 Show abstract syntax tree
  --semantic            Show semantic analysis details
  --generate-c          Generate C code
  --output <file>       Specify C output file
  --exe                 Compile to executable
```

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
│   ├── backend.py           # GCC integration
│   └── compiler.py          # Main driver
│
├── examples/                 # Example programs
│   ├── ex1.minipar          # Variables, loops
│   ├── ex5.minipar          # Functions
│   ├── fatorial_rec.minipar # Recursion
│   └── ...                  # More examples
│
└── docs/                     # Documentation
    ├── README.md            # Main documentation
    ├── ARCHITECTURE.md      # System design
    └── ...                  # Phase reports
```

---

## Troubleshooting

### Problem: "gcc not found"

**Solution:**
1. Install GCC (see Prerequisites)
2. Add GCC to PATH
3. Restart terminal

**Windows:**
```bash
# Add MinGW to PATH
set PATH=%PATH%;C:\MinGW\bin
```

### Problem: "Python not found"

**Solution:**
Use `py` instead of `python`:
```bash
py src\compiler.py program.minipar --exe
```

### Problem: Compilation errors

**Check:**
1. Syntax errors in your .minipar file
2. Run with `--semantic` to see detailed errors
3. Review example programs for correct syntax

### Problem: "Module not found"

**Solution:**
Make sure you're in the project root directory:
```bash
cd projeto_compiladores
py src\compiler.py examples\ex5.minipar --exe
```

### Problem: Executable won't run

**Check:**
1. Compilation succeeded (look for "✓ Executable generated")
2. File exists: `dir *.exe` (Windows) or `ls *.exe` (Linux)
3. Run from correct directory

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

---

## Performance Tips

### 1. Use GCC Optimization

The compiler uses `-O2` optimization by default, which provides:
- Loop unrolling
- Function inlining
- Dead code elimination
- Register optimization

### 2. Prefer Local Variables

Local variables are faster than global variables.

### 3. Minimize Function Calls in Loops

When possible, hoist function calls out of loops.

---

## Next Steps

### Learn More

1. **Read the docs:** Check out `docs/ARCHITECTURE.md` for system design
2. **Study examples:** All example programs in `examples/` folder
3. **Experiment:** Modify examples and see what happens
4. **Extend:** Add new features (see IMPLEMENTATION_PLAN.md)

### Advanced Topics

1. **Add array support** - Modify parser to support indexing
2. **Implement for loops** - Add new syntax to parser
3. **Optimize TAC** - Add optimization passes
4. **Target ARM** - Cross-compile for ARM devices

---

## Useful Commands Summary

```bash
# Quick compile and run
py src\compiler.py examples\ex5.minipar --exe && .\output.exe

# See all compilation stages
py src\compiler.py program.minipar --tokens --ast --semantic --exe

# Generate both assembly and executable
py src\compiler.py program.minipar --asm --exe --output myprogram

# View generated C code
py src\compiler.py program.minipar --generate-c && type output.c

# Test all examples
for %f in (examples\*.minipar) do (
    py src\compiler.py %f --exe --output test_%~nf
)
```

---

## Getting Help

### Resources

1. **Documentation:** `docs/` folder
2. **Examples:** `examples/` folder with working programs
3. **Phase Reports:** PHASE1_COMPLETE.md, PHASE2_COMPLETE.md, etc.
4. **Bug Reports:** BUGS_FOUND.md for known issues

### Quick Reference

- **Main compiler:** `src/compiler.py`
- **Example programs:** `examples/*.minipar`
- **Documentation:** `docs/*.md`
- **Test files:** `tests/*.py`

---

## Success Checklist

After completing this tutorial, you should be able to:

- [ ] Compile a Minipar program to executable
- [ ] Create your own Minipar programs
- [ ] Understand the compilation pipeline
- [ ] Use all compiler flags effectively
- [ ] Debug compilation errors
- [ ] Generate assembly code
- [ ] View intermediate representations
- [ ] Run and test programs

---

## Conclusion

You now have a complete understanding of how to use the Minipar Compiler! 

**Key Takeaways:**
- ✅ Complete compilation pipeline working
- ✅ Multiple output formats (C, Assembly, Executable)
- ✅ Comprehensive debugging options
- ✅ Production-ready code generation
- ✅ Cross-platform support

**Next Challenge:** Try creating your own Minipar program!

Happy compiling! 🎉

---

**Tutorial Version:** 1.0  
**Last Updated:** January 10, 2025  
**Tested On:** Windows 10, Python 3.7+, GCC 6.3.0  
**Project Status:** Production Ready ✅
