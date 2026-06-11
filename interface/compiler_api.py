"""
Minipar Compiler API
Backend API for the Gradio frontend interface
"""

import sys
import os
import io
import tempfile
import base64
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from compiler import compile_source


class CompilerAPI:
    """API wrapper for the Minipar compiler"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        
    def compile_code(self, source_code, show_tokens=False, show_ast=False, 
                     show_semantic=False, show_tac=True, generate_c=False,
                     generate_asm=False, generate_exe=False):
        """
        Compile Minipar source code and return results
        
        Args:
            source_code: Minipar source code string
            show_tokens: Show token stream
            show_ast: Show abstract syntax tree
            show_semantic: Show semantic analysis
            show_tac: Show Three-Address Code
            generate_c: Generate C code
            generate_asm: Generate assembly code
            generate_exe: Generate executable
            
        Returns:
            dict with compilation results
        """
        if not source_code or not source_code.strip():
            return {
                'success': False,
                'error': 'No source code provided',
                'output': '',
                'tokens': '',
                'ast': '',
                'semantic': '',
                'tac': '',
                'c_code': '',
                'assembly': '',
                'exe_file': None
            }
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        result = {
            'success': False,
            'error': '',
            'output': '',
            'tokens': '',
            'ast': '',
            'semantic': '',
            'tac': '',
            'c_code': '',
            'assembly': '',
            'exe_file': None
        }
        
        # Set up output file paths in current directory (not temp)
        c_output = 'output.c'
        asm_output = 'output.s'
        
        try:
            # Compile the source code
            codegen, c_gen, arm_gen = compile_source(
                source_code,
                show_tokens=show_tokens,
                show_ast=show_ast,
                show_semantic=show_semantic,
                generate_c=generate_c or generate_exe,
                c_output=c_output,
                compile_exe=generate_exe,
                generate_asm=generate_asm
            )
            
            # Get the captured output
            output = captured_output.getvalue()
            
            # Parse output sections
            result['output'] = output
            result['success'] = True
            
            # Extract TAC if requested
            if show_tac and codegen:
                tac_lines = []
                for i, instr in enumerate(codegen.code):
                    tac_lines.append(f"{i:3d}: {instr}")
                result['tac'] = '\n'.join(tac_lines)
            
            # Extract tokens section
            if show_tokens and '=== Lexical Analysis ===' in output:
                tokens_start = output.find('Tokens:')
                if tokens_start != -1:
                    tokens_end = output.find('===', tokens_start)
                    result['tokens'] = output[tokens_start:tokens_end].strip()
            
            # Extract AST section
            if show_ast and 'AST:' in output:
                ast_start = output.find('AST:')
                ast_end = output.find('===', ast_start)
                if ast_start != -1 and ast_end != -1:
                    result['ast'] = output[ast_start:ast_end].strip()
            
            # Get C code if generated
            if (generate_c or generate_exe) and c_gen:
                # C code is stored in c_gen.c_code list
                result['c_code'] = '\n'.join(c_gen.c_code)
                
            # Get assembly if generated  
            if generate_asm:
                # Assembly is saved to output.s in current directory
                if os.path.exists(asm_output):
                    with open(asm_output, 'r', encoding='utf-8') as f:
                        result['assembly'] = f.read()
                else:
                    result['assembly'] = "Assembly file not found"
            
            # Get executable if generated
            if generate_exe:
                exe_path = 'output.exe' if os.name == 'nt' else 'output'
                if os.path.exists(exe_path):
                    # Read the executable file
                    with open(exe_path, 'rb') as f:
                        exe_data = f.read()
                    result['exe_file'] = {
                        'name': 'minipar_program.exe',
                        'data': base64.b64encode(exe_data).decode('utf-8'),
                        'path': os.path.abspath(exe_path)
                    }
                else:
                    result['error'] = f"Executable not found at {exe_path}"
        except SyntaxError as e:
            result['error'] = f"Compilation Error: {str(e)}"
            result['output'] = captured_output.getvalue()
            
        except Exception as e:
            result['error'] = f"Unexpected Error: {str(e)}"
            result['output'] = captured_output.getvalue()
            
        finally:
            sys.stdout = old_stdout
            
        return result
    
    def execute_code(self, source_code, user_input=""):
        """
        Execute Minipar code and return output
        
        Args:
            source_code: Minipar source code
            user_input: Input to provide to the program
            
        Returns:
            dict with execution results
        """
        # First compile to executable
        compile_result = self.compile_code(
            source_code,
            show_tac=False,
            generate_exe=True
        )
        
        if not compile_result['success']:
            return {
                'success': False,
                'error': compile_result['error'],
                'output': compile_result['output']
            }
        
        if not compile_result['exe_file']:
            return {
                'success': False,
                'error': 'Failed to generate executable',
                'output': compile_result['output']
            }
        
        # Execute the program
        exe_path = compile_result['exe_file']['path']
        
        try:
            import subprocess
            
            # Prepare input
            stdin_data = user_input.encode('utf-8') if user_input else None
            
            # Run the executable
            process = subprocess.Popen(
                [exe_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = process.communicate(input=stdin_data, timeout=10)
            
            output = stdout.decode('utf-8', errors='replace')
            if stderr:
                error_output = stderr.decode('utf-8', errors='replace')
                if error_output.strip():  # Only add if there's actual error content
                    output += f"\n\nStderr:\n{error_output}"
            
            return {
                'success': True,
                'output': output,
                'error': ''
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Execution timeout (10 seconds)'
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': f'Execution error: {str(e)}'
            }


# Global API instance
api = CompilerAPI()


def compile_and_show(source_code, show_tokens, show_ast, show_semantic, 
                     show_tac, show_c, show_assembly):
    """
    Compile code and return formatted output for display
    """
    result = api.compile_code(
        source_code,
        show_tokens=show_tokens,
        show_ast=show_ast,
        show_semantic=show_semantic,
        show_tac=show_tac,
        generate_c=show_c,
        generate_asm=show_assembly
    )
    
    if not result['success']:
        return f"❌ Error:\n{result['error']}\n\n{result['output']}", ""
    
    # Format output based on selected options
    output_parts = []
    
    if show_tokens and result['tokens']:
        output_parts.append(f"🔤 TOKENS\n{'='*60}\n{result['tokens']}\n")
    
    if show_ast and result['ast']:
        output_parts.append(f"🌳 ABSTRACT SYNTAX TREE\n{'='*60}\n{result['ast']}\n")
    
    if show_semantic:
        output_parts.append(f"✓ SEMANTIC ANALYSIS\n{'='*60}\nSemantic analysis complete\n")
    
    if show_tac and result['tac']:
        output_parts.append(f"📝 THREE-ADDRESS CODE (TAC)\n{'='*60}\n{result['tac']}\n")
    
    if show_c and result['c_code']:
        output_parts.append(f"⚙️ GENERATED C CODE\n{'='*60}\n{result['c_code']}\n")
    
    if show_assembly and result['assembly']:
        output_parts.append(f"🔧 ARM ASSEMBLY CODE\n{'='*60}\n{result['assembly']}\n")
    
    if not output_parts:
        output_parts.append("✅ Compilation successful! Select options above to view output.")
    
    return '\n\n'.join(output_parts), result['output']


def compile_and_download(source_code):
    """
    Compile code and return executable for download
    """
    result = api.compile_code(source_code, generate_exe=True)
    
    if not result['success']:
        return None, f"❌ Error:\n{result['error']}"
    
    if not result['exe_file']:
        return None, "❌ Failed to generate executable"
    
    exe_path = result['exe_file']['path']
    
    return exe_path, "✅ Executable generated successfully!"


def execute_program(source_code, user_input):
    """
    Execute program and return output
    """
    result = api.execute_code(source_code, user_input)

    if not result['success']:
        return f"❌ Execution Error:\n{result['error']}"

    return result['output']


# ---------------------------------------------------------------------------
# Flask HTTP API
# Endpoints: GET /health, POST /compile, POST /generate, GET /
# Run standalone:  python interface/compiler_api.py
# ---------------------------------------------------------------------------

try:
    import logging
    from flask import Flask, Response, jsonify, request

    flask_app = Flask(__name__)
    flask_app.logger.setLevel(logging.INFO)

    @flask_app.route("/health")
    def health():
        return jsonify({"ok": True})

    @flask_app.route("/compile", methods=["POST"])
    def compile_route():
        data = request.get_json(silent=True) or {}
        source = data.get("source", "")
        if not source.strip():
            return jsonify({"ok": False, "errors": ["No source code provided"]}), 400

        result = api.compile_code(
            source,
            show_tokens=bool(data.get("show_tokens", False)),
            show_ast=bool(data.get("show_ast", False)),
            show_semantic=bool(data.get("show_semantic", False)),
            show_tac=bool(data.get("show_tac", True)),
            generate_c=bool(data.get("generate_c", False)),
            generate_asm=bool(data.get("generate_asm", False)),
        )

        errors = [result["error"]] if result["error"] else []
        return jsonify({
            "ok": result["success"],
            "errors": errors,
            "tac": result["tac"],
            "ast": result["ast"],
            "tokens": result["tokens"],
            "c_code": result["c_code"],
            "assembly": result["assembly"],
            "output": result["output"],
        })

    @flask_app.route("/generate", methods=["POST"])
    def generate_route():
        data = request.get_json(silent=True) or {}
        source = data.get("source", "")
        target = data.get("target", "c")  # "c" or "arm"

        if not source.strip():
            return jsonify({"ok": False, "error": "No source code provided"}), 400
        if target not in ("c", "arm"):
            return jsonify({"ok": False, "error": "target must be 'c' or 'arm'"}), 400

        result = api.compile_code(
            source,
            show_tac=False,
            generate_c=(target == "c"),
            generate_asm=(target == "arm"),
        )

        if not result["success"]:
            return jsonify({"ok": False, "error": result["error"]}), 422

        code = result["c_code"] if target == "c" else result["assembly"]
        return Response(code, status=200, mimetype="text/plain")

    def launch_flask(host="127.0.0.1", port=8000, debug=False):
        """Start the Flask HTTP API."""
        print(f"MiniPar HTTP API running at http://{host}:{port}")
        print("  GET  /health      — readiness check")
        print("  POST /compile     — compile source, returns JSON")
        print("  POST /generate    — generate C or ARM code, returns text")
        flask_app.run(host=host, port=port, debug=debug)

except ImportError:
    flask_app = None  # type: ignore

    def launch_flask(*args, **kwargs):
        raise RuntimeError("Flask is not installed. Run: pip install flask")


if __name__ == "__main__":
    launch_flask(debug=True)
