<h1 align="center">AR Language</h1>
<p align="center">A modern, object-oriented programming language built from scratch.</p>
<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue" />
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey" />
  <img src="https://img.shields.io/badge/license-MIT-green" />
</p>

---

## Install (Windows)

**One command in PowerShell:**
```powershell
irm https://raw.githubusercontent.com/clink9199/AR-Language/main/install.ps1 | iex
```
> Open a new terminal after installing.

**Or download manually:** grab `ar.exe` from the [Releases](https://github.com/clink9199/AR-Language/releases) page and add it to your PATH.

---

## 🚀 New in V2!
- **Arrays & Indexing**: `[1, 2, 3]` and `arr[0]`
- **Built-in native methods**: `.push()`, `.length()`, `.split()`, `.upper()`
- **For-each loops**: `for item in arr { ... }`
- **Modules & Imports**: `import "file.ar"`

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
output("Hello, World!")
```

### Variables & Data Types
```ar
let name    = "Ahmed"
let version = 2
let stable  = true
let nothing = null
```

### Arrays
```ar
let nums = [10, 20, 30]
nums[1] = 99
nums.push(40)
output(nums.length())  ## Prints 4
```

### String Methods
```ar
let msg = "hello world"
output(msg.upper())    ## HELLO WORLD
output(msg.split(" ")) ## [hello, world]
```

### Arithmetic & Comparison
```ar
let sum  = 10 + 5
let same = (5 == 5)    ## true
let big  = (10 > 3)    ## true
```

### If / Else
```ar
if age >= 18 {
    output("Adult")
} else {
    output("Minor")
}
```

### Loops
```ar
## Loop (While-style)
let i = 0
loop i < 5 {
    output(i)
    i = i + 1
}

## For Loop (ForEach-style)
let names = ["Ahmed", "Sarah", "John"]
for name in names {
    output("Hello " + name)
}
```

### Functions
```ar
func add(a, b) {
    return a + b
}

output(add(10, 20))
```

### Classes (OOP)
```ar
class Person {
    init(self, name, age) {
        self.name = name
        self.age  = age
    }

    func greet(self) {
        output("Hi! I am " + self.name)
    }
}

let p = new Person("Ahmed", 20)
p.greet()
```

### Imports
```ar
## Imports another .ar file into the current scope
import "math_util.ar"
```

### Comments
```ar
## This is a comment
```

---

## VS Code Extension

1. Download `ar-language-1.1.0.vsix` from [Releases](https://github.com/clink9199/AR-Language/releases)
2. In VS Code: `Ctrl+Shift+P` → `Extensions: Install from VSIX...`
3. Select the downloaded file → **Reload Window**

---

## License

MIT
