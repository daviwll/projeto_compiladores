"""
Quick test script for the compiler API
Tests the fixed C code and Assembly generation
"""

import sys
from pathlib import Path

# Add paths
interface_dir = Path(__file__).parent
project_root = interface_dir.parent
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(interface_dir))

from compiler_api import CompilerAPI

# Test code
test_program = """
var x: number = 10

func greet() -> void {
    print("Hello from Minipar!")
    print("x =", x)
}

greet()
"""

print("=" * 60)
print("Testing Compiler API")
print("=" * 60)
print()

api = CompilerAPI()

print("[Test 1] Compile with TAC...")
result = api.compile_code(test_program, show_tac=True)
print(f"Success: {result['success']}")
print(f"TAC length: {len(result['tac'])} characters")
if result['tac']:
    print("TAC Preview:")
    print(result['tac'][:200] + "..." if len(result['tac']) > 200 else result['tac'])
print()

print("[Test 2] Generate C Code...")
result = api.compile_code(test_program, generate_c=True)
print(f"Success: {result['success']}")
print(f"C Code length: {len(result['c_code'])} characters")
if result['c_code']:
    print("C Code Preview:")
    lines = result['c_code'].split('\n')
    print('\n'.join(lines[:15]))
    print("...")
print()

print("[Test 3] Generate Assembly...")
result = api.compile_code(test_program, generate_asm=True)
print(f"Success: {result['success']}")
print(f"Assembly length: {len(result['assembly'])} characters")
if result['assembly']:
    print("Assembly Preview:")
    lines = result['assembly'].split('\n')
    print('\n'.join(lines[:15]))
    print("...")
print()

print("[Test 4] Generate Executable...")
result = api.compile_code(test_program, generate_exe=True)
print(f"Success: {result['success']}")
print(f"Exe generated: {result['exe_file'] is not None}")
if result['exe_file']:
    print(f"Exe path: {result['exe_file']['path']}")
    import os
    print(f"Exe exists: {os.path.exists(result['exe_file']['path'])}")
print()

print("=" * 60)
print("API Test Complete!")
print("=" * 60)
