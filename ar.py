"""
AR Language - CLI Entry Point (ar.py)
======================================
This is the front door of AR Language.
Run it two ways:

  1. Execute an .ar file:
       python ar.py examples/hello.ar

  2. Launch the interactive REPL (Read-Eval-Print Loop):
       python ar.py
     Then type AR code line by line and press Enter.
     Type  exit  to quit the REPL.

How this file works:
  1. Read the source code (from file or REPL input)
  2. Feed it to the Lexer → get a list of tokens
  3. Feed tokens to the Parser → get an AST
  4. Feed the AST to the Interpreter → execute & print results
"""

import sys
import os

# Make sure Python can find our 'src' package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E402

from src.lexer import Lexer  # noqa: E402
from src.parser import Parser  # noqa: E402
from src.interpreter import Interpreter  # noqa: E402


def run_source(source: str, interpreter: Interpreter):
    """
    The core pipeline: source code → tokens → AST → execute.
    Any errors (syntax, name, runtime) are caught and shown nicely.
    """
    try:
        # Step 1: Lexer — break source into tokens
        tokens = Lexer(source).tokenize()

        # Step 2: Parser — build the AST from tokens
        ast = Parser(tokens).parse()

        # Step 3: Interpreter — walk the AST and run it
        interpreter.run(ast)

    except SyntaxError as e:
        print(f"\n  ❌ Syntax Error: {e}\n")
    except NameError as e:
        print(f"\n  ❌ Name Error: {e}\n")
    except TypeError as e:
        print(f"\n  ❌ Type Error: {e}\n")
    except AttributeError as e:
        print(f"\n  ❌ Attribute Error: {e}\n")
    except ZeroDivisionError as e:
        print(f"\n  ❌ Math Error: {e}\n")
    except RecursionError:
        print("\n  ❌ Stack Overflow: Too many nested function calls.\n")
    except Exception as e:
        print(f"\n  ❌ Runtime Error: {e}\n")


def run_file(filepath: str):
    """Read an .ar file and run it."""
    if not filepath.endswith(".ar"):
        print(f"  ⚠️  Warning: '{filepath}' does not have a .ar extension.")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"\n  ❌ File not found: '{filepath}'\n")
        sys.exit(1)

    interpreter = Interpreter()
    run_source(source, interpreter)


def run_repl():
    """
    Interactive REPL — Read, Eval, Print, Loop.
    Lets you type AR code directly and see results instantly.
    Great for learning and experimenting!
    """
    print("╔══════════════════════════════════════╗")
    print("║      AR Language  v1.0  —  REPL      ║")
    print("║  Type AR code.  Type 'exit' to quit. ║")
    print("╚══════════════════════════════════════╝")
    print()

    interpreter = Interpreter()  # shared state across REPL entries
    buffer = []  # accumulate multi-line blocks

    while True:
        try:
            # Show a different prompt when inside a block
            prompt = "... " if buffer else "ar> "
            line = input(prompt)

            if line.strip() == "exit":
                print("Goodbye! 👋")
                break

            buffer.append(line)

            # Try to run whatever is in the buffer
            source = "\n".join(buffer)

            # Simple heuristic: if last non-empty line ends with ':',
            # we're expecting a block — keep collecting
            stripped_lines = [line for line in buffer if line.strip()]
            if stripped_lines and stripped_lines[-1].rstrip().endswith(":"):
                continue  # wait for the block body

            # Otherwise try to run and clear buffer
            run_source(source, interpreter)
            buffer = []

        except KeyboardInterrupt:
            print("\n  (Use 'exit' to quit)")
            buffer = []
        except EOFError:
            print("\nGoodbye! 👋")
            break


# ── Entry point ─────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) == 2:
        # A file path was provided — run it
        run_file(sys.argv[1])
    elif len(sys.argv) == 1:
        # No arguments — start the REPL
        run_repl()
    else:
        print("Usage:")
        print("  python ar.py              → Launch interactive REPL")
        print("  python ar.py <file.ar>    → Run an AR source file")
        sys.exit(1)
