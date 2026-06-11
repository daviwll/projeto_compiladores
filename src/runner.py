"""
Minipar Runtime Executor
Executes Minipar programs with support for channels, parallel execution, and more
"""

import socket
import threading
import time
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

try:
    from src.ast_nodes import *
    from src.lexer import Lexer
    from src.parser import Parser
    from src.semantic import SemanticAnalyzer
except ImportError:
    from ast_nodes import *
    from lexer import Lexer
    from parser import Parser
    from semantic import SemanticAnalyzer


class BreakException(Exception):
    """Raised when break statement is executed"""
    pass


class ContinueException(Exception):
    """Raised when continue statement is executed"""
    pass


class ReturnException(Exception):
    """Raised when return statement is executed"""
    def __init__(self, value=None):
        self.value = value
        super().__init__()


class VariableTable:
    """Variable scope management"""
    def __init__(self, parent=None):
        self.table: Dict[str, Any] = {}
        self.parent = parent
    
    def get(self, name: str) -> Any:
        """Get variable value, checking parent scopes"""
        if name in self.table:
            return self.table[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise NameError(f"Variable '{name}' not defined")
    
    def set(self, name: str, value: Any):
        """Set variable in current or parent scope"""
        if name in self.table or self.parent is None:
            self.table[name] = value
        else:
            # Try to find in parent scopes
            try:
                self.parent.get(name)
                self.parent.set(name, value)
            except NameError:
                # Not in parent, create in current scope
                self.table[name] = value
    
    def define(self, name: str, value: Any):
        """Define new variable in current scope"""
        self.table[name] = value


class MiniparRunner:
    """Main runtime executor for Minipar programs"""
    
    def __init__(self):
        self.global_scope = VariableTable()
        self.current_scope = self.global_scope
        self.functions: Dict[str, FuncDecl] = {}
        self.channels: Dict[str, socket.socket] = {}
        self.servers: Dict[str, threading.Thread] = {}
        
        # Built-in functions
        self.builtins = {
            'print': self._builtin_print,
            'input': self._builtin_input,
            'to_string': str,
            'to_number': lambda x: int(x) if isinstance(x, str) else x,
            'to_bool': bool,
            'len': len,
        }
    
    def run_file(self, filename: str):
        """Run a Minipar source file"""
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        return self.run_source(source)
    
    def run_source(self, source: str):
        """Run Minipar source code"""
        # Compile
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        semantic = SemanticAnalyzer()
        if not semantic.analyze(ast):
            raise Exception("Semantic errors found")
        
        # Execute
        return self.execute(ast)
    
    def execute(self, node: ASTNode) -> Any:
        """Execute an AST node"""
        method_name = f'exec_{type(node).__name__}'
        method = getattr(self, method_name, None)
        
        if method:
            return method(node)
        else:
            raise NotImplementedError(f"Execution for {type(node).__name__} not implemented")
    
    def enter_scope(self):
        """Enter a new scope"""
        self.current_scope = VariableTable(parent=self.current_scope)
    
    def exit_scope(self):
        """Exit current scope"""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    # Built-in functions
    def _builtin_print(self, *args):
        """Built-in print function"""
        print(*args)
        return None
    
    def _builtin_input(self, prompt=""):
        """Built-in input function"""
        return input(prompt)
    
    # Execution methods for each AST node type
    
    def exec_Program(self, node: Program) -> Any:
        """Execute program"""
        result = None
        for decl in node.declarations:
            result = self.execute(decl)
        return result
    
    def exec_VarDecl(self, node: VarDecl) -> Any:
        """Execute variable declaration"""
        if node.initializer:
            value = self.execute(node.initializer)
        else:
            # Initialize with default values based on type
            if node.type == "number":
                value = 0
            elif node.type == "string":
                value = ""
            elif node.type == "bool":
                value = False
            else:
                value = None
        
        self.current_scope.define(node.name, value)
        return value
    
    def exec_FuncDecl(self, node: FuncDecl) -> Any:
        """Register function declaration"""
        self.functions[node.name] = node
        return None
    
    def exec_Assignment(self, node: Assignment) -> Any:
        """Execute assignment"""
        value = self.execute(node.value)
        self.current_scope.set(node.name, value)
        return value
    
    def exec_IfStmt(self, node: IfStmt) -> Any:
        """Execute if statement"""
        condition = self.execute(node.condition)
        
        if condition:
            self.execute(node.then_branch)
        elif node.else_branch:
            self.execute(node.else_branch)
        
        return None
    
    def exec_WhileStmt(self, node: WhileStmt) -> Any:
        """Execute while loop"""
        while self.execute(node.condition):
            try:
                self.execute(node.body)
            except BreakException:
                break
            except ContinueException:
                continue

        return None

    def exec_ForStmt(self, node: 'ForStmt') -> Any:
        """Execute for loop"""
        iterable = self.execute(node.iterable)
        
        # Check if iterable is valid
        if not isinstance(iterable, (list, str)):
            raise TypeError(f"Cannot iterate over {type(iterable).__name__}")
        
        # Enter new scope for loop variable
        self.enter_scope()
        
        try:
            for item in iterable:
                # Assign loop variable
                self.current_scope.set(node.variable.name, item)
                
                try:
                    self.execute(node.body)
                except BreakException:
                    break
                except ContinueException:
                    continue
        finally:
            self.exit_scope()
        
        return None

    def exec_BreakStmt(self, node: BreakStmt) -> Any:
        """Execute break statement"""
        raise BreakException()
    
    def exec_ContinueStmt(self, node: ContinueStmt) -> Any:
        """Execute continue statement"""
        raise ContinueException()
    
    def exec_Block(self, node: Block) -> Any:
        """Execute block of statements"""
        self.enter_scope()
        try:
            result = None
            for stmt in node.statements:
                result = self.execute(stmt)
            return result
        finally:
            self.exit_scope()
    
    def exec_ReturnStmt(self, node: ReturnStmt) -> Any:
        """Execute return statement"""
        value = self.execute(node.value) if node.value else None
        raise ReturnException(value)
    
    def exec_ExprStmt(self, node: ExprStmt) -> Any:
        """Execute expression statement"""
        return self.execute(node.expression)
    
    def exec_FuncCall(self, node: FuncCall) -> Any:
        """Execute function call"""
        func_name = node.name
        
        # Check if it's a built-in function
        if func_name in self.builtins:
            args = [self.execute(arg) for arg in node.arguments]
            return self.builtins[func_name](*args)
        
        # Check if it's a user-defined function
        if func_name not in self.functions:
            raise NameError(f"Function '{func_name}' not defined")
        
        func = self.functions[func_name]
        
        # Create new scope for function
        self.enter_scope()
        
        try:
            # Bind parameters
            for param, arg in zip(func.parameters, node.arguments):
                arg_value = self.execute(arg)
                self.current_scope.define(param.name, arg_value)
            
            # Execute function body (which is a Block)
            result = self.execute(func.body)
            
            return result
        
        except ReturnException as ret:
            return ret.value
        finally:
            self.exit_scope()
    
    def exec_BinaryOp(self, node: BinaryOp) -> Any:
        """Execute binary operation"""
        left = self.execute(node.left)
        right = self.execute(node.right)

        op = node.operator

        # Arithmetic
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            # Check for division by zero
            if right == 0:
                raise ZeroDivisionError(f"Division by zero in expression")
            return left / right
        elif op == '%':
            # Check for modulo by zero
            if right == 0:
                raise ZeroDivisionError(f"Modulo by zero in expression")
            return left % right

        # Comparison
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<':
            return left < right
        elif op == '>':
            return left > right
        elif op == '<=':
            return left <= right
        elif op == '>=':
            return left >= right

        # Logical
        elif op == '&&':
            return left and right
        elif op == '||':
            return left or right

        else:
            raise ValueError(f"Unknown operator: {op}")
    
    def exec_UnaryOp(self, node: UnaryOp) -> Any:
        """Execute unary operation"""
        operand = self.execute(node.operand)
        
        if node.operator == '-':
            return -operand
        elif node.operator == '!':
            return not operand
        else:
            raise ValueError(f"Unknown unary operator: {node.operator}")
    
    def exec_Variable(self, node: Variable) -> Any:
        """Get variable value"""
        return self.current_scope.get(node.name)
    
    def exec_NumberLiteral(self, node: NumberLiteral) -> Any:
        """Return number literal value"""
        return node.value
    
    def exec_StringLiteral(self, node: StringLiteral) -> Any:
        """Return string literal value"""
        return node.value
    
    def exec_BoolLiteral(self, node: BoolLiteral) -> Any:
        """Return boolean literal value"""
        return node.value

    def exec_ListLiteral(self, node: 'ListLiteral') -> Any:
        """Execute list literal"""
        result = []
        for elem in node.elements:
            result.append(self.execute(elem))
        return result

    def exec_ListComprehension(self, node: 'ListComprehension') -> Any:
        """Execute list comprehension"""
        result = []
        iterable = self.execute(node.iterable)
        
        # Enter new scope for loop variable
        self.enter_scope()
        
        try:
            for item in iterable:
                # Assign loop variable
                self.current_scope.set(node.variable.name, item)
                # Evaluate expression and append to result
                value = self.execute(node.expression)
                result.append(value)
        finally:
            self.exit_scope()
        
        return result

    def exec_DictLiteral(self, node: 'DictLiteral') -> Any:
        """Execute dictionary literal"""
        result = {}
        for key_node, value_node in node.pairs:
            key = self.execute(key_node)
            value = self.execute(value_node)
            result[key] = value
        return result

    def exec_IndexAccess(self, node: 'IndexAccess') -> Any:
        """Execute index access (array/string indexing)"""
        obj = self.execute(node.object)
        index = self.execute(node.index)

        # Convert index to integer
        try:
            index = int(index)
        except (ValueError, TypeError):
            raise TypeError(f"Index must be a number, got {type(index).__name__}")

        # Handle string indexing
        if isinstance(obj, str):
            if index < 0 or index >= len(obj):
                raise IndexError(f"String index out of range: {index}")
            return obj[index]

        # Handle list indexing (if lists are supported)
        if isinstance(obj, list):
            if index < 0 or index >= len(obj):
                raise IndexError(f"List index out of range: {index}")
            return obj[index]

        raise TypeError(f"Cannot index object of type {type(obj).__name__}")

    def exec_SliceAccess(self, node: 'SliceAccess') -> Any:
        """Execute slice access (array/string slicing)"""
        obj = self.execute(node.object)
        
        # Get start index
        if node.start:
            start = self.execute(node.start)
            try:
                start = int(start)
            except (ValueError, TypeError):
                raise TypeError(f"Slice start must be a number, got {type(start).__name__}")
        else:
            start = None
        
        # Get end index
        if node.end:
            end = self.execute(node.end)
            try:
                end = int(end)
            except (ValueError, TypeError):
                raise TypeError(f"Slice end must be a number, got {type(end).__name__}")
        else:
            end = None
        
        # Perform slicing
        if isinstance(obj, (str, list)):
            return obj[start:end]
        
        raise TypeError(f"Cannot slice object of type {type(obj).__name__}")

    def exec_ParBlock(self, node: ParBlock) -> Any:
        """Execute parallel block using threads"""
        # For now, execute statements sequentially
        # True parallelism would require thread-safe variable tables
        for stmt in node.statements:
            self.execute(stmt)
        return None
    
    def exec_SeqBlock(self, node: SeqBlock) -> Any:
        """Execute sequential block"""
        for stmt in node.statements:
            self.execute(stmt)
        return None
    
    def exec_ChannelDecl(self, node: ChannelDecl) -> Any:
        """Execute channel declaration"""
        if node.channel_type == 's_channel':
            return self._create_server_channel(node)
        elif node.channel_type == 'c_channel':
            return self._create_client_channel(node)
        else:
            raise ValueError(f"Unknown channel type: {node.channel_type}")
    
    def _create_server_channel(self, node: ChannelDecl) -> Any:
        """Create server channel (socket server)"""
        # Parse arguments: {func_name, description, host, port}
        args = node.arguments
        
        if len(args) < 4:
            raise ValueError("Server channel requires: function, description, host, port")
        
        func_name = self.execute(args[0]) if not isinstance(args[0], Variable) else args[0].name
        description = self.execute(args[1])
        host = self.execute(args[2])
        port = self.execute(args[3])
        
        # Get the function
        if func_name not in self.functions:
            raise NameError(f"Function '{func_name}' not found for server channel")
        
        func = self.functions[func_name]
        
        # Start server in a separate thread
        def run_server():
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                server.bind((host, int(port)))
                server.listen(5)
                print(f"✓ Server '{node.name}' started on {host}:{port}")
                print(f"  Description: {description}")
                
                while True:
                    try:
                        conn, addr = server.accept()
                        print(f"  Client connected from {addr}")
                        
                        # Handle client in new thread
                        client_thread = threading.Thread(
                            target=self._handle_client,
                            args=(conn, func, description)
                        )
                        client_thread.daemon = True
                        client_thread.start()
                        
                    except KeyboardInterrupt:
                        print(f"\n✓ Server '{node.name}' shutting down...")
                        break
                    except Exception as e:
                        print(f"  Error accepting connection: {e}")
            
            finally:
                server.close()
        
        # Start server thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        self.servers[node.name] = server_thread
        
        # Give server time to start
        time.sleep(0.5)
        
        return None
    
    def _handle_client(self, conn: socket.socket, func: FuncDecl, description: str):
        """Handle client connection on server"""
        try:
            # Send description
            conn.send(description.encode('utf-8'))
            
            while True:
                # Receive data
                data = conn.recv(4096).decode('utf-8')
                if not data:
                    break
                
                print(f"  Received: {data}")
                
                # Parse the data (expecting comma-separated values)
                args_str = data.strip().split(',')
                
                # Create function call
                self.enter_scope()
                try:
                    # Bind parameters
                    for param, arg_str in zip(func.parameters, args_str):
                        # Try to convert to number if possible
                        try:
                            value = float(arg_str) if '.' in arg_str else int(arg_str)
                        except ValueError:
                            value = arg_str.strip()
                        
                        self.current_scope.define(param.name, value)
                    
                    # Execute function body
                    result = self.execute(func.body)
                    
                    # Send result back
                    response = str(result) if result is not None else "OK"
                    conn.send(response.encode('utf-8'))
                    print(f"  Sent: {response}")
                
                except ReturnException as ret:
                    response = str(ret.value) if ret.value is not None else "OK"
                    conn.send(response.encode('utf-8'))
                    print(f"  Sent: {response}")
                
                finally:
                    self.exit_scope()
        
        except Exception as e:
            print(f"  Error handling client: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            print("  Client disconnected")
            conn.close()
    
    def _create_client_channel(self, node: ChannelDecl) -> Any:
        """Create client channel (socket client)"""
        # Parse arguments: {host, port}
        args = node.arguments

        if len(args) < 2:
            raise ValueError("Client channel requires: host, port")

        host = self.execute(args[0])
        port = self.execute(args[1])

        # Create socket and connect
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client.connect((host, int(port)))
            print(f"✓ Client '{node.name}' connected to {host}:{port}")

            # Receive welcome message
            welcome = client.recv(4096).decode('utf-8')
            print(f"  Server says: {welcome}")

            # Store connection
            self.channels[node.name] = client

        except ConnectionRefusedError:
            print(f"✗ Failed to connect client '{node.name}': Connection refused")
            print(f"  Make sure a server is running on {host}:{port}")
            print(f"  Hint: Start the server program in another terminal first!")
            raise ConnectionRefusedError(f"No server running on {host}:{port}. Start the server first!")
        except Exception as e:
            print(f"✗ Failed to connect client '{node.name}': {e}")
            raise

        return None
    
    def exec_MethodCall(self, node: MethodCall) -> Any:
        """Execute method call (e.g., channel.send(), list.append(), str.split())"""
        obj_ref = node.object
        if isinstance(obj_ref, Variable):
            obj_name = obj_ref.name
        elif isinstance(obj_ref, str):
            obj_name = obj_ref
        else:
            obj_name = None
        method_name = node.method

        # Check if it's a channel method
        if obj_name and obj_name in self.channels:
            conn = self.channels[obj_name]

            if method_name == 'send':
                # Send data to server
                args = [self.execute(arg) for arg in node.arguments]
                message = ','.join(str(arg) for arg in args)

                conn.send(message.encode('utf-8'))
                print(f"  Sent to server: {message}")

                # Receive response
                response = conn.recv(4096).decode('utf-8')
                print(f"  Received from server: {response}")

                # Try to convert response to number
                try:
                    return float(response) if '.' in response else int(response)
                except ValueError:
                    return response

            elif method_name == 'close':
                # Close connection
                conn.close()
                del self.channels[obj_name]
                print(f"✓ Connection '{obj_name}' closed")
                return None

            else:
                raise ValueError(f"Unknown channel method: {method_name}")

        # Get the object
        if obj_name is not None:
            obj = self.current_scope.get(obj_name)
        else:
            obj = self.execute(obj_ref)
        if obj is None:
            raise NameError(f"Object '{obj_name}' not found")

        # List methods
        if isinstance(obj, list):
            if method_name == 'append':
                if len(node.arguments) != 1:
                    raise TypeError(f"append() takes exactly 1 argument")
                value = self.execute(node.arguments[0])
                obj.append(value)
                return None
            
            elif method_name == 'pop':
                if len(node.arguments) == 0:
                    return obj.pop() if obj else None
                elif len(node.arguments) == 1:
                    index = int(self.execute(node.arguments[0]))
                    return obj.pop(index)
                else:
                    raise TypeError(f"pop() takes at most 1 argument")
            
            elif method_name == 'insert':
                if len(node.arguments) != 2:
                    raise TypeError(f"insert() takes exactly 2 arguments")
                index = int(self.execute(node.arguments[0]))
                value = self.execute(node.arguments[1])
                obj.insert(index, value)
                return None
            
            elif method_name == 'remove':
                if len(node.arguments) != 1:
                    raise TypeError(f"remove() takes exactly 1 argument")
                value = self.execute(node.arguments[0])
                obj.remove(value)
                return None
            
            elif method_name == 'sort':
                if len(node.arguments) != 0:
                    raise TypeError(f"sort() takes no arguments")
                obj.sort()
                return None
            
            else:
                raise AttributeError(f"List has no method '{method_name}'")

        # String methods
        elif isinstance(obj, str):
            if method_name == 'strip':
                return obj.strip()
            elif method_name == 'lstrip':
                return obj.lstrip()
            elif method_name == 'rstrip':
                return obj.rstrip()
            elif method_name == 'lower':
                return obj.lower()
            elif method_name == 'upper':
                return obj.upper()
            elif method_name == 'split':
                if len(node.arguments) == 0:
                    return obj.split()
                elif len(node.arguments) == 1:
                    sep = self.execute(node.arguments[0])
                    return obj.split(sep)
                else:
                    raise TypeError(f"split() takes at most 1 argument")
            elif method_name == 'replace':
                if len(node.arguments) != 2:
                    raise TypeError(f"replace() takes exactly 2 arguments")
                old = self.execute(node.arguments[0])
                new = self.execute(node.arguments[1])
                return obj.replace(old, new)
            elif method_name == 'startswith':
                if len(node.arguments) != 1:
                    raise TypeError(f"startswith() takes exactly 1 argument")
                prefix = self.execute(node.arguments[0])
                return obj.startswith(prefix)
            elif method_name == 'endswith':
                if len(node.arguments) != 1:
                    raise TypeError(f"endswith() takes exactly 1 argument")
                suffix = self.execute(node.arguments[0])
                return obj.endswith(suffix)
            elif method_name == 'to_number':
                try:
                    if '.' in obj:
                        return float(obj)
                    else:
                        return int(obj)
                except ValueError:
                    raise ValueError(f"Cannot convert '{obj}' to number")
            else:
                raise AttributeError(f"String has no method '{method_name}'")

        else:
            raise TypeError(f"Object of type {type(obj).__name__} has no methods")

    def cleanup(self):
        """Clean up resources"""
        # Close all channels
        for name, conn in list(self.channels.items()):
            try:
                conn.close()
            except:
                pass
        
        self.channels.clear()
        print("\n[OK] Runtime cleanup complete")



def main():
    """Command-line interface for runner"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Minipar Runtime Executor")
    parser.add_argument("file", help="Minipar source file to execute")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    args = parser.parse_args()
    
    runner = MiniparRunner()
    
    try:
        print(f"\n{'='*60}")
        print(f"Executing: {args.file}")
        print(f"{'='*60}\n")
        
        runner.run_file(args.file)
        
        # Keep main thread alive if there are server threads
        if runner.servers:
            print("\n[Server running - Press Ctrl+C to stop]")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\nShutting down...")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    except Exception as e:
        print(f"\n✗ Runtime Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    finally:
        runner.cleanup()


if __name__ == '__main__':
    main()
