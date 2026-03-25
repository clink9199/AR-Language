"""
AR Language - Parser
=====================
What is a Parser?
  The Lexer gave us a flat LIST of tokens (words).
  The Parser takes that list and builds a TREE that shows the STRUCTURE.

  It's like the difference between:
    - A list of words: ["the", "cat", "sat", "on", "mat"]
    - A sentence tree: Sentence → Subject("cat") + Verb("sat") + Location("on mat")

  The Parser understands GRAMMAR — the rules of AR Language.

How does it work?
  We use a technique called "Recursive Descent Parsing".
  Each grammar rule becomes its own method.

  The hierarchy from lowest to highest priority (precedence):
    statement
      → expression_statement
          → assignment (= )
              → or_expr  (or)
                  → and_expr  (and)
                      → equality  (== !=)
                          → comparison  (< > <= >=)
                              → addition  (+ -)
                                  → multiplication  (* /)
                                      → unary  (not, -)
                                          → call / member
                                              → primary (number, string, ident...)

  Higher priority = evaluated FIRST (like * before + in math).
"""

from typing import List
from src.lexer import Token, TT
from src.ast_nodes import *


class Parser:
    """
    Recursive descent parser for AR Language.
    Consumes tokens one by one and returns a Program AST node.
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0              # current position in the token list

    # ── Token helpers ─────────────────────────────────────────────

    @property
    def current(self) -> Token:
        """The token we're currently looking at."""
        return self.tokens[self.pos]

    def peek(self, offset: int = 1) -> Token:
        """Look ahead by offset without consuming tokens."""
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # return EOF

    def advance(self) -> Token:
        """Consume (move past) the current token and return it."""
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def check(self, *types: TT) -> bool:
        """Return True if the current token is one of the given types."""
        return self.current.type in types

    def match(self, *types: TT) -> bool:
        """If current token matches, advance and return True. Else False."""
        if self.check(*types):
            self.advance()
            return True
        return False

    def expect(self, token_type: TT, msg: str = "") -> Token:
        """
        Consume the current token, but CRASH if it's not the expected type.
        Used when we KNOW what must come next based on grammar rules.
        """
        if not self.check(token_type):
            raise SyntaxError(
                f"[AR Parser] Line {self.current.line}: "
                f"Expected {token_type.name}, got {self.current.type.name} "
                f"({self.current.value!r}). {msg}"
            )
        return self.advance()

    def skip_newlines(self):
        """Skip any blank newline tokens."""
        while self.check(TT.NEWLINE):
            self.advance()

    # ── Program ───────────────────────────────────────────────────

    def parse(self) -> Program:
        """
        Entry point — parse the entire program.
        Returns a Program node containing all top-level statements.
        """
        statements = []
        self.skip_newlines()

        while not self.check(TT.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()

        return Program(statements=statements)

    # ── Statements ────────────────────────────────────────────────

    def parse_statement(self) -> Node:
        """
        Decide what kind of statement we're looking at and dispatch to
        the right parsing method.
        """
        tok = self.current

        if tok.type == TT.OUTPUT:
            return self.parse_output()
        elif tok.type == TT.LET:
            return self.parse_let()
        elif tok.type == TT.RETURN:
            return self.parse_return()
        elif tok.type == TT.IF:
            return self.parse_if()
        elif tok.type == TT.LOOP:
            return self.parse_loop()
        elif tok.type == TT.FUNC:
            return self.parse_func()
        elif tok.type == TT.CLASS:
            return self.parse_class()
        else:
            return self.parse_expression_statement()

    def parse_output(self) -> OutputStatement:
        """
        Parse:  output <expression>
        Example: output "Hello, World!"
        """
        self.advance()  # consume 'output'
        value = self.parse_expression()
        self.match(TT.NEWLINE)
        return OutputStatement(value=value)

    def parse_let(self) -> LetStatement:
        """
        Parse:  let <name> = <expression>
        Example: let age = 25
        """
        self.advance()  # consume 'let'
        name = self.expect(TT.IDENT, "Expected variable name after 'let'.").value
        self.expect(TT.EQUALS, "Expected '=' after variable name.")
        value = self.parse_expression()
        self.match(TT.NEWLINE)
        return LetStatement(name=name, value=value)

    def parse_return(self) -> ReturnStatement:
        """
        Parse:  return  or  return <expression>
        """
        self.advance()  # consume 'return'
        if self.check(TT.NEWLINE) or self.check(TT.EOF):
            self.match(TT.NEWLINE)
            return ReturnStatement()
        value = self.parse_expression()
        self.match(TT.NEWLINE)
        return ReturnStatement(value=value)

    def parse_if(self) -> IfStatement:
        """
        Parse:
            if <condition>:
                <body>
            else:
                <body>
        """
        self.advance()  # consume 'if'
        condition = self.parse_expression()
        self.expect(TT.COLON)
        self.match(TT.NEWLINE)

        then_body = self.parse_block()
        else_body = []

        self.skip_newlines()
        if self.check(TT.ELSE):
            self.advance()  # consume 'else'
            self.expect(TT.COLON)
            self.match(TT.NEWLINE)
            else_body = self.parse_block()

        return IfStatement(condition=condition, then_body=then_body, else_body=else_body)

    def parse_loop(self) -> LoopStatement:
        """
        Parse:
            loop <condition>:
                <body>
        """
        self.advance()  # consume 'loop'
        condition = self.parse_expression()
        self.expect(TT.COLON)
        self.match(TT.NEWLINE)
        body = self.parse_block()
        return LoopStatement(condition=condition, body=body)

    def parse_func(self) -> FuncDefinition:
        """
        Parse:
            func <name>(<params>):
                <body>
        """
        self.advance()  # consume 'func'
        name = self.expect(TT.IDENT, "Expected function name.").value
        self.expect(TT.LPAREN)
        params = self.parse_params()
        self.expect(TT.RPAREN)
        self.expect(TT.COLON)
        self.match(TT.NEWLINE)
        body = self.parse_block()
        return FuncDefinition(name=name, params=params, body=body)

    def parse_class(self) -> ClassDefinition:
        """
        Parse:
            class <Name>:
                init(self, ...):
                    ...
                func method(self):
                    ...
        """
        self.advance()  # consume 'class'
        name = self.expect(TT.IDENT, "Expected class name.").value
        self.expect(TT.COLON)
        self.match(TT.NEWLINE)
        self.expect(TT.INDENT)

        methods = []
        self.skip_newlines()

        while not self.check(TT.DEDENT) and not self.check(TT.EOF):
            if self.check(TT.INIT):
                # Constructor: init(self, ...):
                self.advance()  # consume 'init'
                self.expect(TT.LPAREN)
                params = self.parse_params()
                self.expect(TT.RPAREN)
                self.expect(TT.COLON)
                self.match(TT.NEWLINE)
                body = self.parse_block()
                methods.append(FuncDefinition(name="init", params=params, body=body))
            elif self.check(TT.FUNC):
                methods.append(self.parse_func())
            else:
                self.advance()  # skip unexpected tokens

            self.skip_newlines()

        self.match(TT.DEDENT)
        return ClassDefinition(name=name, methods=methods)

    def parse_expression_statement(self) -> Node:
        """
        Parse an expression used as a statement (e.g. a function call).
        Also handles assignment:  x = 10   or   self.name = "Ahmed"
        """
        expr = self.parse_expression()

        # Check if this is an assignment  (expr = value)
        if self.check(TT.EQUALS):
            self.advance()  # consume '='
            value = self.parse_expression()
            self.match(TT.NEWLINE)
            return AssignStatement(target=expr, value=value)

        self.match(TT.NEWLINE)
        return ExpressionStatement(expression=expr)

    # ── Block parsing ─────────────────────────────────────────────

    def parse_block(self) -> List[Node]:
        """
        Parse an indented block of statements.
        A block starts with INDENT and ends with DEDENT.
        """
        self.expect(TT.INDENT)
        statements = []
        self.skip_newlines()

        while not self.check(TT.DEDENT) and not self.check(TT.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()

        self.match(TT.DEDENT)
        return statements

    # ── Parameter list parsing ────────────────────────────────────

    def parse_params(self) -> List[str]:
        """
        Parse a comma-separated list of parameter names.
        Example: (self, name, age) → ["self", "name", "age"]
        """
        params = []
        # 'self' can appear as SELF token type
        if self.check(TT.SELF, TT.IDENT):
            params.append(self.advance().value)
            while self.match(TT.COMMA):
                if self.check(TT.SELF, TT.IDENT):
                    params.append(self.advance().value)
        return params

    # ── Expression parsing (ordered by precedence) ────────────────

    def parse_expression(self) -> Node:
        """Top of the expression hierarchy — handles 'or'."""
        return self.parse_or()

    def parse_or(self) -> Node:
        left = self.parse_and()
        while self.check(TT.OR):
            op = self.advance().value
            right = self.parse_and()
            left = BinaryOp(left=left, op=op, right=right)
        return left

    def parse_and(self) -> Node:
        left = self.parse_equality()
        while self.check(TT.AND):
            op = self.advance().value
            right = self.parse_equality()
            left = BinaryOp(left=left, op=op, right=right)
        return left

    def parse_equality(self) -> Node:
        left = self.parse_comparison()
        while self.check(TT.EQ_EQ, TT.BANG_EQ):
            op = self.advance().value
            right = self.parse_comparison()
            left = BinaryOp(left=left, op=op, right=right)
        return left

    def parse_comparison(self) -> Node:
        left = self.parse_addition()
        while self.check(TT.LT, TT.GT, TT.LT_EQ, TT.GT_EQ):
            op = self.advance().value
            right = self.parse_addition()
            left = BinaryOp(left=left, op=op, right=right)
        return left

    def parse_addition(self) -> Node:
        left = self.parse_multiplication()
        while self.check(TT.PLUS, TT.MINUS):
            op = self.advance().value
            right = self.parse_multiplication()
            left = BinaryOp(left=left, op=op, right=right)
        return left

    def parse_multiplication(self) -> Node:
        left = self.parse_unary()
        while self.check(TT.STAR, TT.SLASH):
            op = self.advance().value
            right = self.parse_unary()
            left = BinaryOp(left=left, op=op, right=right)
        return left

    def parse_unary(self) -> Node:
        """Handle  not  and unary minus  -"""
        if self.check(TT.NOT):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOp(op=op, operand=operand)
        if self.check(TT.MINUS):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOp(op=op, operand=operand)
        return self.parse_call()

    def parse_call(self) -> Node:
        """
        Handle function calls and member access  (obj.method(args))
        Chain them: cat.speak()  →  CallExpression(MemberAccess(cat, "speak"), [])
        """
        expr = self.parse_primary()

        while True:
            if self.check(TT.DOT):
                self.advance()  # consume '.'
                member = self.expect(TT.IDENT, "Expected member name after '.'.").value
                expr = MemberAccess(obj=expr, member=member)
            elif self.check(TT.LPAREN):
                self.advance()  # consume '('
                args = self.parse_args()
                self.expect(TT.RPAREN)
                expr = CallExpression(callee=expr, args=args)
            else:
                break

        return expr

    def parse_primary(self) -> Node:
        """
        Parse the most basic values: literals, identifiers, grouped expressions, 'new'.
        """
        tok = self.current

        if tok.type == TT.NUMBER:
            self.advance()
            return NumberLiteral(value=float(tok.value))

        if tok.type == TT.STRING:
            self.advance()
            return StringLiteral(value=tok.value)

        if tok.type == TT.BOOL:
            self.advance()
            return BoolLiteral(value=tok.value == "true")

        if tok.type == TT.NULL:
            self.advance()
            return NullLiteral()

        if tok.type == TT.SELF:
            self.advance()
            return Identifier(name="self")

        if tok.type == TT.IDENT:
            self.advance()
            return Identifier(name=tok.value)

        if tok.type == TT.NEW:
            return self.parse_new()

        if tok.type == TT.LPAREN:
            self.advance()  # consume '('
            expr = self.parse_expression()
            self.expect(TT.RPAREN)
            return expr

        raise SyntaxError(
            f"[AR Parser] Line {tok.line}: Unexpected token {tok.type.name} ({tok.value!r})"
        )

    def parse_new(self) -> NewExpression:
        """
        Parse:  new ClassName(args)
        Example: new Animal("Cat")
        """
        self.advance()  # consume 'new'
        class_name = self.expect(TT.IDENT, "Expected class name after 'new'.").value
        self.expect(TT.LPAREN)
        args = self.parse_args()
        self.expect(TT.RPAREN)
        return NewExpression(class_name=class_name, args=args)

    def parse_args(self) -> List[Node]:
        """
        Parse a comma-separated list of argument expressions.
        Example:  ("Ahmed", 25)  →  [StringLiteral("Ahmed"), NumberLiteral(25)]
        """
        args = []
        if not self.check(TT.RPAREN):
            args.append(self.parse_expression())
            while self.match(TT.COMMA):
                args.append(self.parse_expression())
        return args
