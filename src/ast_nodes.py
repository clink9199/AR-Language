"""
AR Language - AST (Abstract Syntax Tree) Nodes
================================================
What is an AST?
  When you write code like:  let x = 5 + 3
  The computer can't just read text.  It needs to understand the STRUCTURE.
  An AST is a tree of objects — each object is a "node" representing one piece of code.

  For example:  let x = 5 + 3   becomes a tree like:
    LetStatement
      name: "x"
      value: BinaryOp
                left: Number(5)
                op: "+"
                right: Number(3)

  This file defines all the building blocks (node types) that our language uses.
  Think of them as blueprints for every possible thing you can write in AR Language.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional


# ─────────────────────────────────────────────
#  BASE
# ─────────────────────────────────────────────

@dataclass
class Node:
    """Base class for every AST node."""
    pass


# ─────────────────────────────────────────────
#  PROGRAM (root of every .ar file)
# ─────────────────────────────────────────────

@dataclass
class Program(Node):
    """
    The root node of the entire program.
    Every .ar file becomes one Program node containing a list of statements.
    """
    statements: List[Node] = field(default_factory=list)


# ─────────────────────────────────────────────
#  LITERALS  (raw values like 42, "hello", true)
# ─────────────────────────────────────────────

@dataclass
class NumberLiteral(Node):
    """A plain number.  Example:  42   or   3.14"""
    value: float


@dataclass
class StringLiteral(Node):
    """A text value wrapped in double quotes.  Example:  "Hello World" """
    value: str


@dataclass
class BoolLiteral(Node):
    """true or false"""
    value: bool


@dataclass
class NullLiteral(Node):
    """null — represents the absence of a value"""
    pass


@dataclass
class ArrayLiteral(Node):
    """An array of values. Example: [1, 2, 3]"""
    elements: List[Node] = field(default_factory=list)


# ─────────────────────────────────────────────
#  IDENTIFIER  (a variable name like "x" or "name")
# ─────────────────────────────────────────────

@dataclass
class Identifier(Node):
    """
    Refers to a variable or function by name.
    Example:  output name    <-- "name" is an Identifier
    """
    name: str


# ─────────────────────────────────────────────
#  EXPRESSIONS  (things that produce a value)
# ─────────────────────────────────────────────

@dataclass
class BinaryOp(Node):
    """
    An operation between two values.
    Example:  5 + 3    left=5, op="+", right=3
    Supported ops: +  -  *  /  ==  !=  <  >  <=  >=  and  or
    """
    left: Node
    op: str
    right: Node


@dataclass
class UnaryOp(Node):
    """
    A single-operand operation.
    Example:  not true    op="not", operand=true
    """
    op: str
    operand: Node


@dataclass
class CallExpression(Node):
    """
    Calling a function.
    Example:  greet("Ahmed")
      callee = Identifier("greet")
      args   = [StringLiteral("Ahmed")]
    """
    callee: Node          # What to call (an Identifier, or a MemberAccess)
    args: List[Node] = field(default_factory=list)


@dataclass
class MemberAccess(Node):
    """
    Accessing a property or method on an object.
    Example:  cat.speak()
      obj    = Identifier("cat")
      member = "speak"
    """
    obj: Node
    member: str


@dataclass
class IndexAccess(Node):
    """
    Accessing an element in an array or string.
    Example: arr[0]
      obj   = Identifier("arr")
      index = NumberLiteral(0)
    """
    obj: Node
    index: Node


@dataclass
class NewExpression(Node):
    """
    Creating a new object from a class.
    Example:  new Animal("Cat")
      class_name = "Animal"
      args       = [StringLiteral("Cat")]
    """
    class_name: str
    args: List[Node] = field(default_factory=list)


# ─────────────────────────────────────────────
#  STATEMENTS  (things that DO something)
# ─────────────────────────────────────────────

@dataclass
class OutputStatement(Node):
    """
    Prints a value to the console.
    Example:  output "Hello, World!"
    """
    value: Node


@dataclass
class LetStatement(Node):
    """
    Declares a variable and gives it a value.
    Example:  let name = "Ahmed"
      name  = "name"
      value = StringLiteral("Ahmed")
    """
    name: str
    value: Node


@dataclass
class AssignStatement(Node):
    """
    Changes the value of an existing variable or property.
    Example:  x = 10     or     self.name = "Ahmed"
    """
    target: Node   # Identifier or MemberAccess
    value: Node


@dataclass
class IndexAssignment(Node):
    """
    Reassigning an element in an array.
    Example: arr[0] = 5
      obj   = Identifier("arr")
      index = NumberLiteral(0)
      value = NumberLiteral(5)
    """
    obj: Node
    index: Node
    value: Node


@dataclass
class ReturnStatement(Node):
    """
    Returns a value from a function.
    Example:  return x + 1
    """
    value: Optional[Node] = None


@dataclass
class IfStatement(Node):
    """
    Conditional branching.
    Example:
        if x > 5:
            output "big"
        else:
            output "small"
    """
    condition: Node
    then_body: List[Node] = field(default_factory=list)
    else_body: List[Node] = field(default_factory=list)


@dataclass
class LoopStatement(Node):
    """
    Repeats a block while the condition is true.
    Example:
        loop x < 10:
            output x
            x = x + 1
    """
    condition: Node
    body: List[Node] = field(default_factory=list)


@dataclass
class ForStatement(Node):
    """
    For-each loop over an iterable.
    Example: for item in items { ... }
    """
    iterator_name: str
    iterable: Node
    body: List[Node] = field(default_factory=list)


@dataclass
class ImportStatement(Node):
    """
    Importing another file.
    Example: import "math.ar"
    """
    filepath: str


# ─────────────────────────────────────────────
#  DEFINITIONS  (functions & classes)
# ─────────────────────────────────────────────

@dataclass
class FuncDefinition(Node):
    """
    Defines a reusable block of code.
    Example:
        func add(a, b):
            return a + b
    """
    name: str
    params: List[str] = field(default_factory=list)
    body: List[Node] = field(default_factory=list)


@dataclass
class ClassDefinition(Node):
    """
    Defines a blueprint for objects.
    Example:
        class Animal:
            init(self, name):
                self.name = name
            func speak(self):
                output self.name
    """
    name: str
    methods: List[FuncDefinition] = field(default_factory=list)


@dataclass
class ExpressionStatement(Node):
    """
    Wraps an expression used as a standalone statement.
    Example:  cat.speak()   — a method call used alone on a line.
    """
    expression: Node
