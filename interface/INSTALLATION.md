# 🚀 Minipar Compiler Web Interface - Complete Setup Guide

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Features Overview](#features-overview)
5. [Usage Guide](#usage-guide)
6. [Troubleshooting](#troubleshooting)
7. [API Reference](#api-reference)

---

## 📦 Prerequisites

### Required
- **Python 3.7 or higher**
  - Download: https://www.python.org/downloads/
  - Verify: `python --version` or `py --version`

### Optional (for executable generation)
- **GCC Compiler**
  - Windows: MinGW from http://www.mingw.org/
  - Linux: `sudo apt-get install gcc`
  - macOS: `xcode-select --install`

---

## 🔧 Installation

### Step 1: Install Gradio

Choose one method:

**Method 1: Using pip**
```bash
pip install gradio
```

**Method 2: Using py module (Windows)**
```bash
py -m pip install gradio
```

**Method 3: Using requirements.txt**
```bash
cd interface
pip install -r requirements.txt
```

### Step 2: Verify Installation

**Linux/macOS:**
```bash
cd interface
python3 test_setup.py
```

**Windows:**
```bat
cd interface
py test_setup.py
```

If all checks pass, you're ready! ✅

---

## ⚡ Quick Start

### Option 1: Use Launcher Script (Recommended)

**Windows:**
```bash
cd interface
start.bat
```

**Linux/Mac:**
```bash
cd interface
chmod +x start.sh
./start.sh
```

### Option 2: Manual Start

**Linux/macOS:**
```bash
cd interface
python3 app.py
```

**Windows:**
```bat
cd interface
py app.py
```

### Step 3: Access Interface

Open your browser to: **http://localhost:7860**

The interface will open automatically!

---

## ✨ Features Overview

### 📝 Compiler Tab

**Code Editor**
- Syntax highlighting
- Line numbers
- Auto-save warning
- Copy button

**Example Programs**
- Hello World
- Variables and Arithmetic
- Functions
- Loops
- Conditionals
- Factorial (Recursive)
- Input Example
- OO: Counter Class
- OO: Inheritance
- NN: Perceptron (Neuron)
- NN: Neural Network (XOR)

**Compilation Options** (Toggle buttons)
- 🔤 **Show Tokens** - Lexical analysis output
- 🌳 **Show AST** - Abstract syntax tree
- ✓ **Show Semantic** - Type checking results
- 📝 **Show TAC** - Three-address code (default: ON)
- ⚙️ **Show C Code** - Generated C source
- 🔧 **Show Assembly** - ARM assembly code

**Actions**
- 🔨 **Compile** - Run compilation with selected options
- 💾 **Compile & Download .exe** - Generate executable

**Output Display**
- Formatted compilation stages
- Syntax-highlighted code
- Copy-to-clipboard support
- Scrollable output area

---

### ▶️ Execute Tab

**Features**
- Execute programs directly in browser
- Provide program input
- Real-time output display
- Example program loader
- 10-second execution timeout

> ℹ️ The **Execute** tab runs your program through the Minipar **interpreter**
> (`src/runner.py`), which supports the full language — floating-point math, objects
> and inheritance, lists, and built-ins like `exp()`/`len()`. This is why programs such
> as **NN: Perceptron** and **NN: Neural Network (XOR)** run here even though the
> *Compile & Download .exe* path (C/GCC backend) only covers a simpler subset.

**Usage**
1. Write or load code
2. Enter input (if needed)
3. Click "Execute Program"
4. See results instantly!

---

### ❓ Help Tab

**Contents**
- Quick start guide
- Language reference
- Syntax examples
- Operators and keywords
- Built-in functions
- Troubleshooting tips

---

## 📖 Usage Guide

### Example 1: View Compilation Stages

1. **Load Example**
   - Click "Compiler" tab
   - Select "Loops" from dropdown
   - Code loads automatically

2. **Enable Options**
   - Check "Show Tokens"
   - Check "Show AST"
   - Check "Show TAC"

3. **Compile**
   - Click "🔨 Compile" button
   - View all selected stages in output

4. **Study Output**
   - Tokens show lexical analysis
   - AST shows parse tree
   - TAC shows intermediate code

---

### Example 2: Generate C Code

1. **Write Code**
   ```minipar
   func add(a: number, b: number) -> number {
       return a + b
   }
   
   print("Result:", add(5, 3))
   ```

2. **Enable C Generation**
   - Check "⚙️ Show C Code"

3. **Compile**
   - Click "🔨 Compile"

4. **View Generated C**
   - See complete C source code
   - Study how Minipar translates to C
   - Copy code if needed

---

### Example 3: Download Executable

1. **Write Your Program**
   ```minipar
   var counter: number = 10
   
   while (counter > 0) {
       print(counter)
       counter = counter - 1
   }
   
   print("Done!")
   ```

2. **Generate Executable**
   - Click "💾 Compile & Download .exe"
   - Wait for compilation (~3-5 seconds)

3. **Download**
   - Click download link
   - Save `minipar_program.exe`

4. **Run**
   - Double-click the executable
   - See your program run!

---

### Example 4: Execute Program

1. **Go to Execute Tab**
   - Click "▶️ Execute" tab

2. **Load Example**
   - Select "Factorial (Recursive)"
   - Code loads automatically

3. **Run Program**
   - Click "▶️ Execute Program"
   - See output instantly

4. **Try With Input**
   - Load a program that uses input
   - Type values in "Program Input" box
   - Execute and see results

---

## 🎯 Detailed Feature Guide

### Compilation Options Explained

#### 🔤 Show Tokens
Shows the output of lexical analysis:
```
Token(VAR, 'var', 1:1)
Token(IDENTIFIER, 'x', 1:5)
Token(COLON, ':', 1:6)
Token(NUMBER, 'number', 1:8)
...
```
**Use for:** Understanding tokenization, debugging lexical errors

#### 🌳 Show AST
Shows the abstract syntax tree structure:
```
Program(declarations=[
  VarDecl(type='number', name='x', initializer=NumberLiteral(value=10)),
  FuncDecl(return_type='void', name='greet', ...),
  ...
])
```
**Use for:** Understanding program structure, debugging parse errors

#### ✓ Show Semantic
Shows semantic analysis results:
```
✓ Semantic analysis complete
Symbol table populated
Type checking passed
No errors found
```
**Use for:** Verifying type correctness, checking variable scope

#### 📝 Show TAC (Default)
Shows three-address code (intermediate representation):
```
  0: x = 10
  1: FUNC_BEGIN greet
  2: PARAM name
  3: CALL print 1 t0
  4: FUNC_END greet
```
**Use for:** Understanding compilation process, learning IR

#### ⚙️ Show C Code
Shows complete generated C source code:
```c
#include <stdio.h>

int x = 10;

void greet(char* name) {
    printf("%s\n", name);
}

int main() {
    greet("World");
    return 0;
}
```
**Use for:** Learning code generation, understanding translation

#### 🔧 Show Assembly
Shows generated ARM assembly code:
```assembly
    .data
x:  .word 10

    .text
    .global main
greet:
    push {lr}
    ...
```
**Use for:** Understanding low-level code, learning assembly

---

## 🐛 Troubleshooting

### Installation Issues

#### Problem: "ModuleNotFoundError: No module named 'gradio'"

**Solution:**
```bash
pip install gradio
```

If pip doesn't work:
```bash
# Windows
py -m ensurepip
py -m pip install gradio

# Linux/Mac
python3 -m pip install gradio
```

#### Problem: "Python not found"

**Solution:**
1. Install Python from python.org
2. Check "Add Python to PATH" during installation
3. Restart terminal/command prompt
4. Verify: `python --version`

---

### Interface Issues

#### Problem: "Address already in use"

**Solution:**
```bash
# Kill existing process
# Windows: Ctrl+C in terminal
# Or change port in app.py:
app.launch(server_port=8080)
```

#### Problem: Interface won't open

**Solution:**
1. Check console for errors
2. Verify Gradio installed: `python -c "import gradio"`
3. Check firewall settings
4. Try different browser
5. Manually visit: http://localhost:7860

#### Problem: "Cannot find src directory"

**Solution:**
- Ensure you're running from `interface/` folder
- Check project structure:
  ```
  projeto_compiladores/
  ├── interface/
  │   └── app.py
  └── src/
      └── compiler.py
  ```

---

### Compilation Issues

#### Problem: Syntax errors in code

**Solution:**
1. Check error message carefully
2. Enable "Show Tokens" to verify lexical analysis
3. Enable "Show AST" to check syntax
4. Review Help tab for correct syntax
5. Try example programs first

#### Problem: "Compilation failed"

**Solution:**
1. Read error message in output
2. Check for missing semicolons, braces, or keywords
3. Verify variable types match
4. Ensure functions are defined before use
5. Compare with working examples

#### Problem: "GCC not found" (for .exe generation)

**Solution:**
- Install GCC compiler
- Windows: Download MinGW
- Linux: `sudo apt-get install gcc`
- macOS: `xcode-select --install`
- Or use "Compile" button instead of "Download"

---

### Execution Issues

#### Problem: "Execution timeout"

**Solution:**
- Check for infinite loops
- Reduce computation complexity
- Test with smaller inputs
- Download .exe and run locally for long programs

#### Problem: Program doesn't produce output

**Solution:**
1. Check if program has print statements
2. Verify logic is correct
3. Try in Compiler tab first to see compilation
4. Check for runtime errors in output

#### Problem: Input not working

**Solution:**
1. Ensure program uses input() function
2. Type input in "Program Input" box
3. Put each input value on separate line
4. Execute program after entering input

---

## 🔌 API Reference

### CompilerAPI Class

```python
from compiler_api import CompilerAPI

api = CompilerAPI()
```

#### Method: compile_code()

```python
result = api.compile_code(
    source_code: str,
    show_tokens: bool = False,
    show_ast: bool = False,
    show_semantic: bool = False,
    show_tac: bool = True,
    generate_c: bool = False,
    generate_asm: bool = False,
    generate_exe: bool = False
)
```

**Returns:**
```python
{
    'success': bool,
    'error': str,
    'output': str,
    'tokens': str,
    'ast': str,
    'semantic': str,
    'tac': str,
    'c_code': str,
    'assembly': str,
    'exe_file': dict or None
}
```

#### Method: execute_code()

```python
result = api.execute_code(
    source_code: str,
    user_input: str = ""
)
```

**Returns:**
```python
{
    'success': bool,
    'output': str,
    'error': str
}
```

---

### Frontend Functions

#### compile_and_show()

```python
output, log = compile_and_show(
    source_code,
    show_tokens,
    show_ast,
    show_semantic,
    show_tac,
    show_c,
    show_assembly
)
```

#### compile_and_download()

```python
file_path, message = compile_and_download(source_code)
```

#### execute_program()

```python
output = execute_program(source_code, user_input)
```

---

## 🎨 Customization

### Change Port

Edit `app.py`:
```python
app.launch(
    server_port=8080,  # Your port
    share=False
)
```

### Add Examples

Edit `EXAMPLES` dict in `app.py`:
```python
EXAMPLES = {
    "My Example": """# Your code
print("Hello!")
""",
    # ... more examples
}
```

### Modify Styling

Edit `custom_css` in `app.py`:
```python
custom_css = """
.gradio-container {
    background-color: #f0f0f0;
}
/* ... more CSS */
"""
```

### Enable Public Sharing

Edit `app.py`:
```python
app.launch(
    share=True  # Creates public URL
)
```

**Warning:** Only share if you want public access!

---

## 📊 Performance Notes

### Compilation Time
- Lexical: < 0.1s
- Parsing: < 0.1s
- Semantic: < 0.1s
- TAC: < 0.1s
- C Generation: < 0.1s
- ARM Assembly: < 0.1s
- GCC (exe): 1-3s

**Total:** 3-5 seconds for full compilation to .exe

### Execution Time
- Startup: < 1s
- Execution: Program dependent
- Timeout: 10 seconds max

### Browser Performance
- Interface loads instantly
- Editor responsive on large files
- Output displays quickly
- Works on all modern browsers

---

## 🔒 Security

### Safe Operations
- Code runs in isolated subprocess
- 10-second execution timeout
- Temporary files auto-cleaned
- No network access from code
- No file system access (except temp)

### Limitations
- Cannot read/write files
- Cannot access network
- Cannot run system commands
- Single-file programs only
- Windows .exe only (currently)

---

## 📚 Additional Resources

### Documentation
- **interface/README.md** - Detailed interface guide
- **COMPLETE_GUIDE.md** - Compiler guide (project root)
- **docs/tutorials/** - Step-by-step tutorials

### Examples
- **interface/app.py** - All example programs in code
- **examples/** - Example .minipar files (project root)

### Support
- Check Help tab in interface
- Review troubleshooting section
- Read compiler documentation
- Test with example programs

---

## ✅ Quick Checklist

Before starting:
- [ ] Python 3.7+ installed
- [ ] Gradio installed
- [ ] In correct directory (`interface/`)
- [ ] GCC installed (optional, for .exe)
- [ ] Test setup passed (`python test_setup.py`)

After starting:
- [ ] Interface opens in browser
- [ ] Can load examples
- [ ] Compilation works
- [ ] Execution works
- [ ] Download works (if GCC available)

---

## 🎉 Success!

If you've followed this guide, you should have:

✅ Working web interface
✅ All features functional
✅ Examples loading correctly
✅ Compilation producing output
✅ Programs executing successfully

**Enjoy coding with Minipar!** 🚀

---

## 📞 Getting Help

1. **Read Help tab** in interface
2. **Check troubleshooting** section above
3. **Review examples** in dropdown
4. **Test setup** with `python test_setup.py`
5. **Read documentation** in project root

---

**Version:** 2.0
**Last Updated:** 2026-06-14
**Status:** ✅ Production Ready
**Framework:** Gradio (tested on 6.x)
**Platform:** Cross-platform (Windows, Linux, macOS)
