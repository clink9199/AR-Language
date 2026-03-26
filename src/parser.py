"""
AR Language - Parser (V1.1)
============================
Updated for {} block syntax and output() with parentheses.

New syntax:
    func add(a, b) {
        return a + b
    }

    if x > 5 {
        output("big")
    } else {
        output("small")
    }

    class Animal {
        init(self, name) {
            self.name = name
        }
        func speak(self) {
            output(self.name)
        }
    }
"""

from typing import List
from src.lexer import Token, TT
from src.ast_nodes import (
    Node,
    Program,
    NumberLiteral,
    StringLiteral,
    BoolLiteral,
    NullLiteral,
    ArrayLiteral,
    Identifier,
    BinaryOp,
    UnaryOp,
    MemberAccess,
    IndexAccess,
    CallExpression,
    NewExpression,
    ExpressionStatement,
    OutputStatement,
    LetStatement,
    AssignStatement,
    IndexAssignment,
    ReturnStatement,
    IfStatement,
    LoopStatement,
    ForStatement,
    ImportStatement,
    FuncDefinition,
    ClassDefinition,
)


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # ── Token helpers ─────────────────────────────────────────────

    @property
    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def check(self, *types: TT) -> bool:
        return self.current.type in types

    def match(self, *types: TT) -> bool:
        if self.check(*types):
            self.advance()
            return True
        return False

    def expect(self, token_type: TT, msg: str = "") -> Token:
        if not self.check(token_type):
            raise SyntaxError(
                f"[AR Parser] Line {self.current.line}: "
                f"Expected {token_type.name}, got {self.current.type.name} "
                f"({self.current.value!r}). {msg}"
            )
        return self.advance()

    def skip_newlines(self):
        while self.check(TT.NEWLINE):
            self.advance()

    # ── Program ───────────────────────────────────────────────────

    def parse(self) -> Program:
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
        tok = self.current

        if tok.type == TT.OUTPUT:
            return self.parse_output()
        if tok.type == TT.LET:
            return self.parse_let()
        if tok.type == TT.RETURN:
            return self.parse_return()
        if tok.type == TT.IF:
            return self.parse_if()
        if tok.type == TT.LOOP:
            return self.parse_loop()
        if tok.type == TT.FOR:
            return self.parse_for()
        if tok.type == TT.IMPORT:
            return self.parse_import()
        if tok.type == TT.FUNC:
            return self.parse_func()
        if tok.type == TT.CLASS:
            return self.parse_class()
        return self.parse_expression_statement()

    def parse_output(self) -> OutputStatement:
        """
        output("Hello, World!")
        Requires parentheses around the value.
        """
        self.advance()  # consume 'output'
        self.expect(TT.LPAREN, "output requires parentheses: output(value)")
        value = self.parse_expression()
        self.expect(TT.RPAREN)
        self.match(TT.NEWLINE)
        return OutputStatement(value=value)

    def parse_let(self) -> LetStatement:
        self.advance()  # consume 'let'
        name = self.expect(TT.IDENT, "Expected variable name after 'let'.").value
        self.expect(TT.EQUALS)
        value = self.parse_expression()
        self.match(TT.NEWLINE)
        return LetStatement(name=name, value=value)

    def parse_return(self) -> ReturnStatement:
        self.advance()  # consume 'return'
        if self.check(TT.NEWLINE, TT.RBRACE, TT.EOF):
            self.match(TT.NEWLINE)
            return ReturnStatement()
        value = self.parse_expression()
        self.match(TT.NEWLINE)
        return ReturnStatement(value=value)

    def parse_if(self) -> IfStatement:
        """
        if condition {
            ...
        } else {
            ...
        }
        """
        self.advance()  # consume 'if'
        condition = self.parse_expression()
        then_body = self.parse_block()
        else_body = []

        self.skip_newlines()
        if self.check(TT.ELSE):
            self.advance()  # consume 'else'
            else_body = self.parse_block()

        return IfStatement(
            condition=condition, then_body=then_body, else_body=else_body
        )

    def parse_loop(self) -> LoopStatement:
        """
        loop condition {
            ...
        }
        """
        self.advance()  # consume 'loop'
        condition = self.parse_expression()
        body = self.parse_block()
        return LoopStatement(condition=condition, body=body)

    def parse_for(self) -> ForStatement:
        """
        for item in iterable {
            ...
        }
        """
        self.advance()  # consume 'for'
        iterator_name = self.expect(TT.IDENT, "Expected iterator name.").value
        self.expect(TT.IN, "Expected 'in' after iterator name.")
        iterable = self.parse_expression()
        body = self.parse_block()
        return ForStatement(iterator_name=iterator_name, iterable=iterable, body=body)

    def parse_import(self) -> ImportStatement:
        """
        import "math.ar"
        """
        self.advance()  # consume 'import'
        filepath = self.expect(
            TT.STRING, "Expected string file path after 'import'."
        ).value
        self.match(TT.NEWLINE)
        return ImportStatement(filepath=filepath)

    def parse_func(self) -> FuncDefinition:
        """
        func name(params) {
            ...
        }
        """
        self.advance()  # consume 'func'
        name = self.expect(TT.IDENT, "Expected function name.").value
        self.expect(TT.LPAREN)
        params = self.parse_params()
        self.expect(TT.RPAREN)
        body = self.parse_block()
        return FuncDefinition(name=name, params=params, body=body)

    def parse_class(self) -> ClassDefinition:
        """
        class Name {
            init(self, ...) { ... }
            func method(self) { ... }
        }
        """
        self.advance()  # consume 'class'
        name = self.expect(TT.IDENT, "Expected class name.").value
        self.expect(TT.LBRACE)
        methods = []
        self.skip_newlines()

        while not self.check(TT.RBRACE) and not self.check(TT.EOF):
            if self.check(TT.INIT):
                self.advance()  # consume 'init'
                self.expect(TT.LPAREN)
                params = self.parse_params()
                self.expect(TT.RPAREN)
                body = self.parse_block()
                methods.append(FuncDefinition(name="init", params=params, body=body))
            elif self.check(TT.FUNC):
                methods.append(self.parse_func())
            else:
                self.advance()
            self.skip_newlines()

        self.expect(TT.RBRACE)
        return ClassDefinition(name=name, methods=methods)

    def parse_expression_statement(self) -> Node:
        expr = self.parse_expression()
        if self.check(TT.EQUALS):
            self.advance()
            value = self.parse_expression()
            self.match(TT.NEWLINE)
            if isinstance(expr, IndexAccess):
                return IndexAssignment(obj=expr.obj, index=expr.index, value=value)
            return AssignStatement(target=expr, value=value)
        self.match(TT.NEWLINE)
        return ExpressionStatement(expression=expr)

    # ── Block parsing — now uses { } ─────────────────────────────

    def parse_block(self) -> List[Node]:
        """
        A block is  { statement* }
        Newlines inside are skipped freely.
        """
        self.skip_newlines()
        self.expect(TT.LBRACE)
        statements = []
        self.skip_newlines()

        while not self.check(TT.RBRACE) and not self.check(TT.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()

        self.expect(TT.RBRACE)
        self.match(TT.NEWLINE)
        return statements

    # ── Params / Args ─────────────────────────────────────────────

    def parse_params(self) -> List[str]:
        params = []
        if self.check(TT.SELF, TT.IDENT):
            params.append(self.advance().value)
            while self.match(TT.COMMA):
                if self.check(TT.SELF, TT.IDENT):
                    params.append(self.advance().value)
        return params

    # ── Expression hierarchy (unchanged) ─────────────────────────

    def parse_expression(self) -> Node:
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
        while self.check(TT.STAR, TT.SLASH, TT.PERCENT):
            op = self.advance().value
            right = self.parse_unary()
            left = BinaryOp(left=left, op=op, right=right)
        return left

    def parse_unary(self) -> Node:
        if self.check(TT.NOT):
            op = self.advance().value
            return UnaryOp(op=op, operand=self.parse_unary())
        if self.check(TT.MINUS):
            op = self.advance().value
            return UnaryOp(op=op, operand=self.parse_unary())
        return self.parse_call()

    def parse_call(self) -> Node:
        expr = self.parse_primary()
        while True:
            if self.check(TT.DOT):
                self.advance()
                member = self.expect(TT.IDENT, "Expected member name after '.'.").value
                expr = MemberAccess(obj=expr, member=member)
            elif self.check(TT.LPAREN):
                self.advance()
                args = self.parse_args()
                self.expect(TT.RPAREN)
                expr = CallExpression(callee=expr, args=args)
            elif self.check(TT.LBRACKET):
                self.advance()
                index = self.parse_expression()
                self.expect(TT.RBRACKET)
                expr = IndexAccess(obj=expr, index=index)
            else:
                break
        return expr

    def parse_primary(self) -> Node:
        tok = self.current

        if tok.type == TT.NUMBER:
            self.advance()
            return NumberLiteral(float(tok.value))
        if tok.type == TT.STRING:
            self.advance()
            return StringLiteral(tok.value)
        if tok.type == TT.BOOL:
            self.advance()
            return BoolLiteral(tok.value == "true")
        if tok.type == TT.NULL:
            self.advance()
            return NullLiteral()
        if tok.type == TT.SELF:
            self.advance()
            return Identifier("self")
        if tok.type == TT.IDENT:
            self.advance()
            return Identifier(tok.value)
        if tok.type == TT.NEW:
            return self.parse_new()
        if tok.type == TT.LBRACKET:
            return self.parse_array_literal()

        if tok.type == TT.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TT.RPAREN)
            return expr

        raise SyntaxError(
            f"[AR Parser] Line {tok.line}: Unexpected token {tok.type.name} ({tok.value!r})"
        )

    def parse_array_literal(self) -> ArrayLiteral:
        self.advance()  # consume '['
        elements = []
        if not self.check(TT.RBRACKET):
            elements.append(self.parse_expression())
            while self.match(TT.COMMA):
                elements.append(self.parse_expression())
        self.expect(TT.RBRACKET)
        return ArrayLiteral(elements=elements)

    def parse_new(self) -> NewExpression:
        self.advance()  # consume 'new'
        class_name = self.expect(TT.IDENT, "Expected class name after 'new'.").value
        self.expect(TT.LPAREN)
        args = self.parse_args()
        self.expect(TT.RPAREN)
        return NewExpression(class_name=class_name, args=args)

    def parse_args(self) -> List[Node]:
        args = []
        if not self.check(TT.RPAREN):
            args.append(self.parse_expression())
            while self.match(TT.COMMA):
                args.append(self.parse_expression())
        return args
