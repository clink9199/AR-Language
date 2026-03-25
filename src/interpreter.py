"""
AR Language - Interpreter (Tree-Walker)
=========================================
What is an Interpreter?
  The Lexer broke code into tokens.
  The Parser built an AST (tree of nodes).
  Now the INTERPRETER walks that tree and actually RUNS the code.

  It's like reading a recipe: Lexer lists the ingredients, Parser understands
  the steps, and the Interpreter is YOU actually cooking the meal.

How a tree-walker works:
  For each node in the AST, we have a method called  visit_<NodeType>.
  We start at the root (Program), call visit on it,
  which calls visit on each statement inside it, which calls visit
  on sub-expressions... and so on, recursively.

  Example:  output 5 + 3

    visit_Program
      visit_OutputStatement
        visit_BinaryOp          ← computes 5 + 3 = 8
          visit_NumberLiteral   → 5
          visit_NumberLiteral   → 3
        → prints 8

OOP support:
  When you define a class, we store an ArClass object.
  When you say  new Animal("Cat"), we create an ArInstance.
  Instance methods receive 'self' as the first argument
  so they can access/modify the object's own properties.
"""

from src.ast_nodes import *
from src.environment import Environment


# ─────────────────────────────────────────────
#  SPECIAL CONTROL FLOW SIGNALS
#  These are not errors — they're signals we use internally
#  to implement  return  without breaking the call stack.
# ─────────────────────────────────────────────

class ReturnSignal(Exception):
    """
    Raised when 'return' is encountered inside a function.
    Bubbles up through the call stack until the function call catches it.
    """
    def __init__(self, value):
        self.value = value


# ─────────────────────────────────────────────
#  OOP RUNTIME OBJECTS
# ─────────────────────────────────────────────

class ArFunction:
    """
    A user-defined function or method defined in AR Language.
    Stores the definition (params + body) and the environment
    where it was defined (for closures).
    """
    def __init__(self, definition: FuncDefinition, closure: Environment):
        self.definition = definition
        self.closure    = closure   # the environment snapshot when func was defined


class ArClass:
    """
    A class defined in AR Language using the 'class' keyword.
    Stores the class name and all its methods.
    """
    def __init__(self, definition: ClassDefinition, closure: Environment):
        self.definition = definition
        self.closure    = closure
        self.name       = definition.name
        # Build a method lookup table: name → FuncDefinition
        self.methods    = {m.name: m for m in definition.methods}


class ArInstance:
    """
    An object — a live instance of an ArClass.
    Created with the 'new' keyword.
    Has its own property dictionary (like a personal storage box).
    """
    def __init__(self, ar_class: ArClass):
        self.ar_class   = ar_class
        self.properties = {}   # e.g.  {"name": "Ahmed", "age": 25}

    def get_property(self, name: str):
        if name in self.properties:
            return self.properties[name]
        raise AttributeError(f"[AR] Object of class '{self.ar_class.name}' has no property '{name}'.")

    def set_property(self, name: str, value):
        self.properties[name] = value

    def get_method(self, name: str) -> ArFunction:
        if name in self.ar_class.methods:
            return ArFunction(self.ar_class.methods[name], self.ar_class.closure)
        raise AttributeError(
            f"[AR] Class '{self.ar_class.name}' has no method '{name}'."
        )

    def __repr__(self):
        return f"<{self.ar_class.name} instance>"


# ─────────────────────────────────────────────
#  INTERPRETER
# ─────────────────────────────────────────────

class Interpreter:
    """
    Tree-walking interpreter for AR Language.
    Visits AST nodes and evaluates them.
    """

    def __init__(self):
        # The global environment is the outermost scope.
        # All top-level variables and functions live here.
        self.global_env = Environment()

    def run(self, program: Program):
        """Run a parsed program node in the global environment."""
        self.exec_block(program.statements, self.global_env)

    # ── Block execution ───────────────────────────────────────────

    def exec_block(self, statements: list, env: Environment):
        """Execute a list of statements in the given environment."""
        for stmt in statements:
            self.visit(stmt, env)

    # ── Node dispatcher ───────────────────────────────────────────

    def visit(self, node: Node, env: Environment):
        """
        Central dispatch method.
        Looks up the correct visit_* method for this node type and calls it.
        """
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.no_visitor)
        return visitor(node, env)

    def no_visitor(self, node: Node, env: Environment):
        raise NotImplementedError(
            f"[AR Interpreter] No visitor for node type: {type(node).__name__}"
        )

    # ── Literals ─────────────────────────────────────────────────

    def visit_NumberLiteral(self, node: NumberLiteral, env: Environment):
        """Return the numeric value.  42 → 42.0"""
        # If it's a whole number (42.0), return it as int for cleaner output
        if node.value == int(node.value):
            return int(node.value)
        return node.value

    def visit_StringLiteral(self, node: StringLiteral, env: Environment):
        return node.value

    def visit_BoolLiteral(self, node: BoolLiteral, env: Environment):
        return node.value

    def visit_NullLiteral(self, node: NullLiteral, env: Environment):
        return None

    # ── Identifier ────────────────────────────────────────────────

    def visit_Identifier(self, node: Identifier, env: Environment):
        """Look up the variable's value in the current scope chain."""
        return env.get(node.name)

    # ── Expressions ───────────────────────────────────────────────

    def visit_BinaryOp(self, node: BinaryOp, env: Environment):
        """
        Evaluate both sides, then apply the operator.
        Example:  5 + 3  →  evaluate 5, evaluate 3, add them → 8
        """
        left  = self.visit(node.left,  env)
        right = self.visit(node.right, env)
        op    = node.op

        if op == "+":
            # Special: "hello" + " world" = "hello world"  (string concatenation)
            if isinstance(left, str) or isinstance(right, str):
                return self._display(left) + self._display(right)
            return left + right
        elif op == "-":   return left - right
        elif op == "*":   return left * right
        elif op == "/":
            if right == 0:
                raise ZeroDivisionError("[AR] Cannot divide by zero.")
            result = left / right
            return int(result) if result == int(result) else result
        elif op == "==":  return left == right
        elif op == "!=":  return left != right
        elif op == "<":   return left < right
        elif op == ">":   return left > right
        elif op == "<=":  return left <= right
        elif op == ">=":  return left >= right
        elif op == "and": return bool(left) and bool(right)
        elif op == "or":  return bool(left) or bool(right)
        else:
            raise RuntimeError(f"[AR] Unknown operator: {op}")

    def visit_UnaryOp(self, node: UnaryOp, env: Environment):
        """Negate or invert a single value."""
        operand = self.visit(node.operand, env)
        if node.op == "not": return not operand
        if node.op == "-":   return -operand

    def visit_MemberAccess(self, node: MemberAccess, env: Environment):
        """
        Access a property on an object.
        Example:  cat.name  →  get 'cat' → look up 'name' on it
        """
        obj = self.visit(node.obj, env)
        if isinstance(obj, ArInstance):
            return obj.get_property(node.member)
        raise AttributeError(f"[AR] Cannot access member '{node.member}' on {type(obj).__name__}.")

    def visit_CallExpression(self, node: CallExpression, env: Environment):
        """
        Call a function or method.
        1. Evaluate the callee (what are we calling?)
        2. Evaluate each argument
        3. If it's a method call on an object, handle 'self'
        4. Create a new scope and execute the function body
        """
        args = [self.visit(a, env) for a in node.args]

        # Method call:  cat.speak()
        if isinstance(node.callee, MemberAccess):
            obj = self.visit(node.callee.obj, env)
            if isinstance(obj, ArInstance):
                method = obj.get_method(node.callee.member)
                return self._call_function(method, [obj] + args)
            raise TypeError(f"[AR] '{node.callee.member}' is not callable on this object.")

        # Regular function call:  greet("Ahmed")
        func = self.visit(node.callee, env)

        if isinstance(func, ArFunction):
            return self._call_function(func, args)

        raise TypeError(f"[AR] '{node.callee}' is not a function.")

    def visit_NewExpression(self, node: NewExpression, env: Environment):
        """
        Create a new object instance.
        Example:  new Animal("Cat")
          1. Look up the 'Animal' class
          2. Create an ArInstance
          3. Call init(self, ...) if it exists
          4. Return the instance
        """
        ar_class = env.get(node.class_name)
        if not isinstance(ar_class, ArClass):
            raise TypeError(f"[AR] '{node.class_name}' is not a class.")

        instance = ArInstance(ar_class)
        args = [self.visit(a, env) for a in node.args]

        # Call the constructor if the class has one
        if "init" in ar_class.methods:
            init_func = ArFunction(ar_class.methods["init"], ar_class.closure)
            self._call_function(init_func, [instance] + args)

        return instance

    def _call_function(self, func: ArFunction, args: list):
        """
        Execute a function with the given arguments.
        Creates a fresh environment (scope) for the function,
        binds parameters to arguments, runs the body.
        """
        func_env = Environment(parent=func.closure)

        # Bind parameter names to argument values
        params = func.definition.params
        for param, arg in zip(params, args):
            func_env.set(param, arg)

        # Run the function body, catching any ReturnSignal
        try:
            self.exec_block(func.definition.body, func_env)
        except ReturnSignal as ret:
            return ret.value

        return None  # functions return null by default

    # ── Statements ────────────────────────────────────────────────

    def visit_OutputStatement(self, node: OutputStatement, env: Environment):
        """Evaluate the value and print it nicely."""
        value = self.visit(node.value, env)
        print(self._display(value))

    def visit_LetStatement(self, node: LetStatement, env: Environment):
        """Declare a new variable in the current scope."""
        value = self.visit(node.value, env)
        env.set(node.name, value)

    def visit_AssignStatement(self, node: AssignStatement, env: Environment):
        """
        Reassign an existing variable.
        Handles:  x = 10
        And also: self.name = "Ahmed"  (property on an object)
        """
        value = self.visit(node.value, env)

        if isinstance(node.target, MemberAccess):
            # It's a property assignment: self.name = "Ahmed"
            obj = self.visit(node.target.obj, env)
            if isinstance(obj, ArInstance):
                obj.set_property(node.target.member, value)
                return
            raise AttributeError(f"[AR] Cannot set property on non-object.")
        elif isinstance(node.target, Identifier):
            # It's a variable assignment: x = 10
            try:
                env.assign(node.target.name, value)
            except NameError:
                # Variable doesn't exist yet — create it (treat as let)
                env.set(node.target.name, value)
        else:
            raise SyntaxError("[AR] Invalid assignment target.")

    def visit_ReturnStatement(self, node: ReturnStatement, env: Environment):
        """Raise a ReturnSignal to break out of the current function."""
        value = self.visit(node.value, env) if node.value else None
        raise ReturnSignal(value)

    def visit_IfStatement(self, node: IfStatement, env: Environment):
        """Evaluate the condition — run then_body or else_body accordingly."""
        condition = self.visit(node.condition, env)
        branch_env = Environment(parent=env)

        if condition:
            self.exec_block(node.then_body, branch_env)
        elif node.else_body:
            self.exec_block(node.else_body, branch_env)

    def visit_LoopStatement(self, node: LoopStatement, env: Environment):
        """Keep running the body while the condition is True."""
        while self.visit(node.condition, env):
            loop_env = Environment(parent=env)
            self.exec_block(node.body, loop_env)

    def visit_FuncDefinition(self, node: FuncDefinition, env: Environment):
        """
        Store a function definition in the current environment.
        The function captures its enclosing scope (closure).
        """
        func = ArFunction(definition=node, closure=env)
        env.set(node.name, func)

    def visit_ClassDefinition(self, node: ClassDefinition, env: Environment):
        """Store a class definition in the current environment."""
        ar_class = ArClass(definition=node, closure=env)
        env.set(node.name, ar_class)

    def visit_ExpressionStatement(self, node: ExpressionStatement, env: Environment):
        """Evaluate the expression (often a function call) and discard the result."""
        self.visit(node.expression, env)

    def visit_Program(self, node: Program, env: Environment):
        """Visit the root Program node."""
        self.exec_block(node.statements, env)

    # ── Display helper ────────────────────────────────────────────

    def _display(self, value) -> str:
        """Convert a value to a human-readable string for output."""
        if value is None:    return "null"
        if value is True:    return "true"
        if value is False:   return "false"
        return str(value)
