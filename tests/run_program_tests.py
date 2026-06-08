#!/usr/bin/env python3
"""
Test runner for program_test_1 through program_test_4
Tests the minipar files created from the test specifications
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from compiler import compile_file

def test_program(test_num, description):
    """Test a specific program test file"""
    test_file = f"program_test_{test_num}.minipar"
    test_path = os.path.join(os.path.dirname(__file__), test_file)
    
    print(f"\n{'='*60}")
    print(f"Testing: {test_file}")
    print(f"Description: {description}")
    print(f"{'='*60}")
    
    if not os.path.exists(test_path):
        print(f"❌ File not found: {test_path}")
        return False
    
    try:
        compile_file(test_path, show_tokens=False, show_ast=False)
        print(f"✅ {test_file} compiled successfully!")
        return True
    except Exception as e:
        print(f"❌ {test_file} failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("Minipar Program Tests 1-4")
    print("="*60)
    
    tests = [
        (1, "Cliente-Servidor Calculadora com c_channel"),
        (2, "Execução Paralela: Fatorial e Fibonacci (PAR)"),
        (3, "Fatorial Iterativo"),
        (4, "Série de Fibonacci"),
    ]
    
    results = []
    for test_num, description in tests:
        result = test_program(test_num, description)
        results.append((test_num, result))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_num, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"Program Test {test_num}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("✅ All program tests passed successfully!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
