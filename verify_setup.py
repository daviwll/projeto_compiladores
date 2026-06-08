"""
Dependency Verification Script
Checks that all required dependencies are properly installed
"""
import sys

def check_python_version():
    """Check Python version"""
    print("=" * 70)
    print("CHECKING PYTHON VERSION")
    print("=" * 70)
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python version is compatible (3.8+)")
        return True
    else:
        print("❌ Python version must be 3.8 or higher")
        return False

def check_dependencies():
    """Check all required dependencies"""
    print("\n" + "=" * 70)
    print("CHECKING DEPENDENCIES")
    print("=" * 70)
    
    dependencies = {
        "gradio": "Web interface framework",
        "pathlib": "Path manipulation (stdlib)",
        "tempfile": "Temporary file handling (stdlib)",
        "base64": "Base64 encoding (stdlib)",
        "subprocess": "Process management (stdlib)",
        "io": "I/O operations (stdlib)",
        "os": "Operating system interface (stdlib)",
    }
    
    all_ok = True
    for module_name, description in dependencies.items():
        try:
            mod = __import__(module_name)
            version = getattr(mod, '__version__', 'stdlib')
            print(f"✅ {module_name:15} - {description:40} [{version}]")
        except ImportError:
            print(f"❌ {module_name:15} - {description:40} [NOT FOUND]")
            all_ok = False
    
    return all_ok

def check_compiler_modules():
    """Check compiler source modules"""
    print("\n" + "=" * 70)
    print("CHECKING COMPILER MODULES")
    print("=" * 70)
    
    sys.path.insert(0, 'src')
    
    modules = [
        "lexer",
        "parser",
        "semantic",
        "codegen",
        "c_codegen",
        "arm_codegen",
        "backend",
        "compiler",
    ]
    
    all_ok = True
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name:20} - Available")
        except ImportError as e:
            print(f"❌ {module_name:20} - Import failed: {e}")
            all_ok = False
    
    return all_ok

def check_web_interface():
    """Check web interface modules"""
    print("\n" + "=" * 70)
    print("CHECKING WEB INTERFACE")
    print("=" * 70)
    
    sys.path.insert(0, 'interface')
    
    try:
        import compiler_api
        print("✅ compiler_api - Available")
        
        # Try to create API instance
        api = compiler_api.CompilerAPI()
        print("✅ CompilerAPI - Instance created successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Web interface - Import failed: {e}")
        return False

def main():
    """Run all checks"""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "MINIPAR COMPILER - DEPENDENCY CHECK" + " " * 18 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = []
    
    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Compiler Modules", check_compiler_modules()))
    results.append(("Web Interface", check_web_interface()))
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    all_passed = all(result for _, result in results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} - {name}")
    
    print("=" * 70)
    
    if all_passed:
        print("\n✅ ALL CHECKS PASSED!")
        print("   The Minipar Compiler is ready to use.")
        print("\n   To start the web interface, run:")
        print("   cd interface && start.bat")
        return 0
    else:
        print("\n❌ SOME CHECKS FAILED!")
        print("   Please install missing dependencies:")
        print("   uv sync")
        return 1

if __name__ == '__main__':
    sys.exit(main())
