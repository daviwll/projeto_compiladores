"""
Symbol Table with Scope Management for Minipar Language
Manages symbols, scopes, and type information
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class SymbolType(Enum):
    """Types of symbols that can be stored"""
    VARIABLE = "variable"
    FUNCTION = "function"
    PARAMETER = "parameter"
    CHANNEL = "channel"


@dataclass
class Symbol:
    """Represents a symbol in the symbol table"""
    name: str
    symbol_type: SymbolType
    data_type: str  # number, string, bool, void, etc.
    scope_level: int
    line_declared: int
    is_initialized: bool = True
    # For functions: parameter types and return type
    param_types: Optional[List[str]] = None
    return_type: Optional[str] = None
    # For channels: channel type (c_channel or s_channel)
    channel_type: Optional[str] = None


class Scope:
    """Represents a single scope level"""
    def __init__(self, scope_level: int, scope_name: str, parent: Optional['Scope'] = None):
        self.scope_level = scope_level
        self.scope_name = scope_name
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
    
    def add_symbol(self, symbol: Symbol) -> bool:
        """Add a symbol to this scope. Returns False if already exists."""
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True
    
    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Look up a symbol only in this scope"""
        return self.symbols.get(name)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope or parent scopes"""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
    
    def get_all_symbols(self) -> Dict[str, Symbol]:
        """Get all symbols in this scope"""
        return self.symbols.copy()


class SymbolTable:
    """Symbol table with scope management"""
    
    def __init__(self):
        self.current_scope: Scope = Scope(0, "global", None)
        self.scope_stack: List[Scope] = [self.current_scope]
        self.scope_counter = 0
    
    def enter_scope(self, scope_name: str = "block") -> None:
        """Enter a new scope (for functions, blocks, etc.)"""
        self.scope_counter += 1
        new_scope = Scope(self.scope_counter, scope_name, self.current_scope)
        self.scope_stack.append(new_scope)
        self.current_scope = new_scope
    
    def exit_scope(self) -> None:
        """Exit the current scope and return to parent"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]
    
    def add_symbol(self, name: str, symbol_type: SymbolType, data_type: str, 
                   line: int, **kwargs) -> bool:
        """
        Add a symbol to the current scope
        Returns False if symbol already exists in current scope
        """
        symbol = Symbol(
            name=name,
            symbol_type=symbol_type,
            data_type=data_type,
            scope_level=self.current_scope.scope_level,
            line_declared=line,
            **kwargs
        )
        return self.current_scope.add_symbol(symbol)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in current scope or parent scopes"""
        return self.current_scope.lookup(name)
    
    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Look up a symbol only in current scope"""
        return self.current_scope.lookup_local(name)
    
    def get_current_scope_level(self) -> int:
        """Get the current scope level"""
        return self.current_scope.scope_level
    
    def get_scope_name(self) -> str:
        """Get the current scope name"""
        return self.current_scope.scope_name
    
    def is_global_scope(self) -> bool:
        """Check if we're in global scope"""
        return self.current_scope.scope_level == 0
    
    def get_all_symbols_in_scope(self) -> Dict[str, Symbol]:
        """Get all symbols in current scope"""
        return self.current_scope.get_all_symbols()
    
    def print_table(self):
        """Print the symbol table for debugging"""
        print("\n=== Symbol Table ===")
        print(f"Current Scope: {self.current_scope.scope_name} (Level {self.current_scope.scope_level})")
        print(f"\nScopes in stack: {len(self.scope_stack)}")
        
        for i, scope in enumerate(self.scope_stack):
            print(f"\n--- Scope {i}: {scope.scope_name} (Level {scope.scope_level}) ---")
            if scope.symbols:
                for name, symbol in scope.symbols.items():
                    print(f"  {name}: {symbol.symbol_type.value} - {symbol.data_type} (line {symbol.line_declared})")
            else:
                print("  (empty)")
