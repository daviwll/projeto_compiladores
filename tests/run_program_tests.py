#!/usr/bin/env python3
"""
Test runner for program_test_1 through program_test_9 (todos os programas de
teste da especificação MiniPar 2026.1), mais os testes de aceitação de OO.
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from compiler import compile_file, compile_source
from lexer import Lexer
from parser import Parser
from codegen import CodeGenerator
from c_codegen import CCodeGenerator
from arm_codegen import ARMCodeGenerator
from semantic import SemanticAnalyzer

TESTS_DIR = os.path.dirname(__file__)


def test_program(test_num, description):
    """Compile one of the canonical program test files (1-9)."""
    test_file = f"program_test_{test_num}.minipar"
    test_path = os.path.join(TESTS_DIR, test_file)

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


def _compile_pipeline(source):
    """Return (tac_list, c_code_str, arm_asm_str) for source."""
    lexer = Lexer(source)
    ast = Parser(lexer.tokenize()).parse()
    cg = CodeGenerator()
    cg.generate(ast)
    c_code = CCodeGenerator().generate(cg.code)
    arm_asm = ARMCodeGenerator().generate(cg.code)
    return cg.code, c_code, arm_asm


def test_oo_acceptance():
    """Full pipeline acceptance test for the OO counter fixture."""
    fixture = os.path.join(TESTS_DIR, "oo_counter.minipar")

    print(f"\n{'='*60}")
    print("Testing: oo_counter.minipar (OO acceptance)")
    print(f"{'='*60}")

    if not os.path.exists(fixture):
        print(f"❌ Fixture not found: {fixture}")
        return False

    try:
        with open(fixture, encoding='utf-8') as f:
            source = f.read()

        tac, c_code, arm_asm = _compile_pipeline(source)

        # TAC checks
        ops = [i.op for i in tac]
        assert 'CLASS_BEGIN' in ops, "TAC missing CLASS_BEGIN"
        assert 'FIELD' in ops, "TAC missing FIELD"
        assert 'NEW_OBJECT' in ops, "TAC missing NEW_OBJECT"
        assert 'METHOD_CALL' in ops, "TAC missing METHOD_CALL"
        assert 'MEMBER_ACCESS' in ops, "TAC missing MEMBER_ACCESS (field read in method)"
        assert 'MEMBER_STORE' in ops, "TAC missing MEMBER_STORE (field write)"
        print("  ✓ TAC contains all OO opcodes")

        # C backend checks
        assert 'typedef struct Counter' in c_code, "C missing struct typedef"
        assert 'Counter* Counter_ctor(' in c_code, "C missing ctor signature"
        assert 'malloc(sizeof(Counter))' in c_code, "C missing malloc"
        assert 'this->value' in c_code, "C missing this->field access"
        assert 'c->value' in c_code, "C missing receiver->field access"
        print("  ✓ C backend: struct, ctor, malloc, field access all correct")

        # ARM backend checks
        assert 'Counter_ctor:' in arm_asm, "ARM missing Counter_ctor label"
        assert 'Counter_inc:' in arm_asm, "ARM missing Counter_inc label"
        assert 'Counter_get:' in arm_asm, "ARM missing Counter_get label"
        assert '__minipar_malloc' in arm_asm, "ARM missing heap allocator"
        assert '__heap' in arm_asm, "ARM missing heap storage"
        assert 'bl Counter_ctor' in arm_asm, "ARM missing ctor call"
        assert 'bl Counter_inc' in arm_asm, "ARM missing Counter_inc call"
        assert 'ldr' in arm_asm, "ARM missing ldr for field reads"
        assert 'str' in arm_asm, "ARM missing str for field writes"
        print("  ✓ ARM backend: labels, allocator, ctor, method dispatch, field access all correct")

        print("✅ OO acceptance test passed!")
        return True

    except (AssertionError, Exception) as e:
        print(f"❌ OO acceptance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_oo_semantic_error():
    """Verify that a semantically invalid OO program produces a clear error."""
    print(f"\n{'='*60}")
    print("Testing: OO semantic error reporting")
    print(f"{'='*60}")

    cases = [
        (
            "call to undefined method",
            """
            class Counter { var n: number = 0 }
            var c: Counter = new Counter()
            c.missing()
            """,
            "missing",
        ),
        (
            "duplicate field",
            """
            class Bad { var x: number = 0  var x: number = 1 }
            """,
            "already declared",
        ),
        (
            "undefined base class",
            """
            class Child extends Ghost {}
            """,
            "Ghost",
        ),
    ]

    all_ok = True
    for name, source, expected_fragment in cases:
        try:
            lexer = Lexer(source)
            ast = Parser(lexer.tokenize()).parse()
            sa = SemanticAnalyzer()
            sa.analyze(ast)
            if sa.errors and any(expected_fragment in e for e in sa.errors):
                print(f"  ✓ '{name}': error reported correctly")
            else:
                print(f"  ❌ '{name}': expected error containing '{expected_fragment}', got: {sa.errors}")
                all_ok = False
        except Exception as e:
            print(f"  ❌ '{name}': unexpected exception: {e}")
            all_ok = False

    if all_ok:
        print("✅ OO semantic error tests passed!")
    return all_ok


def main():
    print("="*60)
    print("Minipar Program Tests")
    print("="*60)

    procedural_tests = [
        (1, "Cliente-Servidor Calculadora com c_channel"),
        (2, "Execução Paralela: Fatorial e Fibonacci (PAR)"),
        (3, "Neurônio (perceptron) com Classes e Objetos"),
        (4, "Rede Neural XOR (feedforward + backpropagation)"),
        (5, "Sistema de Recomendação com Rede Neural (Classes)"),
        (6, "Quicksort com Classes e Objetos"),
        (7, "Fatorial Iterativo (gera Assembly ARMv7)"),
        (8, "Série de Fibonacci (gera Assembly ARMv7)"),
        (9, "Quicksort Iterativo (atribuição indexada, gera ARMv7)"),
    ]

    results = []
    for test_num, description in procedural_tests:
        result = test_program(test_num, description)
        results.append((f"Program Test {test_num}", result))

    results.append(("OO Acceptance (oo_counter.minipar)", test_oo_acceptance()))
    results.append(("OO Semantic Error Reporting", test_oo_semantic_error()))

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")

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
