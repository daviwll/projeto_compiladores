"""
Abstract Syntax Tree Node Definitions for Minipar Language
"""

from dataclasses import dataclass
from typing import List, Optional, Any


@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    pass


@dataclass
class Program(ASTNode):
    declarations: List[ASTNode]


@dataclass
class VarDecl(ASTNode):
    type: str
    name: str
    initializer: Optional[ASTNode] = None


@dataclass
class FuncDecl(ASTNode):
    return_type: str
    name: str
    parameters: List[VarDecl]
    body: 'Block'


@dataclass
class Block(ASTNode):
    statements: List[ASTNode]


@dataclass
class IfStmt(ASTNode):
    condition: ASTNode
    then_branch: ASTNode
    else_branch: Optional[ASTNode] = None


@dataclass
class WhileStmt(ASTNode):
    condition: ASTNode
    body: ASTNode


@dataclass
class ForStmt(ASTNode):
    """For loop - for (var x in iterable) { body }"""
    variable: VarDecl  # Loop variable declaration
    iterable: ASTNode  # Expression to iterate over
    body: ASTNode  # Loop body


@dataclass
class ReturnStmt(ASTNode):
    value: Optional[ASTNode] = None


@dataclass
class BreakStmt(ASTNode):
    pass


@dataclass
class ContinueStmt(ASTNode):
    pass


@dataclass
class ExprStmt(ASTNode):
    expression: ASTNode


@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode


@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode


@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: ASTNode


@dataclass
class FuncCall(ASTNode):
    name: str
    arguments: List[ASTNode]


@dataclass
class Variable(ASTNode):
    name: str


@dataclass
class NumberLiteral(ASTNode):
    value: float


@dataclass
class StringLiteral(ASTNode):
    value: str


@dataclass
class BoolLiteral(ASTNode):
    value: bool


@dataclass
class ListLiteral(ASTNode):
    """List literal - [elem1, elem2, ...]"""
    elements: List[ASTNode]


@dataclass
class ListComprehension(ASTNode):
    """List comprehension - [for (var x in iterable) -> expression]"""
    variable: VarDecl  # Loop variable
    iterable: ASTNode  # Expression to iterate over
    expression: ASTNode  # Expression to evaluate for each element


@dataclass
class DictLiteral(ASTNode):
    """Dictionary literal - {key1: val1, key2: val2, ...}"""
    pairs: List[tuple]  # List of (key, value) tuples


@dataclass
class ChannelDecl(ASTNode):
    """Channel declaration (s_channel or c_channel)"""
    channel_type: str  # 's_channel' or 'c_channel'
    name: str
    arguments: List[ASTNode]  # Arguments for the channel (function, desc, host, port, etc.)


@dataclass
class SeqBlock(ASTNode):
    """Sequential execution block - SEQ { stmts }"""
    statements: List[ASTNode]


@dataclass
class ParBlock(ASTNode):
    """Parallel execution block - PAR { stmts }"""
    statements: List[ASTNode]


@dataclass
class MethodCall(ASTNode):
    """Method call on an object - obj.method(args)"""
    object: str  # Object name
    method: str  # Method name
    arguments: List[ASTNode]  # Method arguments


@dataclass
class IndexAccess(ASTNode):
    """Array/string index access - arr[index]"""
    object: ASTNode  # Object being indexed
    index: ASTNode  # Index expression


@dataclass
class SliceAccess(ASTNode):
    """Array/string slice access - arr[start:end]"""
    object: ASTNode  # Object being sliced
    start: Optional[ASTNode] = None  # Start index (None means beginning)
    end: Optional[ASTNode] = None  # End index (None means end)
