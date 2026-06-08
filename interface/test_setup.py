"""
Test script to verify the interface setup
Run this to check if everything is configured correctly
"""

import sys
import os
from pathlib import Path

print("=" * 60)
print("Minipar Compiler Interface - Setup Test")
print("=" * 60)
print()

# Check Python version
print("[1/6] Checking Python version...")
version = sys.version_info
print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
if version.major < 3 or (version.major == 3 and version.minor < 7):
    print("❌ ERROR: Python 3.7+ required")
    sys.exit(1)
print()

# Check project structure
print("[2/6] Checking project structure...")
interface_dir = Path(__file__).parent
project_root = interface_dir.parent
src_dir = project_root / 'src'

if not src_dir.exists():
    print(f"❌ ERROR: src directory not found at {src_dir}")
    sys.exit(1)
print(f"✓ Project root: {project_root}")
print(f"✓ Source directory: {src_dir}")
print()

# Check required files
print("[3/6] Checking required files...")
required_files = [
    interface_dir / 'app.py',
    interface_dir / 'compiler_api.py',
    interface_dir / 'requirements.txt',
    src_dir / 'compiler.py',
    src_dir / 'lexer.py',
    src_dir / 'parser.py',
]

all_exist = True
for file_path in required_files:
    if file_path.exists():
        print(f"✓ {file_path.name}")
    else:
        print(f"❌ MISSING: {file_path.name}")
        all_exist = False

if not all_exist:
    print("\n❌ ERROR: Some required files are missing")
    sys.exit(1)
print()

# Check if Gradio is installed
print("[4/6] Checking Gradio installation...")
try:
    import gradio as gr
    print(f"✓ Gradio {gr.__version__} installed")
except ImportError:
    print("❌ Gradio not installed")
    print("\nTo install Gradio, run:")
    print("  pip install gradio")
    print("  OR")
    print("  py -m pip install gradio")
    sys.exit(1)
print()

# Test compiler import
print("[5/6] Testing compiler import...")
sys.path.insert(0, str(src_dir))
try:
    from compiler import compile_source
    print("✓ Compiler module loaded successfully")
except ImportError as e:
    print(f"❌ Failed to import compiler: {e}")
    sys.exit(1)
print()

# Test API import
print("[6/6] Testing API import...")
sys.path.insert(0, str(interface_dir))
try:
    from compiler_api import CompilerAPI
    api = CompilerAPI()
    print("✓ API module loaded successfully")
except ImportError as e:
    print(f"❌ Failed to import API: {e}")
    sys.exit(1)
print()

# Final result
print("=" * 60)
print("✅ ALL CHECKS PASSED!")
print("=" * 60)
print()
print("You can now start the interface:")
print(f"  cd {interface_dir}")
print("  python app.py")
print()
print("The interface will be available at:")
print("  http://localhost:7860")
print()
print("=" * 60)
