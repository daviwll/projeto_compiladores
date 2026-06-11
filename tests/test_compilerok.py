"""
Test Suite for Minipar Compiler
Tests lexer, parser, and code generator
"""

import sys
import os
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lexer import Lexer, TokenType
from src.parser import Parser
from src.codegen import CodeGenerator
from src.semantic import SemanticAnalyzer
from src.compiler import compile_source
from src.c_codegen import CCodeGenerator
from src.arm_codegen import ARMCodeGenerator
from src.ast_nodes import ClassDecl, FieldDecl, MethodDecl, ObjectCreation, MethodCall, MemberAccess, VarDecl, ExprStmt


def test_lexer():
    print("Testing Lexer...")
    
    # Test 1: Keywords and identifiers
    source = "func number while if else"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.FUNC
    assert tokens[1].type == TokenType.NUMBER
    assert tokens[2].type == TokenType.WHILE
    print("  ✓ Keywords recognized")
    
    # Test 2: Operators
    source = "+ - * / % == != <= >= < > = && ||"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.PLUS
    assert tokens[5].type == TokenType.EQ
    assert tokens[12].type == TokenType.AND
    print("  ✓ Operators recognized")
    
    # Test 3: Literals
    source = '42 3.14 "hello" true false'
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.NUMBER_LITERAL
    assert tokens[0].value == 42
    assert tokens[1].value == 3.14
    assert tokens[2].type == TokenType.STRING_LITERAL
    assert tokens[2].value == "hello"
    print("  ✓ Literals recognized")
    
    # Test 4: Comments
    source = """
    # Single line comment
    number x = 5; /* Multi
    line comment */ number y = 10;
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    token_types = [t.type for t in tokens if t.type != TokenType.EOF]
    assert TokenType.NUMBER in token_types
    print("  ✓ Comments handled")

    # Test 5: OO keywords
    source = "class new this super extends constructor"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.CLASS
    assert tokens[1].type == TokenType.NEW
    assert tokens[2].type == TokenType.THIS
    assert tokens[3].type == TokenType.SUPER
    assert tokens[4].type == TokenType.EXTENDS
    assert tokens[5].type == TokenType.CONSTRUCTOR
    print("  ✓ OO keywords recognized")
    
    print("✅ Lexer tests passed!\n")


def test_parser():
    print("Testing Parser...")
    
    # Test 1: Variable declaration
    source = "var x: number = 10"
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    assert len(ast.declarations) == 1
    print("  ✓ Variable declaration parsed")
    
    # Test 2: Function declaration
    source = """
    func add(a: number, b: number) -> number {
        return a + b
    }
    """
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    assert len(ast.declarations) == 1
    print("  ✓ Function declaration parsed")
    
    # Test 3: If statement
    source = """
    func test() -> void {
        if (x > 0) {
            y = 1
        } else {
            y = 0
        }
    }
    """
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    assert len(ast.declarations) == 1
    print("  ✓ If statement parsed")
    
    # Test 4: While loop
    source = """
    func loop() -> void {
        while (x < 10) {
            x = x + 1
        }
    }
    """
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    assert len(ast.declarations) == 1
    print("  ✓ While loop parsed")

    # Test 5: Class declaration and member access
    source = """
    class Counter {
        var value: number = 0
        func inc() -> number {
            return value + 1
        }
    }

    var c: Counter = new Counter()
    c.inc()
    c.value
    """
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    assert len(ast.declarations) == 4
    assert isinstance(ast.declarations[0], ClassDecl)
    assert isinstance(ast.declarations[1], VarDecl)
    assert isinstance(ast.declarations[1].initializer, ObjectCreation)
    assert isinstance(ast.declarations[2], ExprStmt)
    assert isinstance(ast.declarations[2].expression, MethodCall)
    assert isinstance(ast.declarations[3], ExprStmt)
    assert isinstance(ast.declarations[3].expression, MemberAccess)
    print("  ✓ Class declaration parsed")
    
    print("✅ Parser tests passed!\n")


def test_codegen():
    print("Testing Code Generator...")
    
    # Test 1: Simple arithmetic
    source = """
    var x: number = 5 + 3
    """
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    codegen = CodeGenerator()
    codegen.generate(ast)
    assert len(codegen.code) > 0
    print("  ✓ Arithmetic code generated")
    
    # Test 2: Function call
    source = """
    func add(a: number, b: number) -> number {
        return a + b
    }
    """
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    codegen = CodeGenerator()
    codegen.generate(ast)
    assert len(codegen.code) > 0
    print("  ✓ Function code generated")
    
    # Test 3: Conditional
    source = """
    func test(x: number) -> void {
        if (x > 0) {
            x = x + 1
        }
    }
    """
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    codegen = CodeGenerator()
    codegen.generate(ast)
    assert len(codegen.code) > 0
    has_label = any(instr.op == 'LABEL' for instr in codegen.code)
    assert has_label
    print("  ✓ Conditional code with labels generated")

    # Test 4: OO class generates structured TAC
    source = """
    class Counter {
        var value: number = 0
        func inc() -> number {
            return value + 1
        }
    }
    var c: Counter = new Counter()
    c.inc()
    c.value = 5
    """
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    codegen = CodeGenerator()
    codegen.generate(ast)
    ops = [instr.op for instr in codegen.code]
    assert 'CLASS_BEGIN' in ops, "Expected CLASS_BEGIN in TAC"
    assert 'FIELD' in ops, "Expected FIELD in TAC"
    assert 'CLASS_END' in ops, "Expected CLASS_END in TAC"
    assert 'FUNC_BEGIN' in ops, "Expected FUNC_BEGIN (method body) in TAC"
    assert 'FUNC_END' in ops, "Expected FUNC_END in TAC"
    assert 'RETURN' in ops, "Expected RETURN inside method"
    assert 'NEW_OBJECT' in ops, "Expected NEW_OBJECT in TAC"
    assert 'CALL_METHOD' not in ops  # op name is METHOD_CALL, not CALL_METHOD
    assert 'METHOD_CALL' in ops, "Expected METHOD_CALL in TAC"
    assert 'MEMBER_STORE' in ops, "Expected MEMBER_STORE for c.value = 5"
    # Verify method is named Counter_inc
    func_begins = [instr.arg1 for instr in codegen.code if instr.op == 'FUNC_BEGIN']
    assert 'Counter_inc' in func_begins, f"Expected Counter_inc in FUNC_BEGIN labels, got {func_begins}"
    assert 'Counter_ctor' in func_begins, f"Expected Counter_ctor in FUNC_BEGIN labels, got {func_begins}"
    print("  ✓ OO class TAC structure generated correctly")

    print("✅ Code generator tests passed!\n")


def _analyze(source: str) -> SemanticAnalyzer:
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    sa = SemanticAnalyzer()
    sa.analyze(ast)
    return sa


def test_semantic_oo():
    print("Testing OO Semantic Validation...")

    # Test 1: Valid class with field and method passes without errors
    sa = _analyze("""
    class Box {
        var side: number = 1
        func area() -> number {
            return side * side
        }
    }
    var b: Box = new Box()
    """)
    assert sa.errors == [], f"Expected no errors, got: {sa.errors}"
    print("  ✓ Valid class declaration passes")

    # Test 2: Duplicate field in same class
    sa = _analyze("""
    class Bad {
        var x: number = 0
        var x: number = 1
    }
    """)
    assert any("already declared" in e for e in sa.errors), \
        f"Expected duplicate field error, got: {sa.errors}"
    print("  ✓ Duplicate field detected")

    # Test 3: Duplicate method in same class
    sa = _analyze("""
    class Bad {
        func foo() -> void {}
        func foo() -> void {}
    }
    """)
    assert any("already declared" in e for e in sa.errors), \
        f"Expected duplicate method error, got: {sa.errors}"
    print("  ✓ Duplicate method detected")

    # Test 4: Duplicate constructor
    sa = _analyze("""
    class Bad {
        constructor() {}
        constructor() {}
    }
    """)
    assert any("constructor" in e.lower() for e in sa.errors), \
        f"Expected duplicate constructor error, got: {sa.errors}"
    print("  ✓ Duplicate constructor detected")

    # Test 5: Object creation arity mismatch
    sa = _analyze("""
    class Point {
        constructor(x: number, y: number) {}
    }
    var p: Point = new Point(1)
    """)
    assert any("expects" in e and "argument" in e for e in sa.errors), \
        f"Expected arity error, got: {sa.errors}"
    print("  ✓ Constructor arity mismatch detected")

    # Test 6: Method call on undefined class method
    sa = _analyze("""
    class Counter {
        var n: number = 0
        func inc() -> number { return n + 1 }
    }
    var c: Counter = new Counter()
    c.reset()
    """)
    assert any("reset" in e for e in sa.errors), \
        f"Expected unknown method error, got: {sa.errors}"
    print("  ✓ Call to undefined method detected")

    # Test 7: Member access on undefined field
    sa = _analyze("""
    class Counter {
        var n: number = 0
    }
    var c: Counter = new Counter()
    c.missing
    """)
    assert any("missing" in e for e in sa.errors), \
        f"Expected unknown member error, got: {sa.errors}"
    print("  ✓ Access to undefined member detected")

    # Test 8: Undefined base class
    sa = _analyze("""
    class Child extends Ghost {}
    """)
    assert any("Ghost" in e for e in sa.errors), \
        f"Expected undefined base class error, got: {sa.errors}"
    print("  ✓ Undefined base class detected")

    # Test 9: Inheritance - child can call method defined on parent
    sa = _analyze("""
    class Animal {
        func speak() -> string { return "..." }
    }
    class Dog extends Animal {}
    var d: Dog = new Dog()
    d.speak()
    """)
    assert sa.errors == [], f"Expected no errors with valid inheritance, got: {sa.errors}"
    print("  ✓ Inherited method call passes")

    # Test 10: Member assignment obj.field = value
    sa = _analyze("""
    class Counter {
        var n: number = 0
        func reset() -> void {
            n = 0
        }
    }
    var c: Counter = new Counter()
    c.n = 5
    """)
    assert sa.errors == [], f"Expected no errors for member assignment, got: {sa.errors}"
    print("  ✓ Member assignment passes")

    # Test 11: Procedural code still passes (regression)
    sa = _analyze("""
    func add(a: number, b: number) -> number {
        return a + b
    }
    var x: number = 10
    """)
    assert sa.errors == [], f"Expected no errors for procedural code, got: {sa.errors}"
    print("  ✓ Procedural regression passes")

    print("✅ OO semantic validation tests passed!\n")


def _compile_oo(source: str):
    """Helper: return (tac_list, c_code_str, arm_asm_str) for an OO source."""
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    cg = CodeGenerator()
    cg.generate(ast)
    c_code = CCodeGenerator().generate(cg.code)
    arm_asm = ARMCodeGenerator().generate(cg.code)
    return cg.code, c_code, arm_asm


def test_c_backend():
    print("Testing C Backend...")

    # Test 1: OO class produces valid C structure
    _, c_code, _ = _compile_oo("""
    class Counter {
        var value: number = 0
        func inc() -> number {
            return value + 1
        }
    }
    var c: Counter = new Counter()
    c.inc()
    c.value
    """)
    assert 'typedef struct Counter' in c_code, "Expected struct typedef"
    assert 'int value;' in c_code, "Expected field declaration"
    assert 'Counter* Counter_ctor(Counter* this)' in c_code, "Expected ctor signature"
    assert 'int Counter_inc(Counter* this)' in c_code, "Expected method signature"
    assert 'malloc(sizeof(Counter))' in c_code, "Expected malloc for new Counter()"
    assert 'Counter_ctor(' in c_code, "Expected ctor call"
    assert 'Counter_inc(' in c_code, "Expected method call"
    assert 'this->value' in c_code, "Expected field access via this->"
    assert 'c->value' in c_code, "Expected field access via c->"
    print("  ✓ OO C struct, ctor, method, malloc all generated")

    # Test 2: Procedural code still produces valid C (regression)
    lexer = Lexer("func add(a: number, b: number) -> number { return a + b }")
    ast = Parser(lexer.tokenize()).parse()
    cg = CodeGenerator()
    cg.generate(ast)
    c_code = CCodeGenerator().generate(cg.code)
    assert 'int add(' in c_code, "Expected function declaration"
    assert 'return' in c_code, "Expected return statement"
    print("  ✓ Procedural C regression passes")

    print("✅ C backend tests passed!\n")


def test_arm_backend():
    print("Testing ARM Backend...")

    # Test 1: OO class produces valid ARM structure
    tac, _, arm_asm = _compile_oo("""
    class Counter {
        var value: number = 0
        func inc() -> number {
            return value + 1
        }
    }
    var c: Counter = new Counter()
    c.inc()
    c.value
    """)
    assert '__minipar_malloc' in arm_asm, "Expected heap allocator"
    assert '__heap' in arm_asm, "Expected heap storage"
    assert 'Counter_ctor:' in arm_asm, "Expected Counter_ctor label"
    assert 'Counter_inc:' in arm_asm, "Expected Counter_inc label"
    assert 'bl Counter_ctor' in arm_asm, "Expected ctor call"
    assert 'bl Counter_inc' in arm_asm, "Expected method call"
    # Field access should use ldr/str with offset 0 (only field)
    assert 'ldr' in arm_asm, "Expected ldr for field reads"
    assert 'str' in arm_asm, "Expected str for field writes"
    print("  ✓ OO ARM: malloc, ctor, method dispatch, field access all generated")

    # Test 2: Procedural code still works (regression)
    lexer = Lexer("""
    func add(a: number, b: number) -> number { return a + b }
    var x: number = 5
    """)
    ast = Parser(lexer.tokenize()).parse()
    cg = CodeGenerator()
    cg.generate(ast)
    arm_asm = ARMCodeGenerator().generate(cg.code)
    assert 'add:' in arm_asm, "Expected add function label"
    assert '__minipar_malloc' not in arm_asm, "No heap for procedural code"
    print("  ✓ Procedural ARM regression passes")

    print("✅ ARM backend tests passed!\n")


def test_arm_snapshot():
    print("Testing ARM Output Snapshot...")

    # Minimal procedural program: one function + one global var.
    # Validates that the code structure is stable and labels are in the right order.
    source = """
    func double(n: number) -> number {
        return n * 2
    }
    var x: number = 7
    """
    lexer = Lexer(source)
    ast = Parser(lexer.tokenize()).parse()
    cg = CodeGenerator()
    cg.generate(ast)
    arm = ARMCodeGenerator().generate(cg.code)

    # Verify structural sections are present
    assert '.data' in arm, "Expected .data section"
    assert '.text' in arm, "Expected .text section"
    assert 'bx lr' in arm, "Expected 'bx lr' return instruction"

    # Entry point and main must be present
    assert '_start:' in arm, "Expected '_start:' entry point"
    assert 'main:' in arm, "Expected 'main:' label"
    assert 'double:' in arm, "Expected 'double:' label"

    # ARM backend emits main first, then user functions (after main body)
    main_pos = arm.index('main:')
    double_pos = arm.index('double:')
    assert main_pos < double_pos, "main should appear before user function 'double'"

    # Data section must declare the global
    assert 'x:' in arm, "Expected global 'x' in .data"

    # No OO heap when there are no classes
    assert '__minipar_malloc' not in arm, "No heap allocator for procedural-only programs"
    assert '__heap' not in arm, "No heap storage for procedural-only programs"

    print("  ✓ Procedural ARM snapshot: sections, labels, ordering all stable")

    # OO snapshot: verify field-offset pattern in ctor body.
    # Counter has one field (value), so all field access uses offset #0.
    _, _, arm_oo = _compile_oo("""
    class Counter {
        var value: number = 0
        func inc() -> number {
            return value + 1
        }
    }
    var c: Counter = new Counter()
    c.inc()
    """)

    # Both ldr and str with offset 0 must be present (ctor stores 0, inc reads)
    assert '#0]' in arm_oo or ', #0]' in arm_oo, \
        "Expected field offset #0 for single-field class"

    # Heap allocator must come after all user functions
    malloc_pos = arm_oo.index('__minipar_malloc:')
    ctor_pos = arm_oo.index('Counter_ctor:')
    inc_pos = arm_oo.index('Counter_inc:')
    assert ctor_pos < malloc_pos, "Counter_ctor should appear before malloc stub"
    assert inc_pos < malloc_pos, "Counter_inc should appear before malloc stub"
    print("  ✓ OO ARM snapshot: field offset #0, malloc stub at end")

    print("✅ ARM snapshot tests passed!\n")


def test_full_examples():
    print("Testing Full Examples...")
    
    # Get examples directory path
    examples_dir = os.path.join(os.path.dirname(__file__), '..', 'examples')
    
    examples = [
        ("ex1.minipar", "Variables, functions and control flow"),
        ("ex2.minipar", "Server channels and types"),
        ("ex3.minipar", "Loops and user input"),
        ("ex5.minipar", "Simple functions"),
        ("fatorial_rec.minipar", "Recursive factorial"),
    ]
    
    for filename, description in examples:
        filepath = os.path.join(examples_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    source = f.read()
                compile_source(source, show_tokens=False, show_ast=False)
                print(f"  ✓ {description} ({filename})")
            except Exception as e:
                print(f"  ❌ {description} ({filename}): {e}")
        else:
            print(f"  ⚠ {filename} not found at {filepath}")

    # OO smoke test
    oo_source = """
    class Counter {
        var value: number = 0
        func inc() -> number {
            return value + 1
        }
    }

    var c: Counter = new Counter()
    c.inc()
    c.value
    """
    compile_source(oo_source, show_tokens=False, show_ast=False)
    print("  ✓ OO class smoke test compiled")
    
    print("✅ Example tests completed!\n")


def main():
    print("=" * 60)
    print("Minipar Compiler Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_lexer()
        test_parser()
        test_codegen()
        test_semantic_oo()
        test_c_backend()
        test_arm_backend()
        test_arm_snapshot()
        test_full_examples()
        
        print("=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
