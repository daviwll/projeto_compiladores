"""
Intermediate Code Generator for Minipar Language
Generates three-address code from AST
"""

from typing import List, Dict, Optional
try:
    from src.ast_nodes import *
except ImportError:
    from ast_nodes import *


class TAC:
    """Three-Address Code instruction"""
    def __init__(self, op: str, arg1=None, arg2=None, result=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result
    
    def __repr__(self):
        if self.op == 'CALL':
            # CALL nome_funcao n_args resultado
            return f"{self.op} {self.arg1} {self.arg2} {self.result}"
        elif self.op == 'INDEX':
            # INDEX object index result
            return f"{self.result} = {self.arg1}[{self.arg2}]"
        elif self.op == 'CHANNEL_CREATE':
            # CHANNEL_CREATE channel_type name args
            return f"{self.op} {self.arg1} {self.arg2} {{{self.result}}}"
        elif self.op == 'METHOD_CALL':
            # METHOD_CALL object method result
            return f"{self.op} {self.arg1}.{self.arg2} {self.result}"
        elif self.op in ['LABEL', 'GOTO', 'PARAM', 'RETURN', 'FUNC_BEGIN', 'FUNC_END',
                         'SEQ_BEGIN', 'SEQ_END', 'PAR_BEGIN', 'PAR_END',
                         'THREAD_START', 'THREAD_END', 'METHOD_ARGS']:
            if self.arg1:
                return f"{self.op} {self.arg1}"
            return self.op
        elif self.op in ['IF_FALSE', 'IF_TRUE']:
            return f"{self.op} {self.arg1} GOTO {self.result}"
        elif self.op == 'ASSIGN':
            return f"{self.result} = {self.arg1}"
        elif self.op == 'UNARY':
            return f"{self.result} = {self.arg1} {self.arg2}"
        elif self.arg2 is None:
            return f"{self.result} = {self.arg1}"
        else:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"


class CodeGenerator:
    def __init__(self):
        self.code: List[TAC] = []
        self.temp_count = 0
        self.label_count = 0
        self.symbol_table: Dict[str, str] = {}
        # Stack to track loop labels for break/continue
        self.loop_stack: List[tuple] = []  # [(start_label, end_label), ...]
    
    def new_temp(self) -> str:
        """Generate a new temporary variable"""
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp
    
    def new_label(self) -> str:
        """Generate a new label"""
        label = f"L{self.label_count}"
        self.label_count += 1
        return label
    
    def emit(self, op: str, arg1=None, arg2=None, result=None):
        """Emit a three-address code instruction"""
        self.code.append(TAC(op, arg1, arg2, result))
    
    def generate(self, node: ASTNode) -> Optional[str]:
        """Generate code for an AST node and return the result variable"""
        method_name = f'gen_{node.__class__.__name__}'
        method = getattr(self, method_name, self.generic_generate)
        return method(node)
    
    def generic_generate(self, node: ASTNode):
        raise NotImplementedError(f"Code generation not implemented for {node.__class__.__name__}")
    
    def gen_Program(self, node: Program) -> None:
        for decl in node.declarations:
            self.generate(decl)
    
    def gen_VarDecl(self, node: VarDecl) -> None:
        self.symbol_table[node.name] = node.type
        
        if node.initializer:
            value = self.generate(node.initializer)
            self.emit('ASSIGN', value, None, node.name)
    
    def gen_ChannelDecl(self, node: 'ChannelDecl') -> None:
        """Generate code for channel declaration"""
        # Register channel in symbol table
        self.symbol_table[node.name] = node.channel_type
        
        # Generate code for channel arguments
        arg_temps = []
        for arg in node.arguments:
            arg_temp = self.generate(arg)
            arg_temps.append(arg_temp)
        
        # Emit channel creation instruction
        # Format: CHANNEL_CREATE channel_type name arg1 arg2 arg3...
        self.emit('CHANNEL_CREATE', node.channel_type, node.name, ','.join(str(a) for a in arg_temps))
    
    def gen_FuncDecl(self, node: FuncDecl) -> None:
        self.emit('FUNC_BEGIN', node.name)
        
        for param in node.parameters:
            self.symbol_table[param.name] = param.type
            self.emit('PARAM', param.name)
        
        self.generate(node.body)
        self.emit('FUNC_END', node.name)
    
    def gen_Block(self, node: Block) -> None:
        for stmt in node.statements:
            self.generate(stmt)
    
    def gen_IfStmt(self, node: IfStmt) -> None:
        condition = self.generate(node.condition)
        
        else_label = self.new_label()
        end_label = self.new_label()
        
        if node.else_branch:
            self.emit('IF_FALSE', condition, None, else_label)
            self.generate(node.then_branch)
            self.emit('GOTO', end_label)
            self.emit('LABEL', else_label)
            self.generate(node.else_branch)
            self.emit('LABEL', end_label)
        else:
            self.emit('IF_FALSE', condition, None, else_label)
            self.generate(node.then_branch)
            self.emit('LABEL', else_label)
    
    def gen_WhileStmt(self, node: WhileStmt) -> None:
        start_label = self.new_label()
        end_label = self.new_label()

        # Push loop labels onto stack for break/continue
        self.loop_stack.append((start_label, end_label))

        self.emit('LABEL', start_label)
        condition = self.generate(node.condition)
        self.emit('IF_FALSE', condition, None, end_label)
        self.generate(node.body)
        self.emit('GOTO', start_label)
        self.emit('LABEL', end_label)

        # Pop loop labels from stack
        self.loop_stack.pop()

    def gen_ForStmt(self, node: 'ForStmt') -> None:
        """Generate code for for loop"""
        start_label = self.new_label()
        end_label = self.new_label()
        
        # Push loop labels onto stack for break/continue
        self.loop_stack.append((start_label, end_label))
        
        # Generate iterable
        iterable = self.generate(node.iterable)
        
        # Create iterator variables
        iter_var = self.new_temp()
        index_var = self.new_temp()
        length_var = self.new_temp()
        
        self.emit('ITER_CREATE', iterable, None, iter_var)
        self.emit('LIST_LEN', iterable, None, length_var)
        self.emit('ASSIGN', 0, None, index_var)
        
        # Loop start
        self.emit('LABEL', start_label)
        
        # Check if index < length
        cond_temp = self.new_temp()
        self.emit('LT', index_var, length_var, cond_temp)
        self.emit('IF_FALSE', cond_temp, None, end_label)
        
        # Get current element and assign to loop variable
        self.emit('LIST_GET', iterable, index_var, node.variable.name)
        
        # Generate loop body
        self.generate(node.body)
        
        # Increment index
        inc_temp = self.new_temp()
        self.emit('ADD', index_var, 1, inc_temp)
        self.emit('ASSIGN', inc_temp, None, index_var)
        
        self.emit('GOTO', start_label)
        self.emit('LABEL', end_label)
        
        # Pop loop labels from stack
        self.loop_stack.pop()

    def gen_ReturnStmt(self, node: ReturnStmt) -> None:
        if node.value:
            result = self.generate(node.value)
            self.emit('RETURN', result)
        else:
            self.emit('RETURN')
    
    def gen_BreakStmt(self, node: BreakStmt) -> None:
        """Generate code for break statement - jump to end of current loop"""
        if not self.loop_stack:
            raise RuntimeError("Break statement outside of loop")
        _, end_label = self.loop_stack[-1]
        self.emit('GOTO', end_label)
    
    def gen_ContinueStmt(self, node: ContinueStmt) -> None:
        """Generate code for continue statement - jump to start of current loop"""
        if not self.loop_stack:
            raise RuntimeError("Continue statement outside of loop")
        start_label, _ = self.loop_stack[-1]
        self.emit('GOTO', start_label)
    
    def gen_ExprStmt(self, node: ExprStmt) -> None:
        self.generate(node.expression)
    
    def gen_Assignment(self, node: Assignment) -> str:
        value = self.generate(node.value)
        self.emit('ASSIGN', value, None, node.name)
        return node.name
    
    def gen_BinaryOp(self, node: BinaryOp) -> str:
        left = self.generate(node.left)
        right = self.generate(node.right)
        result = self.new_temp()
        self.emit(node.operator, left, right, result)
        return result
    
    def gen_UnaryOp(self, node: UnaryOp) -> str:
        operand = self.generate(node.operand)
        result = self.new_temp()
        self.emit('UNARY', node.operator, operand, result)
        return result
    
    def gen_FuncCall(self, node: FuncCall) -> str:
        for arg in node.arguments:
            arg_result = self.generate(arg)
            self.emit('PARAM', arg_result)
        
        result = self.new_temp()
        self.emit('CALL', node.name, len(node.arguments), result)
        return result
    
    def gen_Variable(self, node: Variable) -> str:
        return node.name
    
    def gen_NumberLiteral(self, node: NumberLiteral) -> str:
        return str(node.value)
    
    def gen_StringLiteral(self, node: StringLiteral) -> str:
        return f'"{node.value}"'
    
    def gen_BoolLiteral(self, node: BoolLiteral) -> str:
        return str(node.value).lower()

    def gen_ListLiteral(self, node: 'ListLiteral') -> str:
        """Generate code for list literal"""
        # Generate code for each element
        result = self.new_temp()
        self.emit('LIST_CREATE', result)
        
        for elem in node.elements:
            elem_result = self.generate(elem)
            self.emit('LIST_APPEND', result, elem_result)
        
        return result

    def gen_ListComprehension(self, node: 'ListComprehension') -> str:
        """Generate code for list comprehension"""
        result = self.new_temp()
        self.emit('LIST_CREATE', None, None, result)
        
        # Generate iterable
        iterable = self.generate(node.iterable)
        
        # Create loop
        loop_start = self.new_label()
        loop_end = self.new_label()
        iter_var = self.new_temp()
        
        self.emit('ITER_CREATE', iterable, None, iter_var)
        self.emit('LABEL', loop_start)
        cond_temp = self.new_temp()
        self.emit('ITER_HASNEXT', iter_var, None, cond_temp)
        self.emit('IF_FALSE', cond_temp, None, loop_end)
        
        # Get next value and assign to loop variable
        self.emit('ITER_NEXT', iter_var, None, node.variable.name)
        
        # Generate expression and append to result list
        expr_result = self.generate(node.expression)
        self.emit('LIST_APPEND', result, expr_result)
        
        self.emit('GOTO', loop_start)
        self.emit('LABEL', loop_end)
        
        return result

    def gen_DictLiteral(self, node: 'DictLiteral') -> str:
        """Generate code for dictionary literal"""
        result = self.new_temp()
        self.emit('DICT_CREATE', result)
        
        for key, value in node.pairs:
            key_result = self.generate(key)
            value_result = self.generate(value)
            self.emit('DICT_SET', result, key_result, value_result)
        
        return result

    def gen_SeqBlock(self, node: 'SeqBlock') -> None:
        """Generate code for SEQ block - sequential execution (default behavior)"""
        self.emit('SEQ_BEGIN')
        for stmt in node.statements:
            self.generate(stmt)
        self.emit('SEQ_END')
    
    def gen_ParBlock(self, node: 'ParBlock') -> None:
        """Generate code for PAR block - parallel execution with threads"""
        self.emit('PAR_BEGIN')
        for i, stmt in enumerate(node.statements):
            # Each statement in PAR block will be executed in a separate thread
            self.emit('THREAD_START', i)
            self.generate(stmt)
            self.emit('THREAD_END', i)
        self.emit('PAR_END')
    
    def gen_MethodCall(self, node: 'MethodCall') -> str:
        """Generate code for method call - obj.method(args)"""
        # Generate code for arguments
        for arg in node.arguments:
            arg_result = self.generate(arg)
            self.emit('PARAM', arg_result)

        # Generate method call instruction
        result = self.new_temp()
        self.emit('METHOD_CALL', node.object, node.method, result)
        self.emit('METHOD_ARGS', len(node.arguments))
        return result

    def gen_IndexAccess(self, node: 'IndexAccess') -> str:
        """Generate code for index access - arr[index]"""
        obj = self.generate(node.object)
        index = self.generate(node.index)
        result = self.new_temp()
        self.emit('INDEX', obj, index, result)
        return result

    def gen_SliceAccess(self, node: 'SliceAccess') -> str:
        """Generate code for slice access - arr[start:end]"""
        obj = self.generate(node.object)
        
        # Generate start index (or None for beginning)
        if node.start:
            start = self.generate(node.start)
        else:
            start = 'None'
        
        # Generate end index (or None for end)
        if node.end:
            end = self.generate(node.end)
        else:
            end = 'None'
        
        result = self.new_temp()
        # Encode slice as SLICE obj start:end result
        self.emit('SLICE', f"{obj}[{start}:{end}]", None, result)
        return result

    def print_code(self):
        """Print the generated three-address code"""
        print("\n=== Three-Address Code ===")
        for i, instruction in enumerate(self.code):
            print(f"{i:3d}: {instruction}")
    
    def get_code(self) -> List[TAC]:
        """Return the generated code"""
        return self.code
