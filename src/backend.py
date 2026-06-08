"""
Backend Module - GCC Integration for Minipar Compiler
Handles compilation of generated C code to assembly using GCC
"""

import subprocess
import os
import sys
import platform
from typing import Optional, Tuple
from pathlib import Path


class CompilationError(Exception):
    """Raised when compilation fails"""
    pass


class Backend:
    """
    Backend compiler that uses GCC to compile C code to executable
    """
    
    def __init__(self):
        """Initialize backend"""
        self.gcc_path = self._find_gcc()
        
    def _find_gcc(self) -> str:
        """Find GCC compiler"""
        return "gcc"
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH"""
        try:
            subprocess.run([command, "--version"], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL,
                         check=False)
            return True
        except FileNotFoundError:
            return False
    
    def compile_to_executable(
        self,
        c_file: str,
        output_exe: str,
        optimization: str = "2"
    ) -> Tuple[bool, str]:
        """
        Compile C code to executable
        
        Args:
            c_file: Input C source file
            output_exe: Output executable file
            optimization: GCC optimization level
            
        Returns:
            (success, message) tuple
        """
        if not os.path.exists(c_file):
            return False, f"Input file not found: {c_file}"
        
        # Build GCC command
        cmd = [self.gcc_path, f"-O{optimization}"]
        
        # Add input/output files
        cmd.extend([c_file, "-o", output_exe])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                return True, f"✓ Executable generated: {output_exe}"
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return False, f"GCC compilation failed:\n{error_msg}"
                
        except FileNotFoundError:
            return False, f"GCC compiler not found: {self.gcc_path}"
        except Exception as e:
            return False, f"Compilation error: {str(e)}"
    
    def get_info(self) -> dict:
        """Get backend information"""
        info = {
            "gcc_path": self.gcc_path,
            "gcc_available": self._command_exists(self.gcc_path)
        }
        
        # Get GCC version
        if info["gcc_available"]:
            try:
                result = subprocess.run(
                    [self.gcc_path, "--version"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    first_line = result.stdout.split('\n')[0]
                    info["gcc_version"] = first_line
            except:
                info["gcc_version"] = "Unknown"
        
        return info


def compile_minipar_pipeline(
    source_file: str,
    output_base: Optional[str] = None,
    generate_exe: bool = True,
    keep_c: bool = True,
    optimization: str = "2"
) -> bool:
    """
    Complete compilation pipeline: Minipar → C → Executable
    
    Args:
        source_file: Input .minipar file
        output_base: Base name for output files (without extension)
        generate_exe: Generate executable
        keep_c: Keep intermediate C file
        optimization: GCC optimization level
        
    Returns:
        True if successful, False otherwise
    """
    # Import compiler modules
    try:
        from src.lexer import Lexer
        from src.parser import Parser
        from src.semantic import SemanticAnalyzer
        from src.codegen import CodeGenerator
        from src.c_codegen import CCodeGenerator
    except ImportError:
        from lexer import Lexer
        from parser import Parser
        from semantic import SemanticAnalyzer
        from codegen import CodeGenerator
        from c_codegen import CCodeGenerator
    
    # Determine output file names
    if output_base is None:
        output_base = Path(source_file).stem
    
    c_file = f"{output_base}.c"
    exe_file = f"{output_base}.exe" if platform.system() == "Windows" else output_base
    
    print(f"\n{'='*60}")
    print(f"Compiling: {source_file}")
    print(f"{'='*60}\n")
    
    try:
        # Read source file
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Phase 1: Lexical Analysis
        print("=== Phase 1: Lexical Analysis ===")
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        print(f"✓ Tokenization complete: {len(tokens)} tokens\n")
        
        # Phase 2: Syntax Analysis
        print("=== Phase 2: Syntax Analysis ===")
        parser = Parser(tokens)
        ast = parser.parse()
        # Count declarations
        decl_count = len(ast.declarations) if hasattr(ast, 'declarations') else 0
        print(f"✓ Parsing complete: AST with {decl_count} declarations\n")
        
        # Phase 3: Semantic Analysis
        print("=== Phase 3: Semantic Analysis ===")
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        if analyzer.errors:
            print("✗ Semantic errors found:\n")
            for error in analyzer.errors:
                print(f"  {error}")
            return False
        print(f"✓ Semantic analysis complete: No errors\n")
        
        # Phase 4: TAC Generation
        print("=== Phase 4: TAC Generation ===")
        codegen = CodeGenerator()
        tac_code = codegen.generate(ast)
        print(f"✓ TAC generation complete: {len(tac_code)} instructions\n")
        
        # Phase 5: C Code Generation
        print("=== Phase 5: C Code Generation ===")
        c_codegen = CCodeGenerator()
        c_code = c_codegen.generate(tac_code)
        
        # Write C file
        with open(c_file, 'w', encoding='utf-8') as f:
            f.write(c_code)
        print(f"✓ C code generated: {c_file}\n")
        
        # Phase 6: Backend Compilation
        print("=== Phase 6: Backend Compilation ===")
        backend = Backend()
        
        # Display backend info
        info = backend.get_info()
        print(f"GCC: {info.get('gcc_version', 'Unknown')}\n")
        
        success = True
        
        # Generate executable if requested
        if generate_exe:
            print("Compiling to executable...")
            exe_success, exe_msg = backend.compile_to_executable(
                c_file, exe_file, optimization
            )
            print(exe_msg)
            if not exe_success:
                success = False
        
        # Clean up C file if requested
        if not keep_c and success:
            try:
                os.remove(c_file)
                print(f"\n✓ Cleaned up: {c_file}")
            except:
                pass
        
        # Summary
        print(f"\n{'='*60}")
        if success:
            print("✓ Compilation successful!")
            print(f"\nGenerated files:")
            if keep_c:
                print(f"  • {c_file} (C source)")
            if generate_exe and os.path.exists(exe_file):
                print(f"  • {exe_file} (Executable)")
        else:
            print("✗ Compilation failed")
        print(f"{'='*60}\n")
        
        return success
        
    except FileNotFoundError:
        print(f"✗ Error: File not found: {source_file}")
        return False
    except SyntaxError as e:
        print(f"✗ Syntax Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Compilation Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Command-line interface for backend compiler"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Minipar Backend Compiler - Compile to Executable"
    )
    parser.add_argument("input", help="Input .minipar source file")
    parser.add_argument("-o", "--output", help="Output base name (without extension)")
    parser.add_argument(
        "--no-keep-c",
        action="store_true",
        help="Don't keep intermediate C file"
    )
    parser.add_argument(
        "-O",
        "--optimize",
        choices=["0", "1", "2", "3", "s"],
        default="2",
        help="GCC optimization level (default: 2)"
    )
    
    args = parser.parse_args()
    
    # Run compilation
    success = compile_minipar_pipeline(
        source_file=args.input,
        output_base=args.output,
        generate_exe=True,
        keep_c=not args.no_keep_c,
        optimization=args.optimize
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
