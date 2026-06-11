"""
Lexer for Minipar Language
Performs lexical analysis and tokenization
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    # Keywords
    BREAK = auto()
    C_CHANNEL = auto()
    CLASS = auto()
    CONTINUE = auto()
    ELSE = auto()
    FALSE = auto()
    FOR = auto()
    FUNC = auto()
    IF = auto()
    IN = auto()
    NEW = auto()
    PAR = auto()
    RETURN = auto()
    S_CHANNEL = auto()
    SEQ = auto()  # NEW: Sequential block keyword
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()
    EXTENDS = auto()
    CONSTRUCTOR = auto()
    
    # Types
    NUMBER = auto()
    STRING = auto()
    BOOL = auto()
    VOID = auto()
    LIST = auto()
    DICT = auto()
    ANY = auto()
    
    # Literals
    NUMBER_LITERAL = auto()
    STRING_LITERAL = auto()
    
    # Identifiers
    IDENTIFIER = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    NOT = auto()
    
    # Comparison
    EQ = auto()
    NEQ = auto()
    LTE = auto()
    GTE = auto()
    LT = auto()
    GT = auto()
    ASSIGN = auto()
    
    # Logical
    AND = auto()
    OR = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()
    ARROW = auto()
    DOT = auto()
    
    # Special
    EOF = auto()
    NEWLINE = auto()


@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, {self.line}:{self.column})"


class Lexer:
    KEYWORDS = {
        'break': TokenType.BREAK,
        'c_channel': TokenType.C_CHANNEL,
        'class': TokenType.CLASS,
        'continue': TokenType.CONTINUE,
        'else': TokenType.ELSE,
        'false': TokenType.FALSE,
        'for': TokenType.FOR,
        'func': TokenType.FUNC,
        'if': TokenType.IF,
        'in': TokenType.IN,
        'new': TokenType.NEW,
        'par': TokenType.PAR,
        'return': TokenType.RETURN,
        's_channel': TokenType.S_CHANNEL,
        'seq': TokenType.SEQ,  # NEW: SEQ keyword
        'super': TokenType.SUPER,
        'this': TokenType.THIS,
        'true': TokenType.TRUE,
        'var': TokenType.VAR,
        'while': TokenType.WHILE,
        'extends': TokenType.EXTENDS,
        'constructor': TokenType.CONSTRUCTOR,
        'number': TokenType.NUMBER,
        'string': TokenType.STRING,
        'bool': TokenType.BOOL,
        'void': TokenType.VOID,
        'list': TokenType.LIST,
        'dict': TokenType.DICT,
        'any': TokenType.ANY,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def error(self, msg: str):
        raise SyntaxError(f"Lexer error at {self.line}:{self.column}: {msg}")
    
    def peek(self, offset: int = 0) -> Optional[str]:
        pos = self.pos + offset
        return self.source[pos] if pos < len(self.source) else None
    
    def advance(self) -> Optional[str]:
        if self.pos >= len(self.source):
            return None
        char = self.source[self.pos]
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char
    
    def skip_whitespace(self):
        while self.peek() and self.peek() in ' \t\r\n':
            self.advance()
    
    def skip_comment(self):
        if self.peek() == '#':
            while self.peek() and self.peek() != '\n':
                self.advance()
            return True
        
        if self.peek() == '/' and self.peek(1) == '*':
            self.advance()
            self.advance()
            while self.peek():
                if self.peek() == '*' and self.peek(1) == '/':
                    self.advance()
                    self.advance()
                    return True
                self.advance()
            self.error("Unterminated multi-line comment")
        
        return False
    
    def read_number(self) -> Token:
        start_line, start_col = self.line, self.column
        num_str = ''
        has_dot = False
        
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            if self.peek() == '.':
                if has_dot:
                    break
                has_dot = True
            num_str += self.advance()
        
        value = float(num_str) if has_dot else int(num_str)
        return Token(TokenType.NUMBER_LITERAL, value, start_line, start_col)
    
    def read_string(self) -> Token:
        start_line, start_col = self.line, self.column
        self.advance()  # skip opening quote
        string_val = ''
        
        while self.peek() and self.peek() != '"':
            if self.peek() == '\\':
                self.advance()
                next_char = self.advance()
                if next_char == 'n':
                    string_val += '\n'
                elif next_char == 't':
                    string_val += '\t'
                elif next_char == '"':
                    string_val += '"'
                elif next_char == '\\':
                    string_val += '\\'
                else:
                    string_val += next_char
            else:
                string_val += self.advance()
        
        if not self.peek():
            self.error("Unterminated string literal")
        
        self.advance()  # skip closing quote
        return Token(TokenType.STRING_LITERAL, string_val, start_line, start_col)
    
    def read_identifier(self) -> Token:
        start_line, start_col = self.line, self.column
        ident = ''
        
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            ident += self.advance()
        
        token_type = self.KEYWORDS.get(ident, TokenType.IDENTIFIER)
        value = ident if token_type == TokenType.IDENTIFIER else ident
        return Token(token_type, value, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self.skip_whitespace()
            
            if self.pos >= len(self.source):
                break
            
            if self.skip_comment():
                continue
            
            start_line, start_col = self.line, self.column
            char = self.peek()
            
            # Numbers
            if char.isdigit():
                self.tokens.append(self.read_number())
            
            # Strings
            elif char == '"':
                self.tokens.append(self.read_string())
            
            # Identifiers and keywords
            elif char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
            
            # Two-character operators
            elif char == '=' and self.peek(1) == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.EQ, '==', start_line, start_col))
            
            elif char == '!' and self.peek(1) == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.NEQ, '!=', start_line, start_col))
            
            elif char == '<' and self.peek(1) == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.LTE, '<=', start_line, start_col))
            
            elif char == '>' and self.peek(1) == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.GTE, '>=', start_line, start_col))
            
            elif char == '&' and self.peek(1) == '&':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.AND, '&&', start_line, start_col))
            
            elif char == '|' and self.peek(1) == '|':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.OR, '||', start_line, start_col))
            
            elif char == '-' and self.peek(1) == '>':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.ARROW, '->', start_line, start_col))
            
            # Single-character operators and delimiters
            elif char == '+':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS, '+', start_line, start_col))
            
            elif char == '-':
                self.advance()
                self.tokens.append(Token(TokenType.MINUS, '-', start_line, start_col))
            
            elif char == '*':
                self.advance()
                self.tokens.append(Token(TokenType.MULTIPLY, '*', start_line, start_col))
            
            elif char == '/':
                self.advance()
                self.tokens.append(Token(TokenType.DIVIDE, '/', start_line, start_col))
            
            elif char == '%':
                self.advance()
                self.tokens.append(Token(TokenType.MODULO, '%', start_line, start_col))
            
            elif char == '!':
                self.advance()
                self.tokens.append(Token(TokenType.NOT, '!', start_line, start_col))
            
            elif char == '<':
                self.advance()
                self.tokens.append(Token(TokenType.LT, '<', start_line, start_col))
            
            elif char == '>':
                self.advance()
                self.tokens.append(Token(TokenType.GT, '>', start_line, start_col))
            
            elif char == '=':
                self.advance()
                self.tokens.append(Token(TokenType.ASSIGN, '=', start_line, start_col))
            
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', start_line, start_col))
            
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', start_line, start_col))
            
            elif char == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, '{', start_line, start_col))
            
            elif char == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, '}', start_line, start_col))
            
            elif char == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', start_line, start_col))
            
            elif char == ';':
                self.advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ';', start_line, start_col))
            
            elif char == ':':
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ':', start_line, start_col))
            
            elif char == '.':
                self.advance()
                self.tokens.append(Token(TokenType.DOT, '.', start_line, start_col))
            
            elif char == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, '[', start_line, start_col))
            
            elif char == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, ']', start_line, start_col))
            
            else:
                self.error(f"Unexpected character: '{char}'")
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
