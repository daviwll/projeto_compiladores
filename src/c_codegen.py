"""
C Code Generator for Minipar Language
Translates Three-Address Code (TAC) to C code
"""

from typing import List, Dict, Set, Optional
try:
    from src.codegen import TAC, CodeGenerator
except ImportError:
    from codegen import TAC, CodeGenerator


class CCodeGenerator:
    """Generates C code from Three-Address Code"""
    
    def __init__(self):
        self.c_code: List[str] = []
        self.functions: Dict[str, List[str]] = {}
        self.current_function: Optional[str] = None
        self.function_code: List[str] = []
        self.indent_level = 0
        self.temp_vars: Set[str] = set()
        self.global_vars: Dict[str, str] = {}
        self.function_signatures: Dict[str, tuple] = {}
        self.function_params: Dict[str, List[str]] = {}
        self.label_map: Dict[str, str] = {}
        self.in_par_block = False
        self.par_thread_funcs: List[str] = []
        self.par_thread_code: Dict[int, List[str]] = {}
        self.current_thread_id: Optional[int] = None
        self.pending_params: List[str] = []
        self.last_label: Optional[str] = None
        self.current_local_vars: Dict[str, str] = {}
        # OO support
        self.classes: Dict[str, dict] = {}           # class_name -> {fields: [(name,type)], base: str}
        self.var_types: Dict[str, str] = {}          # var_name -> class_name
        self.method_class_map: Dict[str, str] = {}   # func_name -> class_name
    
    def indent(self) -> str:
        """Get current indentation"""
        return "    " * self.indent_level
    
    def emit(self, line: str):
        """Emit a line of C code"""
        if self.current_function:
            self.function_code.append(self.indent() + line)
        else:
            self.c_code.append(self.indent() + line)
    
    def emit_blank(self):
        """Emit a blank line"""
        if self.current_function:
            self.function_code.append("")
        else:
            self.c_code.append("")
    
    def generate(self, tac_instructions: List[TAC]) -> str:
        """
        Generate C code from TAC instructions
        Returns the complete C program as a string
        """
        # Reset state
        self.c_code = []
        self.functions = {}
        self.temp_vars = set()
        self.global_vars = {}
        self.function_signatures = {}
        self.classes = {}
        self.var_types = {}
        self.method_class_map = {}

        # First pass: collect information about functions, variables, and OO structure
        self._analyze_oo_tac(tac_instructions)
        self._analyze_tac(tac_instructions)

        # Generate C code
        self._generate_headers()
        self._generate_struct_definitions()
        self._generate_forward_declarations()
        self._generate_global_variables()
        self._generate_functions(tac_instructions)
        self._generate_main_function(tac_instructions)
        
        return "\n".join(self.c_code)
    
    def _analyze_tac(self, instructions: List[TAC]):
        """First pass: analyze TAC to collect information"""
        current_func = None
        
        # First, identify which PARAM instructions are for CALLs
        call_params = set()  # Indices of PARAM instructions that are for CALL arguments
        for i, instr in enumerate(instructions):
            if instr.op == 'CALL':
                n_args = int(instr.arg2) if instr.arg2 else 0
                # Mark the previous n_args PARAM instructions as call arguments
                j = i - 1
                count = 0
                while j >= 0 and count < n_args:
                    if instructions[j].op == 'PARAM':
                        call_params.add(j)
                        count += 1
                    j -= 1
        
        # Build a map of temp variables to their eventual destinations
        # This helps with polymorphic input() typing
        temp_destinations = {}  # temp_var -> destination_var
        input_vars = set()  # Variables that get their value from input()
        
        for i, instr in enumerate(instructions):
            if instr.op == 'ASSIGN' and instr.arg1 and isinstance(instr.arg1, str):
                if instr.arg1.startswith('t') and instr.result and not instr.result.startswith('t'):
                    # This is: real_var = temp_var
                    # Look backwards to find where temp_var was assigned
                    for j in range(i-1, -1, -1):
                        if instructions[j].result == instr.arg1:
                            # Found where temp was assigned
                            if instructions[j].op == 'CALL' and instructions[j].arg1 == 'input':
                                # This temp comes from input(), record the destination
                                temp_destinations[instr.arg1] = instr.result
                                input_vars.add(instr.result)
                            break
        
        # For variables that come from input(), analyze their usage to determine type
        # Heuristic: if used in arithmetic, it's number; otherwise assume string
        input_var_types = {}  # var -> inferred type
        for var in input_vars:
            # Default to string (safer choice, matches the common case)
            var_type = 'char*'
            
            # Look for usage patterns
            for instr in instructions:
                # Check if used in arithmetic operations
                if instr.op in ['+', '-', '*', '/', '%']:
                    if instr.arg1 == var or instr.arg2 == var:
                        var_type = 'int'  # Used in math, must be number
                        break
                # Check if result of arithmetic (assigned from math operation)
                if instr.op in ['+', '-', '*', '/', '%'] and instr.result == var:
                    var_type = 'int'
                    break
            
            input_var_types[var] = var_type
        
        # Now collect function parameters (PARAM instructions NOT for calls)
        for i, instr in enumerate(instructions):
            if instr.op == 'FUNC_BEGIN':
                current_func = instr.arg1
                # Collect function FORMAL parameters (PARAM instructions after FUNC_BEGIN that are NOT call args)
                params = []
                j = i + 1
                while j < len(instructions) and instructions[j].op == 'PARAM':
                    if j not in call_params:  # Only formal parameters, not call arguments
                        params.append(instructions[j].arg1)
                    j += 1
                self.function_params[current_func] = params
            elif instr.op == 'FUNC_END':
                current_func = None
            elif current_func is None:
                # Global scope - collect global variables and infer types
                if instr.op == 'ASSIGN' and instr.result and not instr.result.startswith('t'):
                    # Only infer type on first assignment (don't overwrite)
                    if instr.result not in self.global_vars:
                        # Check if this variable comes from input
                        if instr.result in input_var_types:
                            # Use the inferred type from usage analysis
                            self.global_vars[instr.result] = input_var_types[instr.result]
                        else:
                            # Infer type from assigned value
                            var_type = self._infer_type(instr.arg1)
                            self.global_vars[instr.result] = var_type
            
            # Collect temporary variables
            if instr.result and instr.result.startswith('t'):
                self.temp_vars.add(instr.result)
        
        # Store temp destinations for use during code generation
        self.temp_destinations = temp_destinations
    
    def _analyze_oo_tac(self, instructions: List[TAC]):
        """First pass: collect class definitions, method map, and variable types."""
        in_class = None
        current_fields: List[tuple] = []
        current_base: Optional[str] = None

        for instr in instructions:
            if instr.op == 'CLASS_BEGIN':
                parts = str(instr.arg1).split(' extends ', 1)
                in_class = parts[0].strip()
                current_base = parts[1].strip() if len(parts) > 1 else None
                current_fields = []
            elif instr.op == 'CLASS_END':
                if in_class:
                    self.classes[in_class] = {'fields': list(current_fields), 'base': current_base}
                in_class = None
            elif instr.op == 'FIELD' and in_class:
                current_fields.append((str(instr.arg1), str(instr.arg2)))
            elif instr.op == 'FUNC_BEGIN':
                fname = str(instr.arg1)
                for cls in self.classes:
                    if fname.startswith(cls + '_'):
                        self.method_class_map[fname] = cls
                        break
            elif instr.op == 'NEW_OBJECT' and instr.result:
                self.var_types[str(instr.result)] = str(instr.arg1)
            elif instr.op == 'ASSIGN':
                if instr.arg1 and str(instr.arg1) in self.var_types and instr.result:
                    self.var_types[str(instr.result)] = self.var_types[str(instr.arg1)]

    def _generate_struct_definitions(self):
        """Emit C struct typedefs for each class."""
        if not self.classes:
            return
        self.emit("// Class struct definitions")
        for class_name, info in self.classes.items():
            self.emit(f"typedef struct {class_name} {{")
            self.indent_level += 1
            for fname, ftype in info['fields']:
                self.emit(f"{self._minipar_type_to_c(ftype)} {fname};")
            self.indent_level -= 1
            self.emit(f"}} {class_name};")
        self.emit_blank()

    def _minipar_type_to_c(self, t: str) -> str:
        return {'number': 'int', 'string': 'char*', 'bool': 'int', 'void': 'void'}.get(t, 'int')

    def _infer_type(self, value) -> str:
        """Infer C type from a value"""
        if value is None:
            return 'int'
        
        # String literal
        if isinstance(value, str):
            if value.startswith('"') and value.endswith('"'):
                return 'char*'
            # Boolean literals
            if value in ['true', 'false']:
                return 'int'
        
        # Number
        try:
            float(str(value))
            return 'int'
        except (ValueError, TypeError):
            pass
        
        # Default to int
        return 'int'
    
    def _generate_headers(self):
        """Generate C headers and includes"""
        self.emit("#include <stdio.h>")
        self.emit("#include <stdlib.h>")
        self.emit("#include <string.h>")
        self.emit("#include <stdbool.h>")
        
        # Add pthread if we have PAR blocks
        if any(instr.op in ['PAR_BEGIN', 'THREAD_START'] for instr in []):
            self.emit("#include <pthread.h>")
        
        self.emit_blank()
        
        # Add input buffer and helper functions
        self.emit("// Input handling")
        self.emit("#define INPUT_BUFFER_SIZE 1024")
        self.emit("char __input_buffer[INPUT_BUFFER_SIZE];")
        self.emit_blank()
        
        # Helper function to read string input
        self.emit("// Read string input (returns dynamically allocated string)")
        self.emit("char* __read_string_input(const char* prompt) {")
        self.indent_level += 1
        self.emit("if (prompt != NULL) {")
        self.indent_level += 1
        self.emit("printf(\"%s\", prompt);")
        self.indent_level -= 1
        self.emit("}")
        self.emit("if (fgets(__input_buffer, INPUT_BUFFER_SIZE, stdin) != NULL) {")
        self.indent_level += 1
        self.emit("// Remove trailing newline if present")
        self.emit("size_t len = strlen(__input_buffer);")
        self.emit("if (len > 0 && __input_buffer[len-1] == '\\n') {")
        self.indent_level += 1
        self.emit("__input_buffer[len-1] = '\\0';")
        self.indent_level -= 1
        self.emit("}")
        self.emit("// Return a copy of the input")
        self.emit("char* result = (char*)malloc(strlen(__input_buffer) + 1);")
        self.emit("strcpy(result, __input_buffer);")
        self.emit("return result;")
        self.indent_level -= 1
        self.emit("}")
        self.emit("return NULL;")
        self.indent_level -= 1
        self.emit("}")
        self.emit_blank()
        
        # Helper function to read number input
        self.emit("// Read number input")
        self.emit("int __read_number_input(const char* prompt) {")
        self.indent_level += 1
        self.emit("char* str_input = __read_string_input(prompt);")
        self.emit("if (str_input != NULL) {")
        self.indent_level += 1
        self.emit("int result = atoi(str_input);")
        self.emit("free(str_input);")
        self.emit("return result;")
        self.indent_level -= 1
        self.emit("}")
        self.emit("return 0;")
        self.indent_level -= 1
        self.emit("}")
        self.emit_blank()
    
    def _generate_forward_declarations(self):
        """Generate forward declarations for functions"""
        if not self.function_params:
            return
        self.emit("// Forward declarations")
        for func_name, params in self.function_params.items():
            class_name = self.method_class_map.get(func_name)
            if class_name:
                non_this = [p for p in params if p != 'this']
                param_parts = [f"{class_name}* this"] + [f"int {p}" for p in non_this]
                ret = f"{class_name}*" if func_name.endswith('_ctor') else "int"
                self.emit(f"{ret} {func_name}({', '.join(param_parts)});")
            else:
                param_list = ", ".join([f"int {p}" for p in params])
                self.emit(f"int {func_name}({param_list});")
        self.emit_blank()
    
    def _generate_global_variables(self):
        """Generate global variable declarations"""
        if self.global_vars:
            self.emit("// Global variables")
            for var_name, var_type in self.global_vars.items():
                if var_name in self.var_types:
                    cls = self.var_types[var_name]
                    self.emit(f"{cls}* {var_name} = NULL;")
                elif var_type == 'char*':
                    self.emit(f"{var_type} {var_name} = NULL;")
                else:
                    self.emit(f"{var_type} {var_name} = 0;")
            self.emit_blank()
    
    def _generate_functions(self, instructions: List[TAC]):
        """Generate all user-defined functions"""
        # First, identify which PARAM instructions are for CALLs
        call_params_indices = set()  # Indices of PARAM instructions that are for CALL arguments
        for i, instr in enumerate(instructions):
            if instr.op == 'CALL':
                n_args = int(instr.arg2) if instr.arg2 else 0
                # Mark the previous n_args PARAM instructions as call arguments
                j = i - 1
                count = 0
                while j >= 0 and count < n_args:
                    if instructions[j].op == 'PARAM':
                        call_params_indices.add(j)
                        count += 1
                    j -= 1
        
        i = 0
        while i < len(instructions):
            instr = instructions[i]
            
            if instr.op == 'FUNC_BEGIN':
                func_name = instr.arg1
                self.current_function = func_name
                self.function_code = []
                self.label_map = {}
                self.last_label = None
                self.pending_params = []
                self.current_local_vars = {}

                # Collect FORMAL parameters (not call arguments)
                params = []
                j = i + 1
                while j < len(instructions) and instructions[j].op == 'PARAM':
                    if j not in call_params_indices:
                        params.append(instructions[j].arg1)
                    j += 1

                # Build function signature - OO methods get proper types
                class_name = self.method_class_map.get(func_name)
                if class_name:
                    self.var_types['this'] = class_name
                    non_this = [p for p in params if p != 'this']
                    param_parts = [f"{class_name}* this"] + [f"int {p}" for p in non_this]
                    ret = f"{class_name}*" if func_name.endswith('_ctor') else "int"
                    self.emit(f"{ret} {func_name}({', '.join(param_parts)}) {{")
                else:
                    param_list = ", ".join([f"int {p}" for p in params])
                    self.emit(f"int {func_name}({param_list}) {{")
                self.indent_level += 1

                # Declare local temp variables with proper types
                local_temps = set()
                k = i
                while k < len(instructions):
                    if instructions[k].op == 'FUNC_END':
                        break
                    if instructions[k].result and str(instructions[k].result).startswith('t'):
                        local_temps.add(str(instructions[k].result))
                    k += 1

                if local_temps:
                    self.emit("// Temporary variables")
                    for temp in sorted(local_temps):
                        if temp in self.var_types:
                            cls = self.var_types[temp]
                            self.emit(f"{cls}* {temp} = NULL;")
                        else:
                            self.emit(f"int {temp} = 0;")

                # Declare local non-parameter variables
                local_vars: Dict[str, str] = {}
                k = i
                while k < len(instructions):
                    if instructions[k].op == 'FUNC_END':
                        break
                    if instructions[k].op == 'ASSIGN':
                        var = instructions[k].result
                        if var and not str(var).startswith('t') and var not in self.global_vars and var not in params:
                            if var not in local_vars:
                                if var in self.var_types:
                                    local_vars[var] = f"class:{self.var_types[var]}"
                                else:
                                    local_vars[var] = self._infer_type(instructions[k].arg1)
                    k += 1

                self.current_local_vars = local_vars.copy()

                if local_vars:
                    self.emit("// Local variables")
                    for var, var_type in sorted(local_vars.items()):
                        if var_type.startswith('class:'):
                            cls = var_type[6:]
                            self.emit(f"{cls}* {var} = NULL;")
                        elif var_type == 'char*':
                            self.emit(f"{var_type} {var} = NULL;")
                        else:
                            self.emit(f"{var_type} {var} = 0;")

                if local_temps or local_vars:
                    self.emit_blank()

                # Generate function body (skip formal PARAM instructions)
                j = i + 1
                while j < len(instructions) and instructions[j].op == 'PARAM' and j not in call_params_indices:
                    j += 1

                while j < len(instructions):
                    instr = instructions[j]
                    if instr.op == 'FUNC_END':
                        if self.last_label:
                            self.emit(";  // Empty statement after label")
                        i = j
                        break
                    self._generate_instruction(instr)
                    j += 1

                # End function
                self.indent_level -= 1
                self.emit("}")
                self.emit_blank()

                # Save function code
                self.functions[func_name] = self.function_code[:]
                self.c_code.extend(self.function_code)
                self.current_function = None
                self.function_code = []
                if 'this' in self.var_types:
                    del self.var_types['this']
            
            i += 1
    
    def _generate_main_function(self, instructions: List[TAC]):
        """Generate main function with global scope code"""
        self.emit("int main() {")
        self.indent_level += 1
        self.last_label = None
        self.current_local_vars = {}  # Reset for main function
        
        # Collect temps used in global scope
        global_temps = set()
        for instr in instructions:
            if instr.op not in ['FUNC_BEGIN', 'FUNC_END', 'PARAM']:
                # Check if this is outside a function
                in_function = False
                for check_instr in instructions[:instructions.index(instr)]:
                    if check_instr.op == 'FUNC_BEGIN':
                        in_function = True
                    elif check_instr.op == 'FUNC_END':
                        in_function = False
                
                if not in_function and instr.result and instr.result.startswith('t'):
                    global_temps.add(instr.result)
        
        if global_temps:
            self.emit("// Temporary variables")
            for temp in sorted(global_temps):
                if temp in self.var_types:
                    cls = self.var_types[temp]
                    self.emit(f"{cls}* {temp} = NULL;")
                else:
                    self.emit(f"int {temp} = 0;")
            self.emit_blank()
        
        # Generate global scope instructions (outside functions)
        self.pending_params = []
        in_function = False
        for instr in instructions:
            if instr.op == 'FUNC_BEGIN':
                in_function = True
            elif instr.op == 'FUNC_END':
                in_function = False
            elif not in_function:
                self._generate_instruction(instr)
        
        # Check if last instruction was a label
        if self.last_label:
            self.emit(";  // Empty statement after label")
        
        self.emit_blank()
        self.emit("return 0;")
        self.indent_level -= 1
        self.emit("}")
    
    def _generate_instruction(self, instr: TAC):
        """Generate C code for a single TAC instruction"""
        op = instr.op
        
        # Skip function boundary markers and class metadata
        if op in ['FUNC_BEGIN', 'FUNC_END', 'CLASS_BEGIN', 'CLASS_END', 'FIELD', 'METHOD_ARGS']:
            return
        
        # Handle PARAM instructions - collect them for the next CALL
        if op == 'PARAM':
            self.pending_params.append(instr.arg1)
            # Debug: print(f"DEBUG: Added PARAM {instr.arg1}, pending_params = {self.pending_params}")
            return
        
        # Labels
        if op == 'LABEL':
            self.indent_level -= 1  # Unindent labels
            self.emit(f"{instr.arg1}:")
            self.last_label = instr.arg1
            self.indent_level += 1
            return
        
        # If we're generating a non-label instruction, reset last_label
        self.last_label = None
        
        # Jumps
        if op == 'GOTO':
            self.emit(f"goto {instr.arg1};")
            return
        
        if op == 'IF_FALSE':
            self.emit(f"if (!{instr.arg1}) goto {instr.result};")
            return
        
        if op == 'IF_TRUE':
            self.emit(f"if ({instr.arg1}) goto {instr.result};")
            return
        
        # Assignment
        if op == 'ASSIGN':
            # Check if we need type casting (int temp to char* variable)
            result_type = None
            arg_type = None
            
            # Determine result type
            if instr.result in self.global_vars:
                result_type = self.global_vars[instr.result]
            elif instr.result in self.current_local_vars:
                result_type = self.current_local_vars[instr.result]
            
            # Determine arg type (temps are int, string literals are char*)
            if isinstance(instr.arg1, str):
                if instr.arg1.startswith('"') and instr.arg1.endswith('"'):
                    arg_type = 'char*'
                elif instr.arg1.startswith('t'):
                    arg_type = 'int'  # temps are int
            
            # Add cast if needed
            if result_type == 'char*' and arg_type == 'int':
                self.emit(f"{instr.result} = (char*){self._format_value(instr.arg1)};  // Cast int to char*")
            else:
                self.emit(f"{instr.result} = {self._format_value(instr.arg1)};")
            return
        
        # Binary operations
        if op in ['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '||']:
            left = self._format_value(instr.arg1)
            right = self._format_value(instr.arg2)
            self.emit(f"{instr.result} = {left} {op} {right};")
            return
        
        # Unary operations
        if op == 'UNARY':
            operator = instr.arg1
            operand = self._format_value(instr.arg2)
            self.emit(f"{instr.result} = {operator}{operand};")
            return
        
        # Function calls
        if op == 'CALL':
            func_name = instr.arg1
            n_args = int(instr.arg2) if instr.arg2 else 0
            result = instr.result
            
            # Get the parameters for this call
            call_params = self.pending_params[-n_args:] if n_args > 0 else []
            self.pending_params = self.pending_params[:-n_args] if n_args > 0 else []
            
            # Special handling for built-in functions
            if func_name == 'print':
                # Generate proper printf with actual arguments
                if call_params:
                    # Build format string and args based on parameter types
                    format_parts = []
                    args = []
                    for p in call_params:
                        formatted = self._format_value(p)
                        # Check if it's a string literal or string variable
                        if isinstance(p, str) and p.startswith('"') and p.endswith('"'):
                            format_parts.append("%s")
                            args.append(formatted)
                        elif p in self.global_vars and self.global_vars[p] == 'char*':
                            format_parts.append("%s")
                            args.append(p)
                        else:
                            format_parts.append("%d")
                            args.append(formatted)
                    
                    format_str = " ".join(format_parts)
                    args_str = ", ".join(args)
                    self.emit(f'printf("{format_str}\\n", {args_str});')
                else:
                    self.emit(f'printf("\\n");')
            elif func_name == 'input':
                # Handle input function
                # Determine if we need string or number result
                prompt_arg = None
                if call_params:
                    # Has prompt parameter
                    prompt_arg = self._format_value(call_params[0])
                
                if result:
                    # Check if result variable (or its destination) is string or number type
                    result_is_string = False
                    
                    # If result is a temp, check where it eventually goes
                    final_dest = result
                    if result.startswith('t') and hasattr(self, 'temp_destinations'):
                        final_dest = self.temp_destinations.get(result, result)
                    
                    # Check in global vars
                    if final_dest in self.global_vars:
                        result_is_string = self.global_vars[final_dest] == 'char*'
                    # Check in local vars
                    elif final_dest in self.current_local_vars:
                        result_is_string = self.current_local_vars[final_dest] == 'char*'
                    
                    if result_is_string:
                        # Return string (store as int with cast for compatibility)
                        if prompt_arg:
                            self.emit(f'{result} = (int)__read_string_input({prompt_arg});  // Cast char* to int')
                        else:
                            self.emit(f'{result} = (int)__read_string_input(NULL);  // Cast char* to int')
                    else:
                        # Return number (convert string to int)
                        if prompt_arg:
                            self.emit(f'{result} = __read_number_input({prompt_arg});')
                        else:
                            self.emit(f'{result} = __read_number_input(NULL);')
                else:
                    # No result, just read and discard (shouldn't happen but handle it)
                    if prompt_arg:
                        self.emit(f'(void)__read_string_input({prompt_arg});')
                    else:
                        self.emit(f'(void)__read_string_input(NULL);')
            else:
                # User-defined function with proper arguments
                args_str = ", ".join([self._format_value(p) for p in call_params])
                if result:
                    self.emit(f"{result} = {func_name}({args_str});")
                else:
                    self.emit(f"{func_name}({args_str});")
            return
        
        # Return
        if op == 'RETURN':
            if instr.arg1:
                self.emit(f"return {self._format_value(instr.arg1)};")
            else:
                self.emit("return 0;")
            return
        
        # SEQ blocks
        if op == 'SEQ_BEGIN':
            self.emit("// Sequential block")
            self.emit("{")
            self.indent_level += 1
            return
        
        if op == 'SEQ_END':
            self.indent_level -= 1
            self.emit("}")
            return
        
        # PAR blocks - generate pthread code
        if op == 'PAR_BEGIN':
            self.emit("// Parallel block (simplified - sequential execution)")
            self.emit("{")
            self.indent_level += 1
            self.in_par_block = True
            return
        
        if op == 'PAR_END':
            self.indent_level -= 1
            self.emit("}")
            self.in_par_block = False
            return
        
        if op == 'THREAD_START':
            self.emit(f"// Thread {instr.arg1 if instr.arg1 else 0} start")
            return
        
        if op == 'THREAD_END':
            self.emit(f"// Thread {instr.arg1 if instr.arg1 else 0} end")
            return
        
        # Channel operations
        if op == 'CHANNEL_CREATE':
            self.emit(f"// Channel {instr.arg2} created ({instr.arg1})")
            return
        
        # OO operations
        if op == 'NEW_OBJECT':
            cls = str(instr.arg1)
            n_args = int(instr.arg2) if instr.arg2 else 0
            result = instr.result
            ctor_args = self.pending_params[-n_args:] if n_args > 0 else []
            self.pending_params = self.pending_params[:-n_args] if n_args > 0 else self.pending_params
            all_args = [self._format_value(result)] + [self._format_value(a) for a in ctor_args]
            self.emit(f"{result} = ({cls}*)malloc(sizeof({cls}));")
            self.emit(f"{cls}_ctor({', '.join(all_args)});")
            return

        if op == 'MEMBER_ACCESS':
            obj = instr.arg1
            field = instr.arg2
            result = instr.result
            self.emit(f"{result} = {self._format_value(obj)}->{field};")
            return

        if op == 'MEMBER_STORE':
            obj = instr.arg1
            field = instr.arg2
            value = instr.result
            self.emit(f"{self._format_value(obj)}->{field} = {self._format_value(value)};")
            return

        if op == 'METHOD_CALL':
            receiver = str(instr.arg1)
            method = str(instr.arg2)
            result = instr.result
            cls = self.var_types.get(receiver)
            method_args = [self._format_value(p) for p in self.pending_params]
            self.pending_params = []
            if cls:
                func_name = f"{cls}_{method}"
                all_args = [self._format_value(receiver)] + method_args
                if result:
                    self.emit(f"{result} = {func_name}({', '.join(all_args)});")
                else:
                    self.emit(f"{func_name}({', '.join(all_args)});")
            else:
                self.emit(f"// METHOD_CALL unresolved: {receiver}.{method}")
            return
        
        # Default: comment out unknown instructions
        self.emit(f"// TAC: {instr}")
    
    def _format_value(self, value) -> str:
        """Format a value for C code"""
        if value is None:
            return "0"
        
        # String literal
        if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
            return value.replace('\\n', '\\n')  # Preserve escape sequences
        
        # Boolean literals
        if value == "true":
            return "1"
        if value == "false":
            return "0"
        
        # Numbers and variables
        return str(value)
    
    def print_code(self):
        """Print the generated C code"""
        print("\n=== Generated C Code ===")
        print("\n".join(self.c_code))
    
    def save_to_file(self, filename: str):
        """Save generated C code to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.c_code))
        print(f"\n✓ C code saved to: {filename}")
