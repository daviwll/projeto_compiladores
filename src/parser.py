"""
Parser for Minipar Language
Performs syntax analysis and builds an Abstract Syntax Tree (AST)
"""

from typing import List, Optional
try:
    from src.lexer import Token, TokenType, Lexer
    from src.ast_nodes import *
except ImportError:
    from lexer import Token, TokenType, Lexer
    from ast_nodes import *


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    
    def current(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]
    
    def peek(self, offset: int = 0) -> Token:
        pos = self.pos + offset
        return self.tokens[pos] if pos < len(self.tokens) else self.tokens[-1]
    
    def advance(self) -> Token:
        token = self.current()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token
    
    def match(self, *types: TokenType) -> bool:
        return self.current().type in types
    
    def consume(self, token_type: TokenType, msg: str = None) -> Token:
        if not self.match(token_type):
            msg = msg or f"Expected {token_type.name}"
            self.error(msg)
        return self.advance()
    
    def error(self, msg: str):
        token = self.current()
        raise SyntaxError(f"Parser error at {token.line}:{token.column}: {msg}")
    
    
    def parse(self) -> Program:
        declarations = []
        while not self.match(TokenType.EOF):
            declarations.append(self.declaration())
        return Program(declarations)
    
    def declaration(self) -> ASTNode:
        if self.match(TokenType.FUNC):
            return self.func_declaration()
        elif self.match(TokenType.VAR):
            return self.var_declaration()
        elif self.match(TokenType.CLASS):
            return self.class_declaration()
        elif self.match(TokenType.S_CHANNEL, TokenType.C_CHANNEL):
            return self.channel_declaration()
        elif self.match(TokenType.SEQ):
            return self.seq_block()
        elif self.match(TokenType.PAR):
            return self.par_block()
        else:
            # Could be a statement (function call, assignment, etc.)
            return self.statement()
    
    def func_declaration(self) -> FuncDecl:
        self.consume(TokenType.FUNC)
        name = self.consume(TokenType.IDENTIFIER, "Expected function name").value
        
        self.consume(TokenType.LPAREN)
        parameters = []
        
        if not self.match(TokenType.RPAREN):
            parameters.append(self.parameter())
            while self.match(TokenType.COMMA):
                self.advance()
                parameters.append(self.parameter())
        
        self.consume(TokenType.RPAREN)
        
        # Expect arrow and return type
        self.consume(TokenType.ARROW, "Expected '->' after parameter list")
        return_type = self.type_specifier()
        
        body = self.block()
        
        return FuncDecl(return_type, name, parameters, body)
    
    def parameter(self) -> VarDecl:
        name = self.consume(TokenType.IDENTIFIER, "Expected parameter name").value
        self.consume(TokenType.COLON, "Expected ':' after parameter name")
        param_type = self.type_specifier()
        
        # Optional default value
        initializer = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            initializer = self.expression()
        
        return VarDecl(param_type, name, initializer)
    
    def var_declaration(self) -> VarDecl:
        self.consume(TokenType.VAR, "Expected 'var' keyword")
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.COLON, "Expected ':' after variable name")
        var_type = self.type_specifier()
        
        initializer = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            initializer = self.expression()
        
        # Semicolon is now optional
        if self.match(TokenType.SEMICOLON):
            self.advance()
        
        return VarDecl(var_type, name, initializer)
    
    def channel_declaration(self) -> 'ChannelDecl':
        """Parse channel declaration: s_channel name {args} or c_channel name {args}"""
        channel_type = 's_channel' if self.match(TokenType.S_CHANNEL) else 'c_channel'
        self.advance()
        
        name = self.consume(TokenType.IDENTIFIER, "Expected channel name").value
        
        self.consume(TokenType.LBRACE, "Expected '{' after channel name")
        
        # Parse arguments (comma-separated expressions)
        arguments = []
        if not self.match(TokenType.RBRACE):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                self.advance()
                arguments.append(self.expression())
        
        self.consume(TokenType.RBRACE, "Expected '}' after channel arguments")
        
        # Semicolon is optional
        if self.match(TokenType.SEMICOLON):
            self.advance()
        
        return ChannelDecl(channel_type, name, arguments)

    def class_declaration(self) -> 'ClassDecl':
        self.consume(TokenType.CLASS, "Expected 'class' keyword")
        name = self.consume(TokenType.IDENTIFIER, "Expected class name").value

        base_class = None
        if self.match(TokenType.EXTENDS):
            self.advance()
            base_class = self.consume(TokenType.IDENTIFIER, "Expected base class name").value

        self.consume(TokenType.LBRACE, "Expected '{' after class header")

        fields = []
        methods = []
        while not self.match(TokenType.RBRACE) and not self.match(TokenType.EOF):
            if self.match(TokenType.VAR):
                fields.append(self.class_field_declaration())
            elif self.match(TokenType.FUNC):
                methods.append(self.class_method_declaration(name))
            elif self.match(TokenType.CONSTRUCTOR):
                methods.append(self.constructor_declaration(name))
            else:
                self.error("Expected class member declaration")

        self.consume(TokenType.RBRACE, "Expected '}' after class body")
        return ClassDecl(name, base_class, fields, methods)

    def class_field_declaration(self) -> 'FieldDecl':
        self.consume(TokenType.VAR, "Expected 'var' in class field declaration")
        name = self.consume(TokenType.IDENTIFIER, "Expected field name").value
        self.consume(TokenType.COLON, "Expected ':' after field name")
        field_type = self.type_specifier()

        initializer = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            initializer = self.expression()

        if self.match(TokenType.SEMICOLON):
            self.advance()

        return FieldDecl(field_type, name, initializer)

    def class_method_declaration(self, class_name: str) -> ASTNode:
        method = self.func_declaration()
        if method.name == class_name and method.return_type == 'void':
            return ConstructorDecl(method.name, method.parameters, method.body)
        return MethodDecl(method.return_type, method.name, method.parameters, method.body)

    def constructor_declaration(self, class_name: str) -> 'ConstructorDecl':
        self.consume(TokenType.CONSTRUCTOR, "Expected 'constructor' keyword")
        self.consume(TokenType.LPAREN, "Expected '(' after constructor keyword")

        parameters = []
        if not self.match(TokenType.RPAREN):
            parameters.append(self.parameter())
            while self.match(TokenType.COMMA):
                self.advance()
                parameters.append(self.parameter())

        self.consume(TokenType.RPAREN)
        body = self.block()
        return ConstructorDecl(class_name, parameters, body)
    
    def type_specifier(self) -> str:
        if self.match(TokenType.NUMBER):
            self.advance()
            return 'number'
        elif self.match(TokenType.STRING):
            self.advance()
            return 'string'
        elif self.match(TokenType.BOOL):
            self.advance()
            return 'bool'
        elif self.match(TokenType.VOID):
            self.advance()
            return 'void'
        elif self.match(TokenType.C_CHANNEL):
            self.advance()
            return 'c_channel'
        elif self.match(TokenType.S_CHANNEL):
            self.advance()
            return 's_channel'
        elif self.match(TokenType.LIST):
            self.advance()
            return 'list'
        elif self.match(TokenType.DICT):
            self.advance()
            return 'dict'
        elif self.match(TokenType.ANY):
            self.advance()
            return 'any'
        elif self.match(TokenType.IDENTIFIER):
            return self.advance().value
        else:
            self.error("Expected type specifier")
    
    def block(self) -> Block:
        self.consume(TokenType.LBRACE)
        statements = []
        
        while not self.match(TokenType.RBRACE) and not self.match(TokenType.EOF):
            statements.append(self.statement())
        
        self.consume(TokenType.RBRACE)
        return Block(statements)
    
    def statement(self) -> ASTNode:
        if self.match(TokenType.IF):
            return self.if_statement()
        elif self.match(TokenType.WHILE):
            return self.while_statement()
        elif self.match(TokenType.FOR):
            return self.for_statement()
        elif self.match(TokenType.SEQ):
            return self.seq_block()
        elif self.match(TokenType.PAR):
            return self.par_block()
        elif self.match(TokenType.RETURN):
            return self.return_statement()
        elif self.match(TokenType.BREAK):
            return self.break_statement()
        elif self.match(TokenType.CONTINUE):
            return self.continue_statement()
        elif self.match(TokenType.LBRACE):
            return self.block()
        elif self.match(TokenType.VAR):
            return self.var_declaration()
        elif self.match(TokenType.FUNC):
            return self.func_declaration()
        else:
            return self.expression_statement()
    
    def if_statement(self) -> IfStmt:
        self.consume(TokenType.IF)
        self.consume(TokenType.LPAREN)
        condition = self.expression()
        self.consume(TokenType.RPAREN)
        
        then_branch = self.statement()
        else_branch = None
        
        if self.match(TokenType.ELSE):
            self.advance()
            else_branch = self.statement()
        
        return IfStmt(condition, then_branch, else_branch)
    
    def while_statement(self) -> WhileStmt:
        self.consume(TokenType.WHILE)
        self.consume(TokenType.LPAREN)
        condition = self.expression()
        self.consume(TokenType.RPAREN)
        body = self.statement()

        return WhileStmt(condition, body)

    def for_statement(self) -> ForStmt:
        """Parse for loop: for (var x: type in iterable) { body }"""
        self.consume(TokenType.FOR)
        self.consume(TokenType.LPAREN)
        
        # Parse loop variable declaration: var x: type
        self.consume(TokenType.VAR, "Expected 'var' in for loop")
        var_name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.COLON, "Expected ':' after variable name")
        var_type = self.type_specifier()
        
        # Create variable declaration
        variable = VarDecl(var_type, var_name, None)
        
        # Parse 'in' keyword
        self.consume(TokenType.IN, "Expected 'in' after variable declaration")
        
        # Parse iterable expression
        iterable = self.expression()
        
        self.consume(TokenType.RPAREN, "Expected ')' after for header")
        
        # Parse loop body
        body = self.statement()
        
        return ForStmt(variable, iterable, body)

    def return_statement(self) -> ReturnStmt:
        self.consume(TokenType.RETURN)
        value = None
        
        if not self.match(TokenType.SEMICOLON) and not self.match(TokenType.RBRACE):
            value = self.expression()
        
        # Semicolon is optional
        if self.match(TokenType.SEMICOLON):
            self.advance()
        
        return ReturnStmt(value)
    
    def break_statement(self) -> BreakStmt:
        self.consume(TokenType.BREAK)
        # Semicolon is optional
        if self.match(TokenType.SEMICOLON):
            self.advance()
        return BreakStmt()
    
    def continue_statement(self) -> ContinueStmt:
        self.consume(TokenType.CONTINUE)
        # Semicolon is optional
        if self.match(TokenType.SEMICOLON):
            self.advance()
        return ContinueStmt()
    
    def seq_block(self) -> 'SeqBlock':
        """Parse SEQ { stmts } - sequential execution block"""
        self.consume(TokenType.SEQ)
        self.consume(TokenType.LBRACE)
        
        statements = []
        while not self.match(TokenType.RBRACE) and not self.match(TokenType.EOF):
            statements.append(self.statement())
        
        self.consume(TokenType.RBRACE)
        return SeqBlock(statements)
    
    def par_block(self) -> 'ParBlock':
        """Parse PAR { stmts } - parallel execution block"""
        self.consume(TokenType.PAR)
        self.consume(TokenType.LBRACE)
        
        statements = []
        while not self.match(TokenType.RBRACE) and not self.match(TokenType.EOF):
            statements.append(self.statement())
        
        self.consume(TokenType.RBRACE)
        return ParBlock(statements)
    
    def expression_statement(self) -> ExprStmt:
        expr = self.expression()
        # Semicolon is optional
        if self.match(TokenType.SEMICOLON):
            self.advance()
        return ExprStmt(expr)
    
    def expression(self) -> ASTNode:
        return self.assignment()
    
    def assignment(self) -> ASTNode:
        expr = self.logical_or()
        
        if self.match(TokenType.ASSIGN):
            self.advance()
            value = self.assignment()
            
            if isinstance(expr, Variable):
                return Assignment(expr.name, value)
            elif isinstance(expr, MemberAccess):
                return MemberAssignment(expr.object, expr.member, value)
            elif isinstance(expr, IndexAccess):
                return IndexedAssignment(expr.object, expr.index, value)
            else:
                self.error("Invalid assignment target")
        
        return expr
    
    def logical_or(self) -> ASTNode:
        expr = self.logical_and()
        
        while self.match(TokenType.OR):
            op = self.advance().value
            right = self.logical_and()
            expr = BinaryOp(expr, op, right)
        
        return expr
    
    def logical_and(self) -> ASTNode:
        expr = self.equality()
        
        while self.match(TokenType.AND):
            op = self.advance().value
            right = self.equality()
            expr = BinaryOp(expr, op, right)
        
        return expr
    
    def equality(self) -> ASTNode:
        expr = self.comparison()
        
        while self.match(TokenType.EQ, TokenType.NEQ):
            op = self.advance().value
            right = self.comparison()
            expr = BinaryOp(expr, op, right)
        
        return expr
    
    def comparison(self) -> ASTNode:
        expr = self.term()
        
        while self.match(TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
            op = self.advance().value
            right = self.term()
            expr = BinaryOp(expr, op, right)
        
        return expr
    
    def term(self) -> ASTNode:
        expr = self.factor()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.factor()
            expr = BinaryOp(expr, op, right)
        
        return expr
    
    def factor(self) -> ASTNode:
        expr = self.unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.advance().value
            right = self.unary()
            expr = BinaryOp(expr, op, right)
        
        return expr
    
    def unary(self) -> ASTNode:
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.advance().value
            expr = self.unary()
            return UnaryOp(op, expr)
        
        return self.call()
    
    def call(self) -> ASTNode:
        expr = self.primary()

        while True:
            # Handle method calls: obj.method()
            if self.match(TokenType.DOT):
                self.advance()
                member_name = self.consume(TokenType.IDENTIFIER, "Expected member name after '.'").value

                if self.match(TokenType.LPAREN):
                    self.advance()
                    arguments = []

                    if not self.match(TokenType.RPAREN):
                        arguments.append(self.expression())
                        while self.match(TokenType.COMMA):
                            self.advance()
                            arguments.append(self.expression())

                    self.consume(TokenType.RPAREN)
                    expr = MethodCall(expr, member_name, arguments)
                else:
                    expr = MemberAccess(expr, member_name)

            # Handle array/string indexing and slicing: arr[index] or arr[start:end]
            elif self.match(TokenType.LBRACKET):
                self.advance()
                
                # Check if it's a slice (has colon)
                if self.match(TokenType.COLON):
                    # [:end] - slice from beginning
                    self.advance()
                    if self.match(TokenType.RBRACKET):
                        # [:] - entire slice
                        self.consume(TokenType.RBRACKET)
                        expr = SliceAccess(expr, None, None)
                    else:
                        # [:end]
                        end = self.expression()
                        self.consume(TokenType.RBRACKET, "Expected ']' after slice")
                        expr = SliceAccess(expr, None, end)
                else:
                    # Parse first expression
                    first_expr = self.expression()
                    
                    if self.match(TokenType.COLON):
                        # [start:] or [start:end]
                        self.advance()
                        if self.match(TokenType.RBRACKET):
                            # [start:]
                            self.consume(TokenType.RBRACKET)
                            expr = SliceAccess(expr, first_expr, None)
                        else:
                            # [start:end]
                            end = self.expression()
                            self.consume(TokenType.RBRACKET, "Expected ']' after slice")
                            expr = SliceAccess(expr, first_expr, end)
                    else:
                        # [index] - regular index access
                        self.consume(TokenType.RBRACKET, "Expected ']' after index")
                        expr = IndexAccess(expr, first_expr)

            # Handle regular function calls: func()
            elif self.match(TokenType.LPAREN):
                self.advance()
                arguments = []

                if not self.match(TokenType.RPAREN):
                    arguments.append(self.expression())
                    while self.match(TokenType.COMMA):
                        self.advance()
                        arguments.append(self.expression())

                self.consume(TokenType.RPAREN)

                if isinstance(expr, Variable):
                    expr = FuncCall(expr.name, arguments)
                else:
                    self.error("Invalid function call")
            else:
                break

        return expr
    
    def primary(self) -> ASTNode:
        if self.match(TokenType.TRUE):
            self.advance()
            return BoolLiteral(True)

        if self.match(TokenType.FALSE):
            self.advance()
            return BoolLiteral(False)

        if self.match(TokenType.NUMBER_LITERAL):
            value = self.advance().value
            return NumberLiteral(value)

        if self.match(TokenType.STRING_LITERAL):
            value = self.advance().value
            return StringLiteral(value)

        if self.match(TokenType.IDENTIFIER):
            name = self.advance().value
            return Variable(name)

        if self.match(TokenType.NEW):
            self.advance()
            class_name = self.consume(TokenType.IDENTIFIER, "Expected class name after 'new'").value
            self.consume(TokenType.LPAREN, "Expected '(' after class name")

            arguments = []
            if not self.match(TokenType.RPAREN):
                arguments.append(self.expression())
                while self.match(TokenType.COMMA):
                    self.advance()
                    arguments.append(self.expression())

            self.consume(TokenType.RPAREN, "Expected ')' after constructor arguments")
            return ObjectCreation(class_name, arguments)

        if self.match(TokenType.THIS):
            self.advance()
            return ThisRef()

        if self.match(TokenType.SUPER):
            self.advance()
            return SuperRef()

        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.expression()
            self.consume(TokenType.RPAREN)
            return expr

        # List literal: []  or  [elem1, elem2, ...]  or  [for ... -> expr]
        if self.match(TokenType.LBRACKET):
            self.advance()
            
            # Check for list comprehension: [for (var x in list) -> expr]
            if self.match(TokenType.FOR):
                self.advance()
                self.consume(TokenType.LPAREN)
                
                # Parse loop variable
                self.consume(TokenType.VAR, "Expected 'var' in list comprehension")
                var_name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
                self.consume(TokenType.COLON, "Expected ':' after variable name")
                var_type = self.type_specifier()
                
                variable = VarDecl(var_type, var_name, None)
                
                # Parse 'in' keyword
                self.consume(TokenType.IN, "Expected 'in' after variable declaration")
                
                # Parse iterable
                iterable = self.expression()
                
                self.consume(TokenType.RPAREN, "Expected ')' after iterable")
                self.consume(TokenType.ARROW, "Expected '->' in list comprehension")
                
                # Parse expression
                expr = self.expression()
                
                self.consume(TokenType.RBRACKET, "Expected ']' after list comprehension")
                return ListComprehension(variable, iterable, expr)
            
            # Regular list literal
            elements = []
            
            if not self.match(TokenType.RBRACKET):
                elements.append(self.expression())
                while self.match(TokenType.COMMA):
                    self.advance()
                    if self.match(TokenType.RBRACKET):  # Allow trailing comma
                        break
                    elements.append(self.expression())
            
            self.consume(TokenType.RBRACKET, "Expected ']' after list elements")
            return ListLiteral(elements)

        # Dictionary literal: {}  or  {key1: val1, key2: val2, ...}
        if self.match(TokenType.LBRACE):
            # Need to distinguish between block and dict literal
            # Check for dictionary patterns by looking ahead
            next_token = self.peek(1)
            
            # Empty dict: {}
            if next_token.type == TokenType.RBRACE:
                return self.dict_literal()
            
            # Dict with string keys: {"key": value}
            if next_token.type == TokenType.STRING_LITERAL:
                if self.peek(2).type == TokenType.COLON:
                    return self.dict_literal()
            
            # Dict with identifier keys: {key: value}
            if next_token.type == TokenType.IDENTIFIER:
                if self.peek(2).type == TokenType.COLON:
                    return self.dict_literal()
            
            # Otherwise fall through to error (not a valid dict in expression context)

        self.error(f"Unexpected token: {self.current().type.name}")

    def dict_literal(self) -> DictLiteral:
        """Parse dictionary literal: {key1: val1, key2: val2}"""
        self.consume(TokenType.LBRACE)
        pairs = []
        
        if not self.match(TokenType.RBRACE):
            # Parse first key:value pair
            key = self.expression()
            self.consume(TokenType.COLON, "Expected ':' after dictionary key")
            value = self.expression()
            pairs.append((key, value))
            
            while self.match(TokenType.COMMA):
                self.advance()
                if self.match(TokenType.RBRACE):  # Allow trailing comma
                    break
                key = self.expression()
                self.consume(TokenType.COLON, "Expected ':' after dictionary key")
                value = self.expression()
                pairs.append((key, value))
        
        self.consume(TokenType.RBRACE, "Expected '}' after dictionary elements")
        return DictLiteral(pairs)
