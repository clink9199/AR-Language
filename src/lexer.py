"""
AR Language - Lexer (Tokenizer)
================================
V1.1: Switched from indentation-based blocks to {} curly braces.
      output now requires parentheses: output("hello")

The Lexer reads raw AR source code and breaks it into TOKENS.

Example: the code    func add(a, b) { return a + b }
becomes these tokens:
  FUNC  IDENT("add")  LPAREN  IDENT("a")  COMMA  IDENT("b")  RPAREN
  LBRACE  RETURN  IDENT("a")  PLUS  IDENT("b")  RBRACE
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TT(Enum):
    """TT = Token Type."""

    # ── Literals ───────────────────────────────
    NUMBER   = auto()
    STRING   = auto()
    BOOL     = auto()
    NULL     = auto()

    # ── Identifier ─────────────────────────────
    IDENT    = auto()

    # ── Keywords ───────────────────────────────
    OUTPUT   = auto()
    LET      = auto()
    FUNC     = auto()
    RETURN   = auto()
    IF       = auto()
    ELSE     = auto()
    LOOP     = auto()
    FOR      = auto()
    IN       = auto()
    IMPORT   = auto()
    CLASS    = auto()
    INIT     = auto()
    NEW      = auto()
    SELF     = auto()
    AND      = auto()
    OR       = auto()
    NOT      = auto()

    # ── Operators ──────────────────────────────
    PLUS     = auto()
    MINUS    = auto()
    STAR     = auto()
    SLASH    = auto()
    EQ_EQ    = auto()
    BANG_EQ  = auto()
    LT       = auto()
    GT       = auto()
    LT_EQ    = auto()
    GT_EQ    = auto()
    EQUALS   = auto()

    # ── Punctuation ────────────────────────────
    LPAREN   = auto()   # (
    RPAREN   = auto()   # )
    LBRACE   = auto()   # {
    RBRACE   = auto()   # }
    LBRACKET = auto()   # [
    RBRACKET = auto()   # ]
    COMMA    = auto()   # ,
    DOT      = auto()   # .

    # ── Structure ──────────────────────────────
    NEWLINE  = auto()
    EOF      = auto()


@dataclass
class Token:
    type: TT
    value: str = ""
    line: int = 0

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, line={self.line})"


KEYWORDS: dict = {
    "output": TT.OUTPUT,
    "let":    TT.LET,
    "func":   TT.FUNC,
    "return": TT.RETURN,
    "if":     TT.IF,
    "else":   TT.ELSE,
    "loop":   TT.LOOP,
    "for":    TT.FOR,
    "in":     TT.IN,
    "import": TT.IMPORT,
    "class":  TT.CLASS,
    "init":   TT.INIT,
    "new":    TT.NEW,
    "self":   TT.SELF,
    "true":   TT.BOOL,
    "false":  TT.BOOL,
    "null":   TT.NULL,
    "and":    TT.AND,
    "or":     TT.OR,
    "not":    TT.NOT,
}


class Lexer:
    """
    Simple single-pass lexer. No more indentation tracking —
    blocks are now delimited by { and }.
    """

    def __init__(self, source: str):
        self.source = source
        self.pos    = 0
        self.line   = 1
        self.tokens: List[Token] = []

    @property
    def current_char(self) -> Optional[str]:
        return self.source[self.pos] if self.pos < len(self.source) else None

    def peek(self, offset: int = 1) -> Optional[str]:
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else None

    def advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        return ch

    def add(self, token_type: TT, value: str = ""):
        self.tokens.append(Token(token_type, value, self.line))

    def tokenize(self) -> List[Token]:
        """Single pass — read every character until EOF."""
        while self.current_char is not None:
            ch = self.current_char

            # ── Newline ──────────────────────────────
            if ch == "\n":
                self.advance()
                self.line += 1
                # Only add NEWLINE if there's a meaningful previous token
                if self.tokens and self.tokens[-1].type not in (
                    TT.NEWLINE, TT.LBRACE, TT.RBRACE
                ):
                    self.add(TT.NEWLINE)

            # ── Carriage return (Windows \r\n) ────────
            elif ch == "\r":
                self.advance()

            # ── Whitespace / Tab (skip) ───────────────
            elif ch in (" ", "\t"):
                self.advance()

            # ── Comment (## ...) ─────────────────────
            elif ch == "#" and self.peek() == "#":
                while self.current_char and self.current_char != "\n":
                    self.advance()

            # ── String ───────────────────────────────
            elif ch == '"':
                self._read_string()

            # ── Number ───────────────────────────────
            elif ch.isdigit():
                self._read_number()

            # ── Identifier / keyword ──────────────────
            elif ch.isalpha() or ch == "_":
                self._read_identifier()

            # ── Two-character operators ───────────────
            elif ch == "=" and self.peek() == "=":
                self.advance(); self.advance(); self.add(TT.EQ_EQ, "==")
            elif ch == "!" and self.peek() == "=":
                self.advance(); self.advance(); self.add(TT.BANG_EQ, "!=")
            elif ch == "<" and self.peek() == "=":
                self.advance(); self.advance(); self.add(TT.LT_EQ, "<=")
            elif ch == ">" and self.peek() == "=":
                self.advance(); self.advance(); self.add(TT.GT_EQ, ">=")

            # ── Single-character operators / punctuation ──
            elif ch == "=":  self.advance(); self.add(TT.EQUALS,  "=")
            elif ch == "+":  self.advance(); self.add(TT.PLUS,    "+")
            elif ch == "-":  self.advance(); self.add(TT.MINUS,   "-")
            elif ch == "*":  self.advance(); self.add(TT.STAR,    "*")
            elif ch == "/":  self.advance(); self.add(TT.SLASH,   "/")
            elif ch == "<":  self.advance(); self.add(TT.LT,      "<")
            elif ch == ">":  self.advance(); self.add(TT.GT,      ">")
            elif ch == "(":  self.advance(); self.add(TT.LPAREN,  "(")
            elif ch == ")":  self.advance(); self.add(TT.RPAREN,  ")")
            elif ch == "{":  self.advance(); self.add(TT.LBRACE,  "{")
            elif ch == "}":  self.advance(); self.add(TT.RBRACE,  "}")
            elif ch == "[":  self.advance(); self.add(TT.LBRACKET, "[")
            elif ch == "]":  self.advance(); self.add(TT.RBRACKET, "]")
            elif ch == ",":  self.advance(); self.add(TT.COMMA,   ",")
            elif ch == ".":  self.advance(); self.add(TT.DOT,     ".")

            else:
                raise SyntaxError(
                    f"[AR Lexer] Unknown character {ch!r} on line {self.line}"
                )

        self.add(TT.EOF)
        return self.tokens

    def _read_string(self):
        self.advance()  # skip opening "
        chars = []
        while self.current_char is not None and self.current_char != '"':
            if self.current_char == "\\":
                self.advance()
                esc = self.current_char
                if esc == "n":   chars.append("\n")
                elif esc == "t": chars.append("\t")
                else:            chars.append(esc)
            else:
                chars.append(self.current_char)
            self.advance()
        self.advance()  # skip closing "
        self.add(TT.STRING, "".join(chars))

    def _read_number(self):
        chars = []
        while self.current_char is not None and (
            self.current_char.isdigit() or self.current_char == "."
        ):
            chars.append(self.current_char)
            self.advance()
        self.add(TT.NUMBER, "".join(chars))

    def _read_identifier(self):
        chars = []
        while self.current_char is not None and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            chars.append(self.current_char)
            self.advance()
        word = "".join(chars)
        token_type = KEYWORDS.get(word, TT.IDENT)
        self.add(token_type, word)
