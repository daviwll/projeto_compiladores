"""
ARM Assembly Code Generator for Minipar Language
Generates correct ARMv7 assembly code from Three-Address Code (TAC)
Following AAPCS (ARM Architecture Procedure Call Standard)

Key features:
- Unique label generation per function to avoid conflicts
- Proper immediate value handling with # prefix
- Correct variable loading/storing from memory
- String literals in .rodata section
- Software routines for division and modulo (__aeabi_idiv, __aeabi_idivmod)
- Proper parameter handling and register allocation
- No duplicate epilogues
"""

from typing import List, Dict, Set, Optional, Union
try:
    from src.codegen import TAC
except ImportError:
    from codegen import TAC


class ARMCodeGenerator:
    """Generates ARMv7 assembly code from Three-Address Code"""

    def __init__(self):
        self.data_section: List[str] = []
        self.rodata_section: List[str] = []
        self.text_section: List[str] = []

        # Variable and function tracking
        self.global_vars: Set[str] = set()
        self.functions: Dict[str, int] = {}
        self.current_function: Optional[str] = None

        # Register management
        self.register_map: Dict[str, str] = {}
        self.next_reg = 4  # r4-r7 are callee-saved; r0-r3 for params/return

        # Label management - unique per function
        self.function_label_prefix = ""

        # Function context
        self.function_params: List[str] = []
        self.function_locals: Set[str] = set()

        # String literal management
        self.string_literals: Dict[str, str] = {}
        self.string_counter = 0

        # Pending parameters for function calls
        self._pending_params: List[str] = []

        # OO support
        self.class_layouts: Dict[str, Dict[str, int]] = {}  # class -> {field: word_offset}
        self.class_sizes: Dict[str, int] = {}               # class -> num_fields
        self.var_types: Dict[str, str] = {}                 # var -> class_name
        self.method_class_map: Dict[str, str] = {}          # func_name -> class_name
        self._has_oo = False                                 # True when OO code present
    
    def generate(self, tac_instructions: List[TAC]) -> str:
        """
        Generate ARMv7 assembly code from TAC instructions
        Returns the complete assembly program as a string
        """
        # First pass: analyze TAC to collect information
        self._analyze_oo_classes(tac_instructions)
        self._analyze_tac(tac_instructions)
        
        # Generate each section
        self._generate_data_section()
        self._generate_rodata_section()
        self._generate_text_section(tac_instructions)
        
        # Combine all sections
        result = []
        
        # Data section
        if self.data_section:
            result.extend(self.data_section)
            result.append("")
        
        # Read-only data section
        if self.rodata_section:
            result.extend(self.rodata_section)
            result.append("")
        
        # Text section
        result.extend(self.text_section)
        result.append("")
        result.append("    .end")
        
        return "\n".join(result)
    
    def _analyze_oo_classes(self, instructions: List[TAC]):
        """Build class field-offset tables and method→class maps from TAC metadata."""
        in_class = None
        field_idx = 0
        for instr in instructions:
            if instr.op == 'CLASS_BEGIN':
                parts = str(instr.arg1).split(' extends ', 1)
                in_class = parts[0].strip()
                field_idx = 0
                self.class_layouts[in_class] = {}
                self.class_sizes[in_class] = 0
                self._has_oo = True
            elif instr.op == 'CLASS_END':
                in_class = None
            elif instr.op == 'FIELD' and in_class:
                self.class_layouts[in_class][str(instr.arg1)] = field_idx
                field_idx += 1
                self.class_sizes[in_class] = field_idx
            elif instr.op == 'FUNC_BEGIN':
                fname = str(instr.arg1)
                for cls in self.class_layouts:
                    if fname.startswith(cls + '_'):
                        self.method_class_map[fname] = cls
                        break
            elif instr.op == 'NEW_OBJECT' and instr.result:
                self.var_types[str(instr.result)] = str(instr.arg1)
            elif instr.op == 'ASSIGN':
                if instr.arg1 and str(instr.arg1) in self.var_types and instr.result:
                    self.var_types[str(instr.result)] = self.var_types[str(instr.arg1)]

    def _analyze_tac(self, instructions: List[TAC]):
        """First pass: identify global variables, functions, and string literals"""
        in_function = False
        
        for instr in instructions:
            if instr.op == 'FUNC_BEGIN':
                in_function = True
                self.functions[instr.arg1] = 0
            elif instr.op == 'FUNC_END':
                in_function = False
            elif not in_function:
                # Skip class metadata (not real global variables)
                if instr.op in ['CLASS_BEGIN', 'CLASS_END', 'FIELD']:
                    pass
                # Global variable - assignment outside function
                elif instr.op == 'ASSIGN' and instr.result:
                    if not str(instr.result).startswith('t'):
                        self.global_vars.add(str(instr.result))
                elif instr.result and not str(instr.result).startswith('t'):
                    if instr.op not in ['PARAM', 'CALL', 'LABEL', 'GOTO',
                                        'NEW_OBJECT', 'MEMBER_ACCESS', 'MEMBER_STORE',
                                        'METHOD_CALL', 'METHOD_ARGS']:
                        self.global_vars.add(str(instr.result))
            
            # Collect string literals from all contexts
            for value in [instr.arg1, instr.arg2, instr.result]:
                if value and isinstance(value, str):
                    if value.startswith('"') and value.endswith('"'):
                        if value not in self.string_literals:
                            label = f".STR{self.string_counter}"
                            self.string_literals[value] = label
                            self.string_counter += 1
    
    def _generate_data_section(self):
        """Generate .data section for global variables and OO heap."""
        self.data_section.append("    .data")
        self.data_section.append("    .align 2")

        if self.global_vars:
            for var in sorted(self.global_vars):
                self.data_section.append(f"{var}:    .word 0")
        else:
            self.data_section.append("    @ No global variables")

        if self._has_oo:
            self.data_section.append("__heap_ptr: .word 0  @ OO bump allocator offset")
            self.data_section.append("    .align 2")
            self.data_section.append("__heap:     .skip 4096  @ 4KB static heap for objects")
    
    def _generate_rodata_section(self):
        """Generate .rodata section for string literals"""
        if not self.string_literals:
            return
        
        self.rodata_section.append("    .section .rodata")
        self.rodata_section.append("    .align 2")
        
        for string_val, label in sorted(self.string_literals.items(), key=lambda x: x[1]):
            # Remove quotes and handle escape sequences
            clean_str = string_val[1:-1]
            clean_str = clean_str.replace('\\n', '\n').replace('\\t', '\t')
            self.rodata_section.append(f"{label}:")
            self.rodata_section.append(f'    .asciz "{clean_str}"')
    
    def _generate_text_section(self, instructions: List[TAC]):
        """Generate .text section with all code"""
        self.text_section.append("    .text")
        self.text_section.append("    .global main")
        self.text_section.append("    .global _start")
        self.text_section.append("    .align 2")
        self.text_section.append("")
        
        # Generate _start that calls main
        self.text_section.append("_start:")
        self.text_section.append("    bl main")
        self.text_section.append("    mov r7, #1      @ exit syscall")
        self.text_section.append("    svc #0          @ make syscall")
        self.text_section.append("")
        
        # Check if there's main code (outside functions)
        has_main_code = self._has_main_code(instructions)

        if has_main_code:
            self._generate_main_function(instructions)

        # Generate user-defined functions
        self._generate_user_functions(instructions)

        # Generate built-in function stubs
        self._generate_builtin_stubs()

        # Generate OO heap allocator if needed
        if self._has_oo:
            self._generate_malloc_stub()
    
    def _has_main_code(self, instructions: List[TAC]) -> bool:
        """Check if there's non-metadata code outside functions."""
        depth = 0
        skip_ops = {'FUNC_BEGIN', 'FUNC_END', 'CLASS_BEGIN', 'CLASS_END', 'FIELD'}
        for instr in instructions:
            if instr.op == 'FUNC_BEGIN':
                depth += 1
            elif instr.op == 'FUNC_END':
                depth -= 1
            elif depth == 0 and instr.op not in skip_ops:
                return True
        return False
    
    def _generate_main_function(self, instructions: List[TAC]):
        """Generate main function with global code"""
        self.text_section.append("main:")
        self.text_section.append("    push {r4, r5, r6, r7, lr}")
        self.text_section.append("")
        
        self.current_function = "main"
        self.function_label_prefix = "main_"
        self.register_map = {}
        self.next_reg = 4
        self._pending_params = []
        
        # Process instructions outside functions
        i = 0
        while i < len(instructions):
            instr = instructions[i]
            
            if instr.op == 'FUNC_BEGIN':
                # Skip entire function
                depth = 1
                i += 1
                while i < len(instructions) and depth > 0:
                    if instructions[i].op == 'FUNC_BEGIN':
                        depth += 1
                    elif instructions[i].op == 'FUNC_END':
                        depth -= 1
                    i += 1
                continue
            
            self._generate_instruction(instr)
            i += 1
        
        self.text_section.append("")
        self.text_section.append("    mov r0, #0")
        self.text_section.append("    pop {r4, r5, r6, r7, lr}")
        self.text_section.append("    bx lr")
        self.text_section.append("")
        
        self.current_function = None
        self.function_label_prefix = ""
    
    def _generate_user_functions(self, instructions: List[TAC]):
        """Generate user-defined functions"""
        i = 0
        while i < len(instructions):
            instr = instructions[i]
            
            if instr.op == 'FUNC_BEGIN':
                func_name = instr.arg1
                self.current_function = func_name
                self.function_label_prefix = f"{func_name}_"
                self.function_params = []
                self.function_locals = set()
                self.register_map = {}
                self.next_reg = 4
                self._pending_params = []

                # Track 'this' type for class methods
                cls = self.method_class_map.get(func_name)
                if cls:
                    self.var_types['this'] = cls

                self.text_section.append(f"{func_name}:")
                self.text_section.append("    push {r4, r5, r6, r7, lr}")
                self.text_section.append("")

                # Process function parameters
                i += 1
                param_reg = 0
                while i < len(instructions) and instructions[i].op == 'PARAM':
                    param_name = str(instructions[i].arg1)
                    self.function_params.append(param_name)
                    if param_reg < 4 and self.next_reg <= 7:
                        self.text_section.append(f"    mov r{self.next_reg}, r{param_reg}  @ save param {param_name}")
                        self.register_map[param_name] = f"r{self.next_reg}"
                        self.next_reg += 1
                    param_reg += 1
                    i += 1

                if self.function_params:
                    self.text_section.append("")

                # Track if we've seen a return
                has_explicit_return = False

                # Process function body
                while i < len(instructions) and instructions[i].op != 'FUNC_END':
                    if instructions[i].op == 'RETURN':
                        has_explicit_return = True
                    self._generate_instruction(instructions[i])
                    i += 1

                # Add epilogue only if no explicit return at end
                if not has_explicit_return or not (self.text_section and 'bx lr' in self.text_section[-1]):
                    self.text_section.append("")
                    self.text_section.append("    pop {r4, r5, r6, r7, lr}")
                    self.text_section.append("    bx lr")

                self.text_section.append("")

                self.current_function = None
                self.function_label_prefix = ""
                if 'this' in self.var_types:
                    del self.var_types['this']
            
            i += 1
    
    def _generate_instruction(self, instr: TAC):
        """Generate assembly for a single TAC instruction"""
        op = instr.op
        
        # Skip function markers and class metadata
        if op in ['FUNC_BEGIN', 'FUNC_END', 'CLASS_BEGIN', 'CLASS_END', 'FIELD', 'METHOD_ARGS']:
            return
        
        # PARAM - collect parameters for next CALL
        if op == 'PARAM':
            param_value = instr.arg1
            param_reg = self._load_value_to_register(param_value)
            self._pending_params.append(param_reg)
            return
        
        # LABEL - make unique per function
        if op == 'LABEL':
            unique_label = self._make_unique_label(instr.arg1)
            self.text_section.append(f"{unique_label}:")
            return
        
        # GOTO - use unique label
        if op == 'GOTO':
            unique_label = self._make_unique_label(instr.arg1)
            self.text_section.append(f"    b {unique_label}")
            return
        
        # IF_FALSE - conditional branch
        if op == 'IF_FALSE':
            cond_reg = self._load_value_to_register(instr.arg1)
            unique_label = self._make_unique_label(instr.result)
            self.text_section.append(f"    cmp {cond_reg}, #0")
            self.text_section.append(f"    beq {unique_label}")
            return
        
        # IF_TRUE - conditional branch
        if op == 'IF_TRUE':
            cond_reg = self._load_value_to_register(instr.arg1)
            unique_label = self._make_unique_label(instr.result)
            self.text_section.append(f"    cmp {cond_reg}, #0")
            self.text_section.append(f"    bne {unique_label}")
            return
        
        # ASSIGN - assignment
        if op == 'ASSIGN':
            src_reg = self._load_value_to_register(instr.arg1)
            self._store_to_variable(src_reg, instr.result)
            return
        
        # Arithmetic: +, -, *
        if op in ['+', '-', '*']:
            left_reg, right_reg = self._load_binop_operands(instr.arg1, instr.arg2)
            dest_reg = self._allocate_register(instr.result)
            
            if op == '+':
                self.text_section.append(f"    add {dest_reg}, {left_reg}, {right_reg}")
            elif op == '-':
                self.text_section.append(f"    sub {dest_reg}, {left_reg}, {right_reg}")
            elif op == '*':
                self.text_section.append(f"    mul {dest_reg}, {left_reg}, {right_reg}")
            return
        
        # Division - use __aeabi_idiv
        if op == '/':
            left_reg, right_reg = self._load_binop_operands(instr.arg1, instr.arg2)
            dest_reg = self._allocate_register(instr.result)
            
            # Move operands to r0, r1 for division routine
            if left_reg != 'r0':
                self.text_section.append(f"    mov r0, {left_reg}")
            if right_reg != 'r1':
                self.text_section.append(f"    mov r1, {right_reg}")
            self.text_section.append(f"    bl __aeabi_idiv")
            if dest_reg != 'r0':
                self.text_section.append(f"    mov {dest_reg}, r0")
            return
        
        # Modulo - use __aeabi_idivmod
        if op == '%':
            left_reg, right_reg = self._load_binop_operands(instr.arg1, instr.arg2)
            dest_reg = self._allocate_register(instr.result)
            
            # Move operands to r0, r1 for modulo routine
            if left_reg != 'r0':
                self.text_section.append(f"    mov r0, {left_reg}")
            if right_reg != 'r1':
                self.text_section.append(f"    mov r1, {right_reg}")
            self.text_section.append(f"    bl __aeabi_idivmod")
            # Remainder is in r1
            if dest_reg != 'r1':
                self.text_section.append(f"    mov {dest_reg}, r1")
            return
        
        # Comparison operations
        if op in ['<', '>', '<=', '>=', '==', '!=']:
            left_reg, right_reg = self._load_binop_operands(instr.arg1, instr.arg2)
            dest_reg = self._allocate_register(instr.result)
            
            self.text_section.append(f"    cmp {left_reg}, {right_reg}")
            
            if op == '<':
                self.text_section.append(f"    movlt {dest_reg}, #1")
                self.text_section.append(f"    movge {dest_reg}, #0")
            elif op == '>':
                self.text_section.append(f"    movgt {dest_reg}, #1")
                self.text_section.append(f"    movle {dest_reg}, #0")
            elif op == '<=':
                self.text_section.append(f"    movle {dest_reg}, #1")
                self.text_section.append(f"    movgt {dest_reg}, #0")
            elif op == '>=':
                self.text_section.append(f"    movge {dest_reg}, #1")
                self.text_section.append(f"    movlt {dest_reg}, #0")
            elif op == '==':
                self.text_section.append(f"    moveq {dest_reg}, #1")
                self.text_section.append(f"    movne {dest_reg}, #0")
            elif op == '!=':
                self.text_section.append(f"    movne {dest_reg}, #1")
                self.text_section.append(f"    moveq {dest_reg}, #0")
            return
        
        # Logical operations
        if op in ['&&', '||']:
            left_reg, right_reg = self._load_binop_operands(instr.arg1, instr.arg2)
            dest_reg = self._allocate_register(instr.result)
            
            if op == '&&':
                self.text_section.append(f"    and {dest_reg}, {left_reg}, {right_reg}")
            elif op == '||':
                self.text_section.append(f"    orr {dest_reg}, {left_reg}, {right_reg}")
            return
        
        # Unary operations
        if op == 'UNARY':
            operator = instr.arg1
            operand_reg = self._load_value_to_register(instr.arg2)
            dest_reg = self._allocate_register(instr.result)
            
            if operator == '-':
                self.text_section.append(f"    rsb {dest_reg}, {operand_reg}, #0")
            elif operator == '!':
                self.text_section.append(f"    cmp {operand_reg}, #0")
                self.text_section.append(f"    moveq {dest_reg}, #1")
                self.text_section.append(f"    movne {dest_reg}, #0")
            return
        
        # CALL - function call
        if op == 'CALL':
            func_name = instr.arg1
            n_args = int(instr.arg2) if instr.arg2 else 0
            
            # Move parameters to r0-r3
            for i, param_reg in enumerate(self._pending_params[:4]):
                if param_reg != f"r{i}":
                    self.text_section.append(f"    mov r{i}, {param_reg}")
            
            self._pending_params = []
            
            # Call function
            self.text_section.append(f"    bl {func_name}")
            
            # Save result if needed
            if instr.result:
                dest_reg = self._allocate_register(instr.result)
                if dest_reg != 'r0':
                    self.text_section.append(f"    mov {dest_reg}, r0")
            return
        
        # RETURN - return from function
        if op == 'RETURN':
            if instr.arg1:
                ret_reg = self._load_value_to_register(instr.arg1)
                if ret_reg != 'r0':
                    self.text_section.append(f"    mov r0, {ret_reg}")
            self.text_section.append("    pop {r4, r5, r6, r7, lr}")
            self.text_section.append("    bx lr")
            return
        
        # INDEX - array/string access
        if op == 'INDEX':
            obj_reg = self._load_value_to_register(instr.arg1)
            index_reg = self._load_value_to_register(instr.arg2)
            dest_reg = self._allocate_register(instr.result)
            self.text_section.append(f"    ldrb {dest_reg}, [{obj_reg}, {index_reg}]")
            return

        # INDEX_STORE - array element assignment: arr[index] = value
        if op == 'INDEX_STORE':
            obj_reg = self._load_value_to_register(instr.arg1)
            index_reg = self._load_value_to_register(instr.arg2)
            val_reg = self._load_value_to_register(str(instr.result))
            self.text_section.append(f"    strb {val_reg}, [{obj_reg}, {index_reg}]")
            return

        # OO operations
        if op == 'NEW_OBJECT':
            cls = str(instr.arg1)
            result = str(instr.result) if instr.result else 'r0'
            size = self.class_sizes.get(cls, 0) * 4  # 4 bytes per word
            dest_reg = self._allocate_register(result)
            self.text_section.append(f"    mov r0, #{size}  @ sizeof({cls})")
            self.text_section.append(f"    bl __minipar_malloc")
            self.text_section.append(f"    mov {dest_reg}, r0  @ {result} = new {cls}*")
            # Call constructor: r0 = this, then pending ctor args in r1-r3
            self.text_section.append(f"    mov r0, {dest_reg}  @ this")
            for idx, preg in enumerate(self._pending_params[:3]):
                self.text_section.append(f"    mov r{idx+1}, {preg}")
            self._pending_params = []
            self.text_section.append(f"    bl {cls}_ctor")
            self.text_section.append(f"    mov {dest_reg}, r0  @ ctor returns this")
            return

        if op == 'MEMBER_ACCESS':
            obj = str(instr.arg1)
            field = str(instr.arg2)
            result = str(instr.result) if instr.result else 'r0'
            cls = self.var_types.get(obj)
            offset = (self.class_layouts.get(cls, {}).get(field, 0) * 4) if cls else 0
            obj_reg = self._load_value_to_register(obj)
            dest_reg = self._allocate_register(result)
            self.text_section.append(f"    ldr {dest_reg}, [{obj_reg}, #{offset}]  @ {result} = {obj}.{field}")
            return

        if op == 'MEMBER_STORE':
            obj = str(instr.arg1)
            field = str(instr.arg2)
            value = str(instr.result) if instr.result is not None else '0'
            cls = self.var_types.get(obj)
            offset = (self.class_layouts.get(cls, {}).get(field, 0) * 4) if cls else 0
            obj_reg = self._load_value_to_register(obj)
            val_reg = self._load_value_to_register(value)
            self.text_section.append(f"    str {val_reg}, [{obj_reg}, #{offset}]  @ {obj}.{field} = {value}")
            return

        if op == 'METHOD_CALL':
            receiver = str(instr.arg1)
            method = str(instr.arg2)
            result = str(instr.result) if instr.result else None
            cls = self.var_types.get(receiver)
            if cls:
                func_name = f"{cls}_{method}"
                obj_reg = self._load_value_to_register(receiver)
                self.text_section.append(f"    mov r0, {obj_reg}  @ this")
                for idx, preg in enumerate(self._pending_params[:3]):
                    self.text_section.append(f"    mov r{idx+1}, {preg}")
                self._pending_params = []
                self.text_section.append(f"    bl {func_name}")
                if result:
                    dest_reg = self._allocate_register(result)
                    if dest_reg != 'r0':
                        self.text_section.append(f"    mov {dest_reg}, r0  @ method result")
            else:
                self.text_section.append(f"    @ METHOD_CALL unresolved: {receiver}.{method}")
                self._pending_params = []
            return

        # Other operations - comment out
        if op in ['CHANNEL_CREATE', 'SEQ_BEGIN', 'SEQ_END', 'PAR_BEGIN', 'PAR_END',
                  'THREAD_START', 'THREAD_END']:
            self.text_section.append(f"    @ {op}: not implemented in basic ARM")
            return
        
        # Unknown instruction
        self.text_section.append(f"    @ Unknown TAC: {instr}")
    
    def _make_unique_label(self, label: str) -> str:
        """Make label unique by adding function prefix"""
        if self.function_label_prefix and not label.startswith('.'):
            return f"{self.function_label_prefix}{label}"
        return label
    
    def _load_value_to_register(self, value, prefer_reg: str = None) -> str:
        """
        Load a value into a register and return the register name.
        Handles: numbers, strings, variables, temps, booleans
        """
        if value is None:
            if prefer_reg:
                self.text_section.append(f"    mov {prefer_reg}, #0")
                return prefer_reg
            return "r0"
        
        value_str = str(value)
        
        # Already a register
        if value_str.startswith('r') and value_str[1:].isdigit():
            return value_str
        
        # Check if already in register map
        if value_str in self.register_map:
            return self.register_map[value_str]
        
        # Choose target register
        target_reg = prefer_reg if prefer_reg else self._get_temp_register()
        
        # Boolean literals
        if value_str in ['true', 'True']:
            self.text_section.append(f"    mov {target_reg}, #1")
            return target_reg
        if value_str in ['false', 'False']:
            self.text_section.append(f"    mov {target_reg}, #0")
            return target_reg
        
        # Number literals
        try:
            num = int(float(value_str))
            self.text_section.append(f"    mov {target_reg}, #{num}")
            return target_reg
        except (ValueError, TypeError):
            pass
        
        # String literals - load address
        if value_str.startswith('"') and value_str.endswith('"'):
            if value_str in self.string_literals:
                label = self.string_literals[value_str]
                self.text_section.append(f"    ldr {target_reg}, ={label}")
                return target_reg
            else:
                # String not in literals, use null
                self.text_section.append(f"    mov {target_reg}, #0")
                return target_reg
        
        # Global variable - load from memory
        if value_str in self.global_vars:
            self.text_section.append(f"    ldr {target_reg}, ={value_str}")
            self.text_section.append(f"    ldr {target_reg}, [{target_reg}]")
            return target_reg
        
        # Function parameter or local - should be in register map
        if value_str in self.function_params:
            # If not in map, it's a problem, but try to handle it
            if value_str in self.register_map:
                return self.register_map[value_str]
        
        # Temporary variable - allocate register
        if value_str.startswith('t'):
            reg = self._allocate_register(value_str)
            return reg
        
        # Unknown - use as immediate or comment
        self.text_section.append(f"    @ Unknown value: {value_str}")
        self.text_section.append(f"    mov {target_reg}, #0")
        return target_reg
    
    def _store_to_variable(self, src_reg: str, var_name: str):
        """Store register value to a variable (global or local)"""
        if not var_name or var_name.startswith('t'):
            # Temporary - just update register map
            self.register_map[var_name] = src_reg
            return
        
        if var_name in self.global_vars:
            # Global variable - store to memory
            self.text_section.append(f"    ldr r1, ={var_name}")
            self.text_section.append(f"    str {src_reg}, [r1]")
        else:
            # Local variable - keep in register
            self.register_map[var_name] = src_reg
    
    def _allocate_register(self, var_name: str) -> str:
        """Allocate a register for a variable"""
        if var_name in self.register_map:
            return self.register_map[var_name]
        
        # Use r4-r7 for locals (callee-saved)
        if self.next_reg <= 7:
            reg = f"r{self.next_reg}"
            self.register_map[var_name] = reg
            self.next_reg += 1
            return reg
        
        # Out of registers, reuse r4
        return "r4"
    
    def _get_temp_register(self) -> str:
        """Get a temporary register for intermediate values"""
        # Use r0-r3 for temporaries (caller-saved)
        # r0 is safest as it's used for return values
        return "r0"

    def _load_binop_operands(self, arg1, arg2):
        """
        Load the two operands of a binary operation into *distinct* registers.

        Loading both through the default temp register (r0) would make the
        second load clobber the first (e.g. `cmp r0, r0`). We pin the left
        operand to r0 and the right one to r1 (or r2 if the left already
        resolved to r1), guaranteeing two different registers.
        """
        left_reg = self._load_value_to_register(arg1, prefer_reg='r0')
        right_prefer = 'r1' if left_reg != 'r1' else 'r2'
        right_reg = self._load_value_to_register(arg2, prefer_reg=right_prefer)
        return left_reg, right_reg
    
    def _generate_builtin_stubs(self):
        """Generate stub implementations for built-in functions"""
        self.text_section.append("@ Built-in function stubs")
        self.text_section.append("")
        
        # print function stub
        self.text_section.append("print:")
        self.text_section.append("    push {lr}")
        self.text_section.append("    @ TODO: Implement print (value in r0)")
        self.text_section.append("    @ Could use printf or write syscall")
        self.text_section.append("    pop {lr}")
        self.text_section.append("    bx lr")
        self.text_section.append("")
        
        # input function stub
        self.text_section.append("input:")
        self.text_section.append("    push {lr}")
        self.text_section.append("    @ TODO: Implement input")
        self.text_section.append("    mov r0, #0")
        self.text_section.append("    pop {lr}")
        self.text_section.append("    bx lr")
        self.text_section.append("")
        
        # Division helper (if not provided by libc)
        self.text_section.append("@ Software division helpers")
        self.text_section.append("@ These should be provided by compiler-rt or libc")
        self.text_section.append("@ If not available, link with -lgcc or provide implementations")
        self.text_section.append("")
    
    def _generate_malloc_stub(self):
        """Bump allocator: r0=size -> r0=ptr, uses __heap / __heap_ptr in .data."""
        self.text_section.append("@ OO bump allocator")
        self.text_section.append("__minipar_malloc:")
        self.text_section.append("    push {r4, r5, lr}")
        self.text_section.append("    ldr r4, =__heap_ptr")
        self.text_section.append("    ldr r5, [r4]              @ r5 = current offset")
        self.text_section.append("    add r1, r5, r0            @ r1 = new offset")
        self.text_section.append("    str r1, [r4]              @ store updated offset")
        self.text_section.append("    ldr r0, =__heap")
        self.text_section.append("    add r0, r0, r5            @ r0 = heap_base + old_offset")
        self.text_section.append("    pop {r4, r5, lr}")
        self.text_section.append("    bx lr")
        self.text_section.append("")

    def save_to_file(self, filename: str):
        """Save generated assembly to file (deprecated - use generate())"""
        pass


def generate_arm_assembly(tac_instructions: List[TAC], output_file: str = "output.s") -> str:
    """
    Generate ARM assembly from TAC instructions and save to file
    
    Args:
        tac_instructions: List of TAC instructions
        output_file: Output assembly file name
        
    Returns:
        Generated assembly code as string
    """
    generator = ARMCodeGenerator()
    asm_code = generator.generate(tac_instructions)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(asm_code)
    
    print(f"\n✓ ARM assembly generated: {output_file}")
    return asm_code
