from bminor.semantic.typesys import typenames, check_binop, check_unaryop, CheckError
from bminor.semantic.symtab  import Symtab
from bminor.parser.model     import *
from bminor.errors           import error, errors_detected

from typing import Union, List
from rich   import print

if_counter = 0
while_counter = 0
for_counter = 0
do_while_counter = 0

class Check(Visitor):
  @classmethod
  def checker(cls, n: Program):
    checker = cls()
    env = Symtab('global')

    for decl in n.body:
      decl.accept(checker, env)

    return env

  def visit(self, n: VarDecl, env: Symtab):
    if n.value:
      n.value.accept(self, env)

      if hasattr(n.value, "type"):
        if check_binop('=', n.type, n.value.type) is None:
          error(f"Types do not match in '{n.name}'", n.lineno, "Semantic")
        
    try:
      env.add(n.name, n)
    except Symtab.SymbolConflictError:
      error(f"'{n.name}' has already been declared with a different type", n.lineno, "Semantic")
    except Symtab.SymbolDefinedError:
      error(f"'{n.name}' has already been declared", n.lineno, "Semantic")
  
  def visit(self, n: ArrayDecl, env: Symtab):
    if n.size:
      n.size.accept(self, env)
    else:
      error(f"'{n.name}' must have size", n.lineno, "Semantic")

    if hasattr(n.size, "type"):
      if n.size.type != "integer":
        error(f"Size of '{n.name}' must be an integer", n.lineno, "Semantic")
    
    if n.value:
      for value in n.value:
        value.accept(self, env)

        if hasattr(value, "type"):
          if value.type != n.type:
            error(f"All elements of '{n.name}' must be '{n.type}'", n.lineno, "Semantic")
            break
    
    try:
      env.add(n.name, n)
    except Symtab.SymbolConflictError:
      error(f"'{n.name}' has already been declared with a different type", n.lineno, "Semantic")
    except Symtab.SymbolDefinedError:
      error(f"'{n.name}' has already been declared", n.lineno, "Semantic")

  def visit(self, n: VarParam, env: Symtab):
    try:
      env.add(n.name, n)
    except Symtab.SymbolConflictError:
      error(f"'{n.name}' has already been declared with a different type", n.lineno, "Semantic")
    except Symtab.SymbolDefinedError:
      error(f"'{n.name}' has already been declared", n.lineno, "Semantic")
  
  def visit(self, n: ArrayParam, env: Symtab):
    if n.size:
      n.size.accept(self, env)

      if hasattr(n.size, "type"):
        if n.size.type != "integer":
          error(f"Size of '{n.name}' must be an integer", n.lineno, "Semantic")

    try:
      env.add(n.name, n)
    except Symtab.SymbolConflictError:
      error(f"'{n.name}' has already been declared with a different type", n.lineno, "Semantic")
    except Symtab.SymbolDefinedError:
      error(f"'{n.name}' has already been declared", n.lineno, "Semantic")

  def visit(self, n: FuncDecl, env: Symtab):
    try:
      env.add(n.name, n)
    except Symtab.SymbolConflictError:
      error(f"'{n.name}' has already been declared with a different type", n.lineno, "Semantic")
    except Symtab.SymbolDefinedError:
      error(f"'{n.name}' has already been declared", n.lineno, "Semantic")
    
    func_env = Symtab(n.name, env)
    func_env.has_return = False

    for param in n.params:
      param.accept(self, func_env)
    
    for stmt in n.body:
      stmt.accept(self, func_env)
    
    if len(n.body) != 0 and n.type != "void" and not getattr(func_env, "has_return", False):
      error(f"'{n.name}' must have a return", n.lineno, "Semantic")

  def visit(self, n: UnaryOper, env: Symtab):
    n.expr.accept(self, env)

    if hasattr(n, "type"):
      n.type = check_unaryop(n.oper, n.expr.type)

      if n.type is None:
        error(f"Types do not match in '{n.oper}'", n.lineno, "Semantic")
    
  def visit(self, n: BinOper, env: Symtab):
    n.left.accept(self, env)
    n.right.accept(self, env)

    if hasattr(n.left, "type") and hasattr(n.right, "type"):
      n.type = check_binop(n.oper, n.left.type, n.right.type)

      if n.type is None:
        error(f"Types do not match in '{n.oper}'", n.lineno, "Semantic")
  
  def visit(self, n: ReturnStmt, env: Symtab):
    current_env = env
    func = None

    while current_env is not None:
      if hasattr(current_env, "has_return"):  # Estamos dentro de una función
        current_env.has_return = True
        break
      current_env = current_env.parent

    while current_env is not None:
        possible = current_env.get(current_env.name)
        if possible and possible.__class__.__name__ == "FuncDecl":
            func = possible
            break
        current_env = current_env.parent

    if n.value:
      n.value.accept(self, env)

      if hasattr(n.value, "type"):
        if func.type != n.value.type:
          error(f"'{func.name}' returns a different type", n.lineno, "Semantic")
    
  def visit(self, n: Assignment, env: Symtab):
    target = env.get(n.target.name)

    if target is not None:
      n.value.accept(self, env)

      if hasattr(n.value, "type"):
        if n.value.type is not None and target.type != n.value.type:
          error(f"Types do not match in {n.target.name}", n.lineno, "Semantic")
    else:
      error(f"'{n.target.name}' is not defined", n.lineno, "Semantic")
    
  def visit(self, n: VarLoc, env: Symtab):
    symbol = env.get(n.name)

    if symbol is None:
      error(f"'{n.name}' is not defined", n.lineno, "Semantic")
      return

    if not hasattr(symbol, 'type'):
      error(f"'{n.name}' has no type information", n.lineno, "Semantic")
        
    n.type = symbol.type

  def visit(self, n: ArrayLoc, env: Symtab):
    symbol = env.get(n.name)

    if symbol is None:
      error(f"'{n.name}' is not defined", n.lineno, "Semantic")
      return

    if not hasattr(symbol, 'type'):
      error(f"'{n.name}' has no type information", n.lineno, "Semantic")
        
    n.type = symbol.type

    n.index.accept(self, env)

    if hasattr(n.index, "type"):
      if n.index.type != "integer":
        error(f"'{n.name}' index must be an integer", n.lineno, "Semantic")

  def visit(self, n: FuncCall, env: Symtab):
    symbol = env.get(n.name)
    
    if symbol is None:
      error(f"'{n.name}' is not defined", n.lineno, "Semantic")
      return

    if not hasattr(symbol, 'type'):
      error(f"'{n.name}' has no type information", n.lineno, "Semantic")
      return
    
    if len(n.args) != len(symbol.params):
      error(f"Wrong arguments in '{n.name}'", n.lineno, "Semantic")
      return

    n.type = symbol.type

    for arg in n.args:
      arg.accept(self, env)
    
    for i in range(0, len(n.args)):
      if hasattr(n.args[i], "type"):
        if n.args[i].type != symbol.params[i].type:
          error(f"Types do not match in '{n.name}' arguments", n.lineno, "Semantic")
          return
  
  def visit(self, n: BlockStmt, env: Symtab):
    for stmt in n.body:
      stmt.accept(self, env)

  def visit(self, n: IfStmt, env: Symtab):
    global if_counter
    name = f"if{if_counter}"

    if n.condition is not None:
      n.condition.accept(self, env)

      if hasattr(n.condition, "type"):
        if n.condition.type != "boolean":
          error("Condition in 'if' must be boolean", n.lineno, "Semantic")
    else:
      error("'if' must have a boolean condition", n.lineno, "Semantic")



    if_env = Symtab(name, env)
    if_counter += 1

    n.then_branch.accept(self, if_env)

    if n.else_branch:
      else_env = Symtab(f"{name}else", env)
      n.else_branch.accept(self, else_env)
  
  def visit(self, n: WhileStmt, env: Symtab):
    global while_counter
    name = f"while{while_counter}"

    if n.condition is not None:
      n.condition.accept(self, env)

      if hasattr(n.condition, "type"):
        if n.condition.type != "boolean":
          error("Condition in 'while' must be boolean", n.lineno, "Semantic")
    else:
      error("'while' must have a boolean condition", n.lineno, "Semantic")

    while_env = Symtab(name, env)
    while_counter += 1

    n.body.accept(self, while_env)
  
  def visit(self, n: ForStmt, env: Symtab):
    global for_counter
    name = f"for{for_counter}"

    if n.init is not None:
      n.init.accept(self, env)
    else:
      error("'for' must have a variable initialization", n.lineno, "Semantic")

    if n.condition is not None:
      n.condition.accept(self, env)

      if hasattr(n.condition, "type"):
        if n.condition.type != "boolean":
          error("Condition in 'for' must be boolean", n.lineno, "Semantic")
    else:
      error("'for' must have a boolean condition", n.lineno, "Semantic")

    if n.incr is not None:
      n.incr.accept(self, env)
    else:
      error("'for' must have a variable increment or decrement", n.lineno, "Semantic")

    for_env = Symtab(name, env)
    for_counter += 1

    n.body.accept(self, for_env)

  def visit(self, n: DoWhileStmt, env: Symtab):
    global do_while_counter
    name = f"do_while{do_while_counter}"

    if n.condition is not None:
      n.condition.accept(self, env)

      if hasattr(n.condition, "type"):
        if n.condition.type != "boolean":
          error("Condition in 'do-while' must be boolean", n.lineno, "Semantic")
    else:
      error("'do-while' must have a boolean condition", n.lineno, "Semantic")

    do_while_env = Symtab(name, env)
    do_while_counter += 1

    n.body.accept(self, do_while_env)
  
  def visit(self, n: PrintStmt, env: Symtab):
    for v in n.value:
      v.accept(self, env)

  def visit(self, n: Node, env: Symtab):
    # print(f"Node '{n.__class__.__name__}' not implemented")
    pass

if __name__ == '__main__':
  import sys
  from bminor.parser import parse

  if len(sys.argv) != 2:
	  raise SystemExit("Usage: python checker.py <filename>")

  code = open(sys.argv[1], encoding='utf-8').read()
  ast = parse(code)

  Check.checker(ast)