"""
AR Language - Lexer (Tokenizer)
================================
What is a Lexer?
  Imagine you're reading a sentence:  "The cat sat on the mat"
  Your brain automatically breaks it into words.  That's exactly what a Lexer does.
  It reads raw AR source code (just a big string of characters) and breaks it into
  meaningful chunks called TOKENS.

  Example: the line    let x = 5 + 3
  becomes these tokens:
    Token(LET,    "let")
    Token(IDENT,  "x")
    Token(EQUALS, "=")
    Token(NUMBER, "5")
    Token(PLUS,   "+")
    Token(NUMBER, "3")
    Token(NEWLINE)

  The parser will then use these tokens (not raw text) to build the AST.

Why separate Lexer from Parser?
  Separation of concerns — each step does one job cleanly.
  The Lexer handles raw characters → tokens.
  The Parser handles tokens → structure (AST).
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


# ─────────────────────────────────────────────
#  TOKEN TYPES
#  These are all the kinds of "words" AR Language understands.
# ─────────────────────────────────────────────

class TT(Enum):
    """TT = Token Type. Every possible category of token."""

    # ── Literals ───────────────────────────────
    NUMBER   = auto()   # 42, 3.14
    STRING   = auto()   # "hello"
    BOOL     = auto()   # true, false
    NULL     = auto()   # null

    # ── Identifier ─────────────────────────────
    IDENT    = auto()   # variable / function / class names

    # ── Keywords ───────────────────────────────
    OUTPUT   = auto()   # output
    LET      = auto()   # let
    FUNC     = auto()   # func
    RETURN   = auto()   # return
    IF       = auto()   # if
    ELSE     = auto()   # else
    LOOP     = auto()   # loop
    CLASS    = auto()   # class
    INIT     = auto()   # init  (constructor)
    NEW      = auto()   # new
    SELF     = auto()   # self
    AND      = auto()   # and
    OR       = auto()   # or
    NOT      = auto()   # not

    # ── Operators ──────────────────────────────
    PLUS     = auto()   # +
    MINUS    = auto()   # -
    STAR     = auto()   # *
    SLASH    = auto()   # /
    EQ_EQ    = auto()   # ==   (equality check)
    BANG_EQ  = auto()   # !=   (not equal)
    LT       = auto()   # <
    GT       = auto()   # >
    LT_EQ    = auto()   # <=
    GT_EQ    = auto()   # >=
    EQUALS   = auto()   # =    (assignment)

    # ── Punctuation ────────────────────────────
    LPAREN   = auto()   # (
    RPAREN   = auto()   # )
    COLON    = auto()   # :
    COMMA    = auto()   # ,
    DOT      = auto()   # .

    # ── Structure ──────────────────────────────
    NEWLINE  = auto()   # end of a logical line
    INDENT   = auto()   # indentation increased
    DEDENT   = auto()   # indentation decreased
    EOF      = auto()   # end of file


# ─────────────────────────────────────────────
#  TOKEN dataclass
#  A token wraps its type AND the actual text from the source code.
# ─────────────────────────────────────────────

@dataclass
class Token:
    type: TT
    value: str = ""
    line: int = 0     # which source line this came from (for error messages)

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, line={self.line})"


# ─────────────────────────────────────────────
#  KEYWORD MAP
#  Maps exact text → token type for all reserved words
# ─────────────────────────────────────────────

KEYWORDS: dict = {
    "output": TT.OUTPUT,
    "let":    TT.LET,
    "func":   TT.FUNC,
    "return": TT.RETURN,
    "if":     TT.IF,
    "else":   TT.ELSE,
    "loop":   TT.LOOP,
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


# ─────────────────────────────────────────────
#  LEXER CLASS
# ─────────────────────────────────────────────

class Lexer:
    """
    Reads source code character by character and produces a flat list of tokens.

    How it works:
      1. We keep a 'pos' (position) cursor that starts at 0.
      2. We look at the current character (self.current_char).
      3. Based on what we see, we decide what token to create.
      4. We advance 'pos' past the characters we consumed.
      5. Repeat until we hit the end of the file.
    """

    def __init__(self, source: str):
        self.source = source          # the entire AR source code as a string
        self.pos    = 0               # current character position
        self.line   = 1               # current line number (for error messages)
        self.tokens: List[Token] = [] # output list

        # Indentation stack: tracks how deep we currently are.
        # We start with 0 (no indentation = top level).
        self.indent_stack: List[int] = [0]

    # ── Helpers ──────────────────────────────────────────

    @property
    def current_char(self) -> Optional[str]:
        """The character at the current position, or None at end of file."""
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def peek(self, offset: int = 1) -> Optional[str]:
        """Look ahead without moving the cursor."""
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return None

    def advance(self) -> str:
        """Move one character forward and return the character we just left."""
        ch = self.source[self.pos]
        self.pos += 1
        return ch

    def add(self, token_type: TT, value: str = ""):
        """Add a token to our output list."""
        self.tokens.append(Token(token_type, value, self.line))

    # ── Main tokenize method ──────────────────────────────

    def tokenize(self) -> List[Token]:
        """
        Main entry point.
        Processes the source code line by line to handle indentation correctly,
        then returns the full token list.
        """
        lines = self.source.splitlines(keepends=True)

        for line in lines:
            self._process_line(line)

        # Close any remaining open indentation levels
        while self.indent_stack[-1] > 0:
            self.indent_stack.pop()
            self.add(TT.DEDENT)

        self.add(TT.EOF)
        return self.tokens

    def _process_line(self, line: str):
        """Process a single line of source code."""
        # Skip fully blank lines and comment lines
        stripped = line.strip()
        if not stripped or stripped.startswith("##"):
            self.line += 1
            return

        # Count leading spaces to determine indentation level
        indent = len(line) - len(line.lstrip(" "))

        # Compare indent to the top of the stack
        current_indent = self.indent_stack[-1]

        if indent > current_indent:
            # We went deeper — emit INDENT token
            self.indent_stack.append(indent)
            self.add(TT.INDENT)
        elif indent < current_indent:
            # We came back out — emit DEDENT(s) until we match
            while self.indent_stack[-1] > indent:
                self.indent_stack.pop()
                self.add(TT.DEDENT)

        # Now tokenize the actual content of this line
        self.pos = self._offset_in_source(line)
        end = self.pos + len(line.rstrip("\n").rstrip("\r"))

        self._tokenize_segment(self.pos, end)

        self.add(TT.NEWLINE)
        self.line += 1

    def _offset_in_source(self, line: str) -> int:
        """Find where this line starts in the full source string."""
        # Walk through the source to find the current line start
        pos = 0
        current_line = 1
        while current_line < self.line and pos < len(self.source):
            if self.source[pos] == "\n":
                current_line += 1
            pos += 1
        return pos

    def _tokenize_segment(self, start: int, end: int):
        """Tokenize characters from start to end."""
        self.pos = start

        while self.pos < end:
            ch = self.current_char

            # ── Whitespace (skip) ────────────
            if ch in (" ", "\t"):
                self.advance()

            # ── Comment (## ...) ────────────
            elif ch == "#" and self.peek() == "#":
                break  # rest of line is a comment, stop

            # ── String literal ────────────────
            elif ch == '"':
                self._read_string()

            # ── Number literal ────────────────
            elif ch.isdigit():
                self._read_number()

            # ── Identifier or keyword ─────────
            elif ch.isalpha() or ch == "_":
                self._read_identifier()

            # ── Two-character operators ────────
            elif ch == "=" and self.peek() == "=":
                self.advance(); self.advance()
                self.add(TT.EQ_EQ, "==")
            elif ch == "!" and self.peek() == "=":
                self.advance(); self.advance()
                self.add(TT.BANG_EQ, "!=")
            elif ch == "<" and self.peek() == "=":
                self.advance(); self.advance()
                self.add(TT.LT_EQ, "<=")
            elif ch == ">" and self.peek() == "=":
                self.advance(); self.advance()
                self.add(TT.GT_EQ, ">=")

            # ── Single character operators/punctuation ──
            elif ch == "=":  self.advance(); self.add(TT.EQUALS, "=")
            elif ch == "+":  self.advance(); self.add(TT.PLUS,   "+")
            elif ch == "-":  self.advance(); self.add(TT.MINUS,  "-")
            elif ch == "*":  self.advance(); self.add(TT.STAR,   "*")
            elif ch == "/":  self.advance(); self.add(TT.SLASH,  "/")
            elif ch == "<":  self.advance(); self.add(TT.LT,     "<")
            elif ch == ">":  self.advance(); self.add(TT.GT,     ">")
            elif ch == "(":  self.advance(); self.add(TT.LPAREN, "(")
            elif ch == ")":  self.advance(); self.add(TT.RPAREN, ")")
            elif ch == ":":  self.advance(); self.add(TT.COLON,  ":")
            elif ch == ",":  self.advance(); self.add(TT.COMMA,  ",")
            elif ch == ".":  self.advance(); self.add(TT.DOT,    ".")

            else:
                raise SyntaxError(
                    f"[AR Lexer] Unknown character {ch!r} on line {self.line}"
                )

    def _read_string(self):
        """
        Read a string literal enclosed in double quotes.
        Example:  "Hello, World!"
        We skip the opening quote, collect characters until the closing quote.
        """
        self.advance()  # skip opening "
        chars = []
        while self.current_char is not None and self.current_char != '"':
            if self.current_char == "\\":
                # Handle escape sequences like \n (newline) and \t (tab)
                self.advance()
                esc = self.current_char
                if esc == "n":  chars.append("\n")
                elif esc == "t": chars.append("\t")
                else:           chars.append(esc)
            else:
                chars.append(self.current_char)
            self.advance()
        self.advance()  # skip closing "
        self.add(TT.STRING, "".join(chars))

    def _read_number(self):
        """
        Read an integer or decimal number.
        Example:  42   or   3.14
        """
        chars = []
        while self.current_char is not None and (
            self.current_char.isdigit() or self.current_char == "."
        ):
            chars.append(self.current_char)
            self.advance()
        self.add(TT.NUMBER, "".join(chars))

    def _read_identifier(self):
        """
        Read an identifier (variable name, keyword, etc.)
        Example:  output   name   MyClass   self
        After reading, we check if it's a keyword — if so, use the keyword token type.
        """
        chars = []
        while self.current_char is not None and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            chars.append(self.current_char)
            self.advance()
        word = "".join(chars)

        # Is it a reserved keyword?
        token_type = KEYWORDS.get(word, TT.IDENT)
        self.add(token_type, word)
