# Minipar Compiler - Dependency Setup & Configuration Guide

## Table of Contents

1. [Overview](#overview)
2. [Requirements](#requirements)
3. [What Was Done](#what-was-done)
4. [Installation Methods](#installation-methods)
5. [Dependencies Breakdown](#dependencies-breakdown)
6. [Configuration Details](#configuration-details)
7. [Verification](#verification)
8. [Testing Results](#testing-results)
9. [Troubleshooting](#troubleshooting)
10. [Development Workflow](#development-workflow)
11. [Comparison: Before vs After](#comparison-before-vs-after)
12. [Additional Resources](#additional-resources)

---

## Overview

This document explains the complete dependency setup and configuration for the Minipar Compiler project, including both the core compiler and the optional web interface.

### Project Structure

The Minipar Compiler is designed with minimal dependencies:

- **Core Compiler**: Uses only Python standard library (no external dependencies)
- **Web Interface**: Requires Gradio for the interactive web UI

### Design Philosophy

1. **Zero Core Dependencies**: The compiler itself uses only Python stdlib
2. **Optional Web Interface**: Gradio is only needed for the web UI
3. **UV as Primary Tool**: Leverages UV's speed and reliability
4. **Backward Compatibility**: Still works with pip if needed

---

## Requirements

- **Python**: 3.8 or higher (required for Gradio compatibility)
- **uv**: Python package manager (recommended) - [Install uv](https://docs.astral.sh/uv/)

---

## What Was Done

### 1. Updated Python Version Requirement

- **Changed**: `requires-python = ">=3.7"` → `requires-python = ">=3.8"`
- **Reason**: Gradio requires Python 3.8 or higher
- **File**: `pyproject.toml`

### 2. Added Gradio to Dependencies

Added Gradio to both optional and dev dependencies in `pyproject.toml`:

```toml
[project.optional-dependencies]
web = [
    "gradio>=4.0.0",
]

[tool.uv]
dev-dependencies = [
    "gradio>=4.0.0",
]
```

### 3. Updated Python Version Classifiers

Removed Python 3.7 from supported versions list in `pyproject.toml`

### 4. Enhanced start.bat Script

Improved the Windows launcher script (`interface/start.bat`) to:
- Check for UV installation
- Automatically run `uv sync` if venv or dependencies are missing
- Use the virtual environment Python explicitly
- Better error messages and status reporting

### 5. Created Documentation and Tools

- **DEPENDENCY_SETUP.md**: Comprehensive dependency installation guide (this file)
- **verify_setup.py**: Automated verification script for checking setup
- **BUG_FIX_REPORT.md**: Documentation of the sys.exit() bug fix

### 6. Updated Lock File

- Generated/updated `uv.lock` with all dependencies
- Total: ~101 packages including transitive dependencies

---

## Installation Methods

### Method 1: Using UV (Recommended)

UV is a fast Python package manager that handles virtual environments and dependencies automatically.

#### Step 1: Install UV (if not already installed)

**Windows:**
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or using pip:
```bash
pip install uv
```

#### Step 2: Sync Dependencies

From the project root directory:

```bash
uv sync
```

This command will:
- Create a virtual environment in `.venv/`
- Install the project in editable mode
- Install all development dependencies (including Gradio)
- Generate/update the `uv.lock` file

#### Step 3: Run the Web Interface

**Windows:**
```bash
cd interface
start.bat
```

**Linux/macOS:**
```bash
cd interface
../venv/bin/python app.py
```

### Method 2: Using pip

If you prefer using pip instead of uv:

#### Step 1: Create Virtual Environment

```bash
python -m venv .venv
```

#### Step 2: Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

#### Step 3: Install Dependencies

For web interface support:
```bash
pip install gradio>=4.0.0
```

#### Step 4: Install Project

```bash
pip install -e .
```

---

## Dependencies Breakdown

### Core Compiler (No External Dependencies)

The core compiler components use only Python standard library:
- `src/lexer.py` - Lexical analysis
- `src/parser.py` - Syntax analysis
- `src/semantic.py` - Semantic analysis
- `src/codegen.py` - Three-address code generation
- `src/c_codegen.py` - C code generation
- `src/arm_codegen.py` - ARM assembly generation
- `src/backend.py` - Executable compilation

### Web Interface Dependencies

The web interface requires:
- **gradio >= 4.0.0**: Interactive web UI framework

### What Gets Installed

When running `uv sync`, the following are installed:

#### Direct Dependencies
- **gradio** (5.49.1 or compatible version)

#### Transitive Dependencies (installed automatically by Gradio)
- fastapi - Web framework
- uvicorn - ASGI server
- starlette - Web toolkit
- pydantic - Data validation
- aiofiles - Async file operations
- httpx - HTTP client
- jinja2 - Template engine
- And ~90 other packages

**Total**: ~101 packages in the lock file

---

## Configuration Details

### pyproject.toml Structure

```toml
[project]
name = "minipar-compiler"
version = "1.0.0"
requires-python = ">=3.8"
dependencies = []  # Core compiler has no dependencies

[project.optional-dependencies]
# Development dependencies
dev = []

# Web interface dependencies
web = [
    "gradio>=4.0.0",
]

[tool.uv]
dev-dependencies = [
    "gradio>=4.0.0",
]
```

### Key Configuration Points

1. **requires-python = ">=3.8"**: Gradio requires Python 3.8+
2. **dependencies = []**: Core compiler has no dependencies
3. **web** optional dependencies: For users who want the web interface
4. **dev-dependencies**: Includes Gradio for development/testing

### Lock File Status

- **File**: `uv.lock`
- **Packages**: 101 total
- **Status**: ✅ Up to date
- **Python Range**: >=3.8
- **Purpose**: Ensures reproducible builds

---

## Verification

### Automated Verification

Run the verification script to check everything is set up correctly:

```bash
python verify_setup.py
```

Expected output:
```
✅ PASS - Python Version
✅ PASS - Dependencies
✅ PASS - Compiler Modules
✅ PASS - Web Interface
```

### Manual Verification

#### 1. Check Python Version
```bash
python --version
```
Should show 3.8 or higher.

#### 2. Check Gradio Installation
```bash
python -c "import gradio; print(f'Gradio {gradio.__version__}')"
```

#### 3. Test Core Compiler
```bash
python src/compiler.py examples/ex1.minipar --tokens --ast
```

#### 4. Test Web Interface
```bash
cd interface
python app.py
```
Then open http://localhost:7860 in your browser.

---

## Testing Results

All tests passed successfully:

✅ **Python Version Check**: 3.10.18 (compatible with >=3.8)  
✅ **Gradio Installation**: Version 5.49.1 installed  
✅ **Compiler Modules**: All 8 modules importable  
✅ **Web Interface**: Starts successfully on http://localhost:7860  
✅ **Existing Tests**: All project tests still pass  
✅ **Bug Fix**: sys.exit() error handling still working correctly  

---

## Troubleshooting

### Issue: "No module named 'gradio'"

**Solution:**
```bash
uv sync
```
Or if using pip:
```bash
pip install gradio>=4.0.0
```

### Issue: "Python version not supported"

Gradio requires Python 3.8+. Upgrade your Python installation:
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **Linux**: `sudo apt update && sudo apt install python3.10` (or newer)
- **macOS**: `brew install python@3.10`

### Issue: UV not found

Install UV:
```bash
pip install uv
```

### Issue: start.bat fails on Windows

Make sure you're running from the `interface` directory and that UV is installed:
```bash
cd interface
where uv
```

If UV is not found, install it:
```bash
pip install uv
```

### Issue: Virtual environment not found

Run from project root:
```bash
uv sync
```

This will create the virtual environment and install all dependencies.

### Issue: Gradio not installed after sync

Try reinstalling:
```bash
uv sync --reinstall
```

### Issue: Web interface won't start

Run the verification script to identify the problem:
```bash
python verify_setup.py
```

---

## Development Workflow

### Adding New Dependencies

If you need to add more dependencies for development:

1. Edit `pyproject.toml`:
```toml
[tool.uv]
dev-dependencies = [
    "gradio>=4.0.0",
    "your-new-package>=1.0.0",
]
```

2. Sync:
```bash
uv sync
```

### Updating Dependencies

To update all dependencies to their latest compatible versions:
```bash
uv sync --upgrade
```

### Locking Dependencies

The `uv.lock` file ensures reproducible builds. Commit this file to version control:
```bash
git add uv.lock
git commit -m "Update dependencies"
```

### CI/CD Integration

For automated testing and deployment:

```yaml
# Example GitHub Actions workflow
- name: Install UV
  run: pip install uv

- name: Sync dependencies
  run: uv sync

- name: Run tests
  run: uv run python run_tests.py
```

### Development Steps

1. Make changes to code
2. Test with existing test suite: `python run_tests.py`
3. Test web interface: `cd interface && python app.py`
4. Commit changes including `uv.lock` if dependencies changed

---

## Comparison: Before vs After

### Before the Configuration Update

- ❌ No dependencies specified in pyproject.toml
- ❌ Manual Gradio installation required
- ❌ Python 3.7 support (incompatible with Gradio)
- ❌ start.bat used system Python inconsistently
- ❌ No automated verification
- ❌ Compiler called sys.exit() crashing web interface

### After the Configuration Update

- ✅ Gradio properly specified in pyproject.toml
- ✅ Automatic installation with `uv sync`
- ✅ Python 3.8+ requirement (Gradio compatible)
- ✅ start.bat uses venv and auto-syncs dependencies
- ✅ Automated verification with verify_setup.py
- ✅ Compiler raises exceptions gracefully for web interface

---

## Advantages of This Setup

### For Users

1. **Simple Setup**: Just `uv sync` and it works
2. **Fast Installation**: UV is significantly faster than pip
3. **Reliable**: Lock file ensures reproducible installations
4. **Clear Separation**: Core compiler vs web interface dependencies
5. **No Confusion**: Clear which dependencies are needed for what

### For Developers

1. **Easy Updates**: `uv sync --upgrade` updates everything
2. **Consistent Environment**: Everyone gets the same versions
3. **CI/CD Ready**: Easy to integrate into automated pipelines
4. **Clear Documentation**: All setup steps are documented
5. **Automated Testing**: verify_setup.py ensures correctness

---

## Quick Reference

### Essential Commands

```bash
# Install UV
pip install uv

# Sync dependencies (first time setup)
uv sync

# Update dependencies
uv sync --upgrade

# Verify setup
python verify_setup.py

# Run compiler (CLI)
python src/compiler.py examples/ex1.minipar

# Start web interface
cd interface && start.bat          # Windows
cd interface && python app.py      # Linux/macOS

# Run tests
python run_tests.py
```

### File Structure

```
projeto_compiladores/
├── pyproject.toml              # Project configuration
├── uv.lock                     # Lock file (101 packages)
├── verify_setup.py             # Verification script
├── src/                        # Core compiler (no deps)
│   ├── lexer.py
│   ├── parser.py
│   ├── semantic.py
│   ├── codegen.py
│   ├── c_codegen.py
│   ├── arm_codegen.py
│   ├── backend.py
│   └── compiler.py
├── interface/                  # Web interface (needs Gradio)
│   ├── app.py
│   ├── compiler_api.py
│   └── start.bat
└── .venv/                      # Virtual environment
```

---

## Summary

The dependency configuration has been successfully refined with proper UV integration. The project now has:

✅ **Clear dependency specification** in pyproject.toml  
✅ **Automated setup** via `uv sync`  
✅ **Proper version constraints** (Python 3.8+, Gradio 4.0+)  
✅ **Enhanced tooling** (improved start.bat, verification script)  
✅ **Comprehensive documentation** for users and developers  
✅ **Core compiler**: Zero external dependencies  
✅ **Web interface**: Gradio only  
✅ **Package manager**: UV (recommended) or pip  
✅ **Easy setup**: `uv sync` and you're ready!  

Everything is tested and working correctly! 🎉

---

## Additional Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [Gradio Documentation](https://www.gradio.app/docs/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Minipar Compiler README](README.md)
- [Web Interface Guide](WEB_INTERFACE_README.md)
- [Bug Fix Report](BUG_FIX_REPORT.md)

---

## Support

For issues related to:
- **Compiler**: Check the main README.md
- **Dependencies**: This document
- **Web Interface**: See WEB_INTERFACE_README.md
- **Bug Reports**: Check BUG_FIX_REPORT.md for known issues

---

**Last Updated**: December 2024  
**Status**: ✅ Complete and Verified
