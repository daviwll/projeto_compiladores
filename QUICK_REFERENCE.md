# Minipar Quick Reference

⚡ **Fast access to common commands and information**

## 🚀 Quick Start (1 minute)

```bash
# Compile and run a program (RECOMMENDED)
py compile.py examples\ex5.minipar --exe
.\output.exe

# OR: Run directly with runtime (Advanced)
py src\runner.py test_runner_simple.minipar

# OR: Run server/client example (2 terminals)
py src\runner.py calc_server.minipar    # Terminal 1
py src\runner.py calc_client.minipar    # Terminal 2
```

## 📂 Project Layout

```
/
├── README.md                # Main documentation
├── PROJECT_INDEX.md         # Complete navigation
├── calc_server.minipar      # Server example
├── calc_client.minipar      # Client example
├── src/                     # Compiler source
├── examples/                # Sample programs
├── tests/                   # Test suite
├── docs/                    # All documentation
│   ├── tutorials/          # Guides
│   ├── technical/          # Deep dive
│   └── archive/            # History
├── bin/                     # Utility scripts
└── generated/               # Compiled output
```

## 💻 Common Commands

### Compile Programs (MAIN FEATURE)
```bash
py compile.py <file>                      # To TAC (intermediate code)
py compile.py <file> --exe                # To executable ⭐ MOST USED
py compile.py <file> --exe --output name  # Custom output name
py compile.py <file> --generate-c         # Generate C code
py compile.py <file> --tokens             # Show tokens
py compile.py <file> --ast                # Show AST
py compile.py <file> --tokens --ast --exe # Combine flags
```

### Execute Programs (Runtime - Advanced)
```bash
py src\runner.py <file>              # Run directly (channels work)
py src\runner.py <file> --debug      # Debug mode
```

### Run Tests
```bash
py run_tests.py                      # All tests
py tests\run_program_tests.py       # Program tests
```

### Wrappers (Windows)
```bash
bin\run <file>                       # Execute
bin\minipar <file>                   # Compile
bin\test                             # Test
```

## 📖 Documentation Quick Links

| What You Need | Where to Find It |
|---------------|------------------|
| **Complete guide** | **[COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)** ⭐ NEW |
| Getting started | [README.md](README.md) |
| All compiler flags | [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) |
| Verification report | [VERIFICATION_REPORT.md](VERIFICATION_REPORT.md) |
| 5-min channel tutorial | [docs/tutorials/QUICK_START_CHANNELS.md](docs/tutorials/QUICK_START_CHANNELS.md) |
| Full channel tutorial | [docs/tutorials/CHANNEL_TUTORIAL.md](docs/tutorials/CHANNEL_TUTORIAL.md) |
| General tutorial | [docs/tutorials/TUTORIAL.md](docs/tutorials/TUTORIAL.md) |
| Complete index | [PROJECT_INDEX.md](PROJECT_INDEX.md) |
| Technical details | [docs/technical/CHANNELS_INDEX.md](docs/technical/CHANNELS_INDEX.md) |
| Runner docs | [src/RUNNER_README.md](src/RUNNER_README.md) |
| Examples | [examples/README.md](examples/README.md) |

## 🎯 Language Syntax

### Variables
```minipar
var x: number = 10
var name: string = "Alice"
var flag: bool = true
```

### Functions  
```minipar
func add(a: number, b: number) -> number {
    return a + b
}
```

### Control Flow
```minipar
if (x > 0) { print("positive") }
else { print("negative") }

while (i < 10) {
    i = i + 1
    if (i == 5) { break }
}
```

### Classes and Objects (OO)
```minipar
# Class with field, constructor, and methods
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

# Object creation
var c: Counter = new Counter(0)

# Method call
c.inc()

# Field read / write
c.get()
c.value = 10

# Inheritance
class Animal {
    func speak() -> string { return "..." }
}
class Dog extends Animal {}   # inherits speak()

var d: Dog = new Dog()
d.speak()
```

### OO Keywords
| Keyword | Purpose |
|---------|---------|
| `class` | Declare a class |
| `constructor` | Class initializer |
| `new` | Create an object instance |
| `this` | Reference to current object |
| `super` | Reference to parent class |
| `extends` | Inheritance |

### Channels (Networking)
```minipar
# Server
s_channel server {handler, "Description", "localhost", 5000}

# Client  
c_channel client {"localhost", 5000}
client.send(data)
client.close()
```

## 🛠️ Built-in Functions

- `print(...)` - Output to console
- `input(prompt)` - Read input
- `to_string(x)` - Convert to string
- `to_number(x)` - Convert to number  
- `to_bool(x)` - Convert to boolean

## 📝 Example Locations

| Example | File | Description |
|---------|------|-------------|
| Hello World | `examples/ex1.minipar` | Basic syntax |
| Server | `examples/ex2.minipar` | Channels |
| Loops | `examples/ex3.minipar` | Control flow |
| Calculator | `calc_server.minipar` | Full server |
| Calculator Client | `calc_client.minipar` | Full client |

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Tests fail | Run from project root |
| Can't find module | Use `py` not `python` |
| Port in use | Change port number |
| Connection refused | Start server first |

## ✅ Verify Installation

```bash
# Test compilation (ESSENTIAL)
py compile.py examples\ex5.minipar --exe
.\output.exe

# Test all features
py run_tests.py

# Test runtime (optional)
py src\runner.py test_runner_simple.minipar
```

## 📊 Project Stats

- **Source**: 12 Python modules (~3,600 lines)
- **Examples**: 17 Minipar programs  
- **Tests**: 10 test files
- **Docs**: 27 files (~200 pages)

---

**Need more details?** See [PROJECT_INDEX.md](PROJECT_INDEX.md) for complete navigation!
