"""
AR Language - Environment (Variable Scope)
==========================================
What is an Environment?
  Think of it like a dictionary or a drawer for variables.
  When you write   let x = 5,  we need somewhere to store "x = 5".
  That somewhere is the Environment.

Why do we need MULTIPLE environments?
  Because of SCOPE.  Consider this code:

      let x = 10           ← x lives in the global environment

      func double(n):
          let result = n * 2   ← result lives in the function's OWN environment
          return result

      output x             ← works fine, x is global
      output result        ← ERROR! result doesn't exist out here

  This is scope — variables only exist inside the block they were created in.

How does chaining work?
  Each environment has a 'parent'.  When we look up a variable:
    1. Check this environment first.
    2. If not found, check the parent.
    3. Keep going up the chain until we find it or run out of parents.

  This naturally supports nested scopes (functions inside functions, etc.)
"""


class Environment:
    """A scoped store of variable name → value mappings."""

    def __init__(self, parent=None):
        """
        parent: the enclosing environment (None for the global scope).
        store:  the actual dictionary holding this scope's variables.
        """
        self.parent = parent
        self.store: dict = {}

    def get(self, name: str):
        """
        Look up a variable by name.
        Walks up the parent chain if not found in this scope.
        Raises a helpful error if the name doesn't exist anywhere.
        """
        if name in self.store:
            return self.store[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise NameError(f"[AR] Variable '{name}' is not defined.")

    def set(self, name: str, value):
        """
        Set a variable in THIS scope (used for 'let' declarations).
        Always creates or overwrites at the current level.
        """
        self.store[name] = value

    def assign(self, name: str, value):
        """
        Assign to an EXISTING variable (used for  x = new_value).
        Walks up the chain to find where the variable lives,
        then updates it there (not in the current scope).
        """
        if name in self.store:
            self.store[name] = value
            return
        if self.parent is not None:
            self.parent.assign(name, value)
            return
        raise NameError(f"[AR] Cannot assign to undefined variable '{name}'.")
