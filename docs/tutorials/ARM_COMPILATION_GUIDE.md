# 🔄 ARM Compilation Guide

> **⚠️ The old `--arch` / `--asm` flags were removed.** ARM assembly is now generated
> **automatically** for the CPUlator ARMv7 target. The current workflow below replaces
> the historical instructions kept at the bottom for reference.

## ✅ Current ARM Workflow (Windows & Linux)

The compiler emits ARMv7 assembly (`.s`) by default whenever you run `compile.py`.
There is **no flag needed** to get ARM — use `--no-asm` only if you want to skip it.

**Linux/macOS:**
```bash
# Generates output.c, output.s (ARM), and the native executable
python3 compile.py examples/ex5.minipar --exe

# View the ARM assembly
cat output.s

# Custom output base name (writes myprog.c and myprog.s):
python3 compile.py examples/ex5.minipar --generate-c --output myprog
cat myprog.s
```

**Windows:**
```bat
:: Generates output.c, output.s (ARM), and output.exe
py compile.py examples\ex5.minipar --exe

:: View the ARM assembly
type output.s
```

You can also use the subcommand CLI, which prints/saves ARM directly:

**Linux/macOS:**
```bash
python3 src/minipar_cli.py generate-arm examples/ex5.minipar
```

**Windows:**
```bat
py src\minipar_cli.py generate-arm examples\ex5.minipar
```

> The generated `.s` targets [CPUlator](https://cpulator.01xz.net/) (ARMv7). Paste the
> contents of `output.s` into CPUlator to run/inspect it. Note that `print` is a stub in
> the ARM backend — arithmetic and control flow are validated via registers and the
> Memory tab rather than console output.

For the rest of the compiler's capabilities, see:
- [README.md](../../README.md)
- [TUTORIAL.md](TUTORIAL.md)

---

## Original Documentation (Historical — uses removed `--arch`/`--asm` flags)

**Quick Guide to Targeting Different Architectures**

---

## 🎯 Quick Commands

### Target x86 (Native - Default)
```bash
py src\compiler.py program.minipar --asm --arch native
```

### Target ARMv7
```bash
py src\compiler.py program.minipar --asm --arch armv7
```

### Target x86-64
```bash
py src\compiler.py program.minipar --asm --arch x86_64
```

---

## 📋 Prerequisites

### For ARMv7 Cross-Compilation

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install gcc-arm-linux-gnueabihf
```

**Linux (Other):**
```bash
# Fedora/RHEL
sudo dnf install gcc-arm-linux-gnu

# Arch Linux
sudo pacman -S arm-none-eabi-gcc
```

**macOS:**
```bash
brew tap osx-cross/arm
brew install arm-gcc-bin
```

**Windows:**
1. Download from [ARM Developer](https://developer.arm.com/downloads/-/gnu-rm)
2. Or use MSYS2:
   ```bash
   pacman -S mingw-w64-x86_64-arm-none-eabi-gcc
   ```

### Verify Installation

```bash
# Check ARM GCC
arm-linux-gnueabihf-gcc --version

# Should output something like:
# arm-linux-gnueabihf-gcc (Ubuntu/Linaro ...) 9.4.0
```

---

## 🔨 Compilation Examples

### Example 1: Simple Program

**Minipar Code (simple.minipar):**
```minipar
var x: number = 42
print(x)
```

**Compile for x86:**
```bash
py src\compiler.py simple.minipar --asm --arch native --output simple_x86
```

**Compile for ARMv7:**
```bash
py src\compiler.py simple.minipar --asm --arch armv7 --output simple_arm
```

---

### Example 2: Function with Loop

**Minipar Code (countdown.minipar):**
```minipar
func countdown(n: number) -> void {
    while (n >= 0) {
        print(n)
        n = n - 1
    }
}

countdown(5)
```

**Compare Architectures:**
```bash
# Generate x86 assembly
py src\compiler.py countdown.minipar --asm --arch native --output countdown_x86

# Generate ARMv7 assembly
py src\compiler.py countdown.minipar --asm --arch armv7 --output countdown_arm

# Compare files
diff countdown_x86.s countdown_arm.s
```

---

## 📊 Architecture Comparison

### x86 Assembly Characteristics

**Syntax:** AT&T syntax (default on Linux/GCC)
```assembly
movl    $42, %eax        # Move 42 into register eax
pushl   %ebx             # Push ebx onto stack
call    _printf          # Call function
```

**Registers:**
- General: `%eax`, `%ebx`, `%ecx`, `%edx`
- Stack: `%esp` (stack pointer), `%ebp` (base pointer)
- 32-bit registers for x86, 64-bit for x86_64

**Stack:**
- Grows downward
- Push/pop instructions

---

### ARMv7 Assembly Characteristics

**Syntax:** ARM syntax
```assembly
mov     r0, #42          @ Move 42 into register r0
push    {r4, lr}         @ Push registers onto stack
bl      printf           @ Branch with link (call)
```

**Registers:**
- General: `r0-r12` (13 general-purpose registers)
- Special: `sp` (r13, stack pointer), `lr` (r14, link register), `pc` (r15, program counter)
- `r0-r3` used for function arguments

**Characteristics:**
- RISC architecture (simpler instructions)
- Load/Store architecture (memory access only via load/store)
- Conditional execution on most instructions

---

## 🔍 Detailed Examples

### Example Program

**Input (ex5.minipar):**
```minipar
var num: number = 10

func count(n: number) -> void {
    while(n >= 0) {
        print(n)
        n = n - 1
    }
}

count(num)
```

### x86 Assembly Output

```assembly
_count:
    pushl   %ebx                    # Save register
    subl    $24, %esp               # Allocate stack space
    movl    32(%esp), %ebx          # Load parameter n
    testl   %ebx, %ebx              # Test if n < 0
    js      L3                      # Jump if negative
L7:
    movl    %ebx, 4(%esp)           # Prepare printf argument
    movl    $LC0, (%esp)            # Format string
    subl    $1, %ebx                # n = n - 1
    call    _printf                 # Call printf
    cmpl    $-1, %ebx               # Compare n with -1
    jne     L7                      # Loop if not equal
L3:
    addl    $24, %esp               # Deallocate stack
    popl    %ebx                    # Restore register
    ret                             # Return
```

### ARMv7 Assembly Output (Expected)

```assembly
count:
    push    {r4, lr}                @ Save registers
    mov     r4, r0                  @ r4 = n (parameter)
    cmp     r4, #0                  @ Compare n with 0
    blt     .L3                     @ Branch if less than
.L7:
    mov     r1, r4                  @ Prepare printf argument
    ldr     r0, =.LC0               @ Load format string
    bl      printf                  @ Call printf
    sub     r4, r4, #1              @ n = n - 1
    cmp     r4, #-1                 @ Compare n with -1
    bne     .L7                     @ Branch if not equal
.L3:
    pop     {r4, pc}                @ Restore and return
```

---

## 🎓 Key Differences

| Feature | x86 | ARMv7 |
|---------|-----|-------|
| **Architecture** | CISC | RISC |
| **Registers** | 8 general (x86), 16 (x86-64) | 16 general |
| **Instructions** | Variable length | Fixed 32-bit |
| **Memory Access** | Direct from instructions | Load/Store only |
| **Calling Convention** | Stack-based | Register-based (r0-r3) |
| **Return Value** | %eax | r0 |
| **Stack Pointer** | %esp | sp (r13) |
| **Conditional** | Flags + jump | Condition codes on any inst |

---

## 🚀 Complete Workflow

### 1. Generate C Code First (Optional)

```bash
py src\compiler.py program.minipar --generate-c --output program
```

This creates `program.c` which you can inspect before generating assembly.

### 2. Generate Assembly for Multiple Architectures

```bash
# x86 (32-bit)
py src\compiler.py program.minipar --asm --arch native --output program_x86

# x86-64 (64-bit)
py src\compiler.py program.minipar --asm --arch x86_64 --output program_x64

# ARMv7 (32-bit ARM)
py src\compiler.py program.minipar --asm --arch armv7 --output program_arm
```

### 3. Generate Executable for Target

```bash
# Native executable (runs on your machine)
py src\compiler.py program.minipar --exe --arch native --output program_native

# ARM executable (needs ARM hardware or emulator)
py src\compiler.py program.minipar --exe --arch armv7 --output program_arm
```

---

## 🔧 Testing ARM Executables

### Option 1: QEMU Emulator (Recommended)

**Install QEMU:**
```bash
# Linux
sudo apt-get install qemu-user

# macOS
brew install qemu
```

**Run ARM Executable:**
```bash
qemu-arm ./program_arm
```

### Option 2: ARM Hardware

- Raspberry Pi (ARMv7 or ARMv8)
- BeagleBone
- ARM development boards

**Transfer and run:**
```bash
scp program_arm pi@raspberrypi:/home/pi/
ssh pi@raspberrypi
./program_arm
```

### Option 3: Cross-Compilation Test

Just generate assembly to verify syntax:
```bash
py src\compiler.py program.minipar --asm --arch armv7 --output test_arm

# Verify assembly syntax
arm-linux-gnueabihf-gcc -c test_arm.s -o test_arm.o
```

---

## 💡 Practical Use Cases

### Use x86 When:
- Testing on your development machine (Windows/Linux/Mac x86)
- Learning assembly basics
- Quick compilation and testing
- **Current default for this project**

### Use ARMv7 When:
- Targeting embedded systems
- Raspberry Pi projects
- Mobile/IoT devices
- Learning ARM architecture
- Cross-platform development

---

## 🎯 Common Commands Reference

```bash
# Quick compile and view assembly
py src\compiler.py file.minipar --asm --arch armv7 && cat output.s

# Generate both architectures
py src\compiler.py file.minipar --asm --arch native --output x86
py src\compiler.py file.minipar --asm --arch armv7 --output arm

# Generate all outputs for ARM
py src\compiler.py file.minipar --generate-c --asm --exe --arch armv7 --output arm_build

# Compare architectures
diff x86.s arm.s | less
```

---

## ⚠️ Common Issues

### Issue 1: ARM Compiler Not Found

**Problem:**
```
⚠️ Warning: ARM cross-compiler not found, using native GCC
```

**Solution:**
Install ARM GCC cross-compiler (see Prerequisites section)

---

### Issue 2: Wrong Architecture in Assembly

**Problem:** Generated assembly doesn't match expected architecture

**Solution:** Verify you specified `--arch` flag:
```bash
py src\compiler.py file.minipar --asm --arch armv7  # ✅ Correct
py src\compiler.py file.minipar --asm               # ❌ Uses native
```

---

### Issue 3: Can't Run ARM Executable on x86

**Problem:** ARM executable won't run on x86 machine

**Solution:** This is expected! Options:
1. Use QEMU emulator: `qemu-arm ./program`
2. Transfer to ARM hardware
3. Or just generate assembly for inspection

---

## 📚 Additional Resources

### GCC ARM Options Used

The compiler uses these GCC flags for ARMv7:
```bash
-march=armv7-a          # Target ARMv7-A architecture
-mfloat-abi=hard       # Use hardware floating-point
-mfpu=vfpv3-d16        # VFP v3 floating-point unit
```

### ARM Documentation

- [ARM Architecture Reference](https://developer.arm.com/documentation/)
- [ARM Assembly Basics](https://azeria-labs.com/writing-arm-assembly-part-1/)
- [GCC ARM Options](https://gcc.gnu.org/onlinedocs/gcc/ARM-Options.html)

---

## ✅ Quick Checklist

Before compiling for ARMv7:

- [ ] ARM cross-compiler installed
- [ ] Verified with `arm-linux-gnueabihf-gcc --version`
- [ ] Added `--arch armv7` flag
- [ ] Specified output name with `--output`
- [ ] Have QEMU or ARM hardware for testing (if generating executable)

---

## 🎉 Success Example

```bash
# Complete example
$ py src\compiler.py examples\ex5.minipar --asm --arch armv7 --output countdown_arm

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
✓ C code generated: countdown_arm.c

=== Backend Compilation ===
GCC: arm-linux-gnueabihf-gcc (Ubuntu 9.4.0) 9.4.0
Architecture: armv7

Compiling to assembly...
✓ Assembly generated: countdown_arm.s
============================================================

$ file countdown_arm.s
countdown_arm.s: assembler source, ASCII text

$ head -20 countdown_arm.s
        .arch armv7-a
        .fpu vfpv3-d16
        .file   "countdown_arm.c"
        .text
        .align  2
        .global count
        .type   count, %function
count:
        push    {r4, lr}
        mov     r4, r0
        ...
```

---

**Summary:** Simply add `--arch armv7` to any compilation command to target ARM instead of x86!

---

**Created:** January 10, 2025  
**Last Updated:** January 10, 2025  
**Tested On:** Windows 10, GCC 6.3.0  
**ARM Compiler:** arm-linux-gnueabihf-gcc 9.4.0 (Linux)
