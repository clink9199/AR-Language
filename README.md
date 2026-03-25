<h1 align="center">AR Language</h1>
<p align="center">A modern, object-oriented programming language built from scratch.</p>
<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" />
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey" />
  <img src="https://img.shields.io/badge/license-MIT-green" />
</p>

---

## Install (Windows)

**One command in PowerShell:**
```powershell
irm https://raw.githubusercontent.com/clink9199/AR-Language/main/install.ps1 | iex
```
> Replace `clink9199` with your GitHub username. Open a new terminal after installing.

**Or download manually:** grab `ar.exe` from the [Releases](https://github.com/clink9199/AR-Language/releases) page and add it to your PATH.

---

## Usage

```powershell
ar hello.ar          # run a file
ar                   # launch interactive shell (REPL)
```

---

## Language Reference

### Output
```ar
output "Hello, World!"
```

### Variables
```ar
let name    = "Ahmed"
let version = 1
let active  = true
let nothing = null
```

### Arithmetic & Comparison
```ar
let sum  = 10 + 5
let same = (5 == 5)    ## true
let big  = (10 > 3)    ## true
```

### If / Else
```ar
if age >= 18:
    output "Adult"
else:
    output "Minor"
```

### Loop
```ar
let i = 0
loop i < 5:
    output i
    i = i + 1
```

### Functions
```ar
func add(a, b):
    return a + b

output add(10, 20)
```

### Classes (OOP)
```ar
class Person:
    init(self, name, age):
        self.name = name
        self.age  = age

    func greet(self):
        output "Hi! I am " + self.name

let p = new Person("Ahmed", 20)
p.greet()
```

### Comments
```ar
## This is a comment
```

---

## VS Code Extension

1. Download `ar-language-1.0.0.vsix` from [Releases](https://github.com/clink9199/AR-Language/releases)
2. In VS Code: `Ctrl+Shift+P` → `Extensions: Install from VSIX...`
3. Select the downloaded file → **Done!**

---

## Project Structure

```
ar-language/
├── ar.py               ← CLI entry point
├── install.ps1         ← Windows one-command installer
├── src/
│   ├── lexer.py        ← Tokenizer
│   ├── parser.py       ← AST builder
│   ├── ast_nodes.py    ← Node definitions
│   ├── environment.py  ← Variable scoping
│   └── interpreter.py  ← Tree-walking executor
├── vscode-extension/   ← Syntax highlighting extension
│   └── ar-language-1.0.0.vsix
└── examples/
    ├── hello.ar
    ├── oop_demo.ar
    └── fibonacci.ar
```

---

## Requirements (for building from source)

- Python 3.8+
- No external libraries needed

```powershell
python ar.py examples/hello.ar
```

---

## License

MIT
