# 🏃 How to Run Assembly Code - DEPRECATED

**⚠️ NOTICE: Assembly generation has been removed.**

The `--asm` flag has been removed from the compiler as it was incorrectly implemented.

The compiler now only generates executables directly using GCC.

---

## 🎯 Current Method

The **only way** to compile programs is to generate the executable directly:

```bash
py compile.py program.minipar --exe
.\output.exe
```

For the current compiler capabilities, see:
- [README.md](../../README.md)
- [TUTORIAL.md](TUTORIAL.md)

---

## Original Documentation (For Reference Only)

**Complete Guide to Executing Generated Assembly Files**

---

## 📋 Table of Contents

1. [Method 1: Direct Compilation (Easiest)](#method-1-direct-compilation-easiest)
2. [Method 2: Two-Step Process](#method-2-two-step-process)
3. [Method 3: Study Assembly Only](#method-3-study-assembly-only)
4. [Method 4: Using a Debugger](#method-4-using-a-debugger)
5. [Platform-Specific Instructions](#platform-specific-instructions)
6. [Troubleshooting](#troubleshooting)

---

## Method 1: Direct Compilation (Easiest)

### Generate Assembly + Executable Together

```bash
# One command does everything
py src\compiler.py examples\ex5.minipar --asm --exe

# Creates:
# - output.s (assembly)
# - output.exe (executable)

# Run it:
.\output.exe
```

### With Custom Names

```bash
py src\compiler.py examples\ex5.minipar --asm --exe --output countdown

# Creates:
# - countdown.s
# - countdown.exe

# Run:
.\countdown.exe
```

**This is the recommended method!** ✅

---

## Method 2: Two-Step Process

### Step 1: Generate Assembly

```bash
py src\compiler.py examples\ex5.minipar --asm --output myprogram
```

**Output:** `myprogram.s` (assembly file)

### Step 2: Compile to Executable

**Windows:**
```bash
gcc myprogram.s -o myprogram.exe
.\myprogram.exe
```

**Linux/Mac:**
```bash
gcc myprogram.s -o myprogram
./myprogram
```

### Why Use This Method?

- Inspect assembly before running
- Modify assembly manually
- Learn assembly programming
- Debug compilation issues

---

## Method 3: Study Assembly Only

**If you just want to see/study the assembly code:**

### Generate Assembly

```bash
py src\compiler.py examples\ex5.minipar --asm --output study
```

### View Assembly

**Windows:**
```powershell
type study.s
# or
notepad study.s
# or
code study.s  # VS Code
```

**Linux/Mac:**
```bash
cat study.s
# or
less study.s
# or
nano study.s
```

### Understanding the Assembly

**Example output (x86):**
```assembly
_count:
    pushl   %ebx              # Save register
    subl    $24, %esp         # Allocate stack space
    movl    32(%esp), %ebx    # Load parameter
    testl   %ebx, %ebx        # Test if negative
    js      L3                # Jump if negative
L7:
    movl    %ebx, 4(%esp)     # Prepare argument
    movl    $LC0, (%esp)      # Load format string
    subl    $1, %ebx          # Decrement counter
    call    _printf           # Call printf
    cmpl    $-1, %ebx         # Compare with -1
    jne     L7                # Loop if not equal
L3:
    addl    $24, %esp         # Deallocate stack
    popl    %ebx              # Restore register
    ret                       # Return
```

---

## Method 4: Using a Debugger

### GDB (GNU Debugger)

**Generate with debug symbols:**
```bash
py src\compiler.py examples\ex5.minipar --asm --output debug_prog
gcc -g debug_prog.s -o debug_prog.exe
```

**Run in GDB:**
```bash
gdb debug_prog.exe
```

**GDB Commands:**
```gdb
(gdb) break main              # Set breakpoint at main
(gdb) run                     # Start program
(gdb) step                    # Execute one instruction
(gdb) next                    # Execute one line
(gdb) info registers          # Show register values
(gdb) disassemble             # Show assembly
(gdb) print $eax              # Print register value
(gdb) continue                # Continue execution
(gdb) quit                    # Exit GDB
```

### Visual Studio Debugger (Windows)

**Open in VS:**
```bash
# Compile with debug info
gcc -g program.s -o program.exe

# Open in Visual Studio and press F5
devenv program.exe
```

---

## Platform-Specific Instructions

### 🪟 Windows

#### Using MinGW GCC

```bash
# Generate assembly
py src\compiler.py program.minipar --asm --output prog

# Compile
gcc prog.s -o prog.exe

# Run
.\prog.exe
```

#### Using MSVC (Microsoft Compiler)

```bash
# MSVC uses different syntax (MASM)
# Use GCC-generated assembly instead
# Or manually convert to MASM syntax
```

---

### 🐧 Linux

```bash
# Generate assembly
python3 src/compiler.py program.minipar --asm --output prog

# Compile
gcc prog.s -o prog

# Make executable
chmod +x prog

# Run
./prog
```

**With optimization:**
```bash
gcc -O2 prog.s -o prog
```

---

### 🍎 macOS

```bash
# Same as Linux
python3 src/compiler.py program.minipar --asm --output prog
gcc prog.s -o prog
chmod +x prog
./prog
```

**Note:** macOS uses different calling conventions, test carefully.

---

## 🔍 Complete Workflow Example

Let's run a complete example step by step:

### Example: Countdown Program

**Source Code (countdown.minipar):**
```minipar
var num: number = 5

func count_down(n: number) -> void {
    while(n >= 0) {
        print(n)
        n = n - 1
    }
}

count_down(num)
```

### Workflow:

```bash
# Step 1: Compile source to assembly
py src\compiler.py countdown.minipar --asm --output countdown

# Output:
# ✓ Tokenization complete: 32 tokens
# ✓ Code generation complete: 18 instructions
# ✓ Assembly generated: countdown.s

# Step 2: Check assembly file
type countdown.s

# Step 3: Compile assembly to executable
gcc countdown.s -o countdown.exe

# Step 4: Run executable
.\countdown.exe

# Output:
# 5
# 4
# 3
# 2
# 1
# 0
```

---

## 📊 File Types Explained

| Extension | Type | Purpose | Can Run? |
|-----------|------|---------|----------|
| `.minipar` | Source | Your program | ❌ No |
| `.c` | C Source | Generated C | ❌ No |
| `.s` | Assembly | Generated ASM | ❌ No |
| `.o` | Object | Compiled code | ❌ No |
| `.exe` | Executable | Final program | ✅ **Yes!** |

**To run code, you MUST have a `.exe` (Windows) or executable file (Linux/Mac).**

---

## 🎓 Advanced Techniques

### 1. Compile with Optimization

```bash
# Generate assembly
py src\compiler.py program.minipar --asm --output prog

# Compile with O2 optimization
gcc -O2 prog.s -o prog_optimized.exe

# Compare file sizes
dir prog*.exe
```

### 2. Generate Assembly Listing

```bash
# Create annotated assembly
gcc -Wa,-adhln -g prog.s > prog_listing.txt
```

### 3. View Object Code

```bash
# Compile to object file
gcc -c prog.s -o prog.o

# Disassemble object file
objdump -d prog.o > prog_disasm.txt
```

### 4. Profile Performance

```bash
# Compile with profiling
gcc -pg prog.s -o prog.exe

# Run program
.\prog.exe

# View profile
gprof prog.exe gmon.out > profile.txt
```

---

## 🐛 Troubleshooting

### Problem 1: "gcc: command not found"

**Solution:** Install GCC compiler

**Windows:**
```bash
# Install MinGW from mingw.org
# Or use MSYS2
```

**Linux:**
```bash
sudo apt-get install gcc
```

**macOS:**
```bash
xcode-select --install
```

---

### Problem 2: Assembly file has errors

**Check:**
```bash
# Verify assembly syntax
gcc -c prog.s -o prog.o

# If errors, regenerate:
py src\compiler.py program.minipar --asm --output prog
```

---

### Problem 3: Executable won't run

**Windows:**
```bash
# Check if created
dir *.exe

# Check permissions
icacls prog.exe

# Try running with full path
.\prog.exe
```

**Linux/Mac:**
```bash
# Make executable
chmod +x prog

# Run with full path
./prog
```

---

### Problem 4: Wrong architecture

**Problem:** Generated x86 assembly on x64 system

**Solution:**
```bash
# Compile as 32-bit
gcc -m32 prog.s -o prog.exe

# Or generate for x86-64:
py src\compiler.py program.minipar --asm --arch x86_64 --output prog
```

---

## 🎯 Quick Reference Commands

```bash
# ===== ONE-STEP (RECOMMENDED) =====
py src\compiler.py file.minipar --exe
.\output.exe

# ===== TWO-STEP =====
py src\compiler.py file.minipar --asm --output prog
gcc prog.s -o prog.exe
.\prog.exe

# ===== VIEW ASSEMBLY =====
py src\compiler.py file.minipar --asm --output prog
type prog.s

# ===== DEBUG =====
py src\compiler.py file.minipar --asm --output prog
gcc -g prog.s -o prog.exe
gdb prog.exe

# ===== WITH OPTIMIZATION =====
py src\compiler.py file.minipar --asm --output prog
gcc -O2 prog.s -o prog.exe
.\prog.exe
```

---

## 💡 Best Practices

### ✅ Do This:

1. **Use `--exe` flag** for quick testing
2. **Specify output names** with `--output`
3. **Keep assembly files** for learning
4. **Test incrementally** with small programs
5. **Use debugger** for understanding execution

### ❌ Avoid This:

1. Don't edit assembly unless you know what you're doing
2. Don't delete `.c` files if you want to debug
3. Don't mix 32-bit and 64-bit code
4. Don't forget to regenerate after source changes

---

## 🔄 Comparison: Different Methods

### Method Comparison

| Method | Speed | Convenience | Learning Value |
|--------|-------|-------------|----------------|
| Direct `--exe` | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| Two-step | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Study only | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| With debugger | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ |

**Recommendation:**
- **Testing:** Use `--exe` (Method 1)
- **Learning:** Use two-step (Method 2)
- **Deep understanding:** Use debugger (Method 4)

---

## 📚 Additional Resources

### Assembly Learning

- **x86 Assembly Guide:** https://www.cs.virginia.edu/~evans/cs216/guides/x86.html
- **GDB Tutorial:** https://www.gnu.org/software/gdb/documentation/
- **GCC Assembly:** https://gcc.gnu.org/onlinedocs/gcc/Extended-Asm.html

### Tools

- **GDB:** GNU Debugger
- **objdump:** View object files
- **readelf:** Inspect ELF files (Linux)
- **dumpbin:** Inspect PE files (Windows)

---

## ✅ Testing Checklist

Before running assembly:

- [ ] Generated `.s` file exists
- [ ] GCC compiler installed and in PATH
- [ ] Correct architecture selected
- [ ] Assembly has no syntax errors
- [ ] Output name specified (optional)

---

## 🎉 Success Example

Complete successful run:

```bash
C:\projeto_compiladores> py src\compiler.py examples\ex5.minipar --asm --exe

Compiling: examples\ex5.minipar
============================================================
=== Lexical Analysis ===
✓ Tokenization complete: 39 tokens

=== Syntax Analysis ===
✓ Parsing complete: AST with 3 declarations

=== Semantic Analysis ===
✓ Semantic analysis complete: No errors

=== Code Generation (TAC) ===
✓ Code generation complete: 15 instructions

=== C Code Generation ===
✓ C code generated: output.c

=== Backend Compilation ===
GCC: gcc (MinGW.org GCC-6.3.0-1) 6.3.0
Architecture: native

Compiling to assembly...
✓ Assembly generated: output.s

Compiling to executable...
✓ Executable generated: output.exe
============================================================

C:\projeto_compiladores> .\output.exe
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

C:\projeto_compiladores> echo %ERRORLEVEL%
0

✓ SUCCESS!
```

---

**Summary:** 
1. **Easiest:** Use `--exe` flag to generate executable directly
2. **Learning:** Use `--asm` to study assembly, then compile manually
3. **Debugging:** Use GDB to step through instructions
4. **Remember:** Assembly files (`.s`) cannot run directly - they must be compiled to executables!

---

**Created:** October 22, 2025  
**Last Updated:** October 22, 2025  
**Tested On:** Windows 10, MinGW GCC 6.3.0  
**Status:** ✅ Complete and Verified
