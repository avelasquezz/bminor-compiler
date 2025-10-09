from rich import print
from typing import Union, List
from bminor.errors import error, errors_detected
from bminor.model import *
from bminor.symtab import Symtab
from bminor.typesys import typenames, check_binop, check_unaryop, CheckError

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

      if check_binop('=', n.type, n.value.type) is None:
        error(f"Types do not match in '{n.name}'", n.lineno, "Semantic")
        
    try:
      env.add(n.name, n)
    except Symtab.SymbolConflictError:
      error(f"'{n.name}' has already been declared with a different type", n.lineno, "Semantic")
    except Symtab.SymbolDefinedError:
      error(f"'{n.name}' has already been declared", n.lineno, "Semantic")
  
  def visit(self, n: ArrayDecl, env: Symtab):
    n.size.accept(self, env)

    if n.size.type != "integer":
      error(f"Size of '{n.name}' must be an integer", n.lineno, "Semantic")
    
    if n.value:
      for value in n.value:
        value.accept(self, env)

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
    except Symtab.SymbolConflictErrorenv.get(n.name):
      error(f"'{n.name}' has already been declared with a different type", n.lineno, "Semantic")
    except Symtab.SymbolDefinedError:
      error(f"'{n.name}' has already been declared", n.lineno, "Semantic")
  
  def visit(self, n: ArrayParam, env: Symtab):
    pass

  def visit(self, n: FuncDecl, env: Symtab):
    try:
      env.add(n.name, n)
    except Symtab.SymbolConflictError:
      error(f"'{n.name}' has already been declared with a different type", n.lineno, "Semantic")
    except Symtab.SymbolDefinedError:
      error(f"'{n.name}' has already been declared", n.lineno, "Semantic")
    
    func_env = Symtab(n.name, env)

    for param in n.params:
      param.accept(self, func_env)

    for stmt in n.body:
      stmt.accept(self, func_env)
  
  def visit(self, n: UnaryOper, env: Symtab):
    n.expr.accept(self, env)

    n.type = check_unaryop(n.oper, n.expr.type)

    if n.type is None:
      error(f"Types do not match in '{n.oper}'", n.lineno, "Semantic")
    
  def visit(self, n: BinOper, env: Symtab):
    n.left.accept(self, env)
    n.right.accept(self, env)

    n.type = check_binop(n.oper, n.left.type, n.right.type)

    if n.type is None:
      error(f"Types do not match in '{n.oper}'", n.lineno, "Semantic")
  
  def visit(self, n: ReturnStmt, env: Symtab):
    func = env.get(env.name)

    if n.value:
      n.value.accept(self, env)

      if func.type != n.value.type:
        error(f"'{func.name}' returns a different type", n.lineno, "Semantic")
  
  def visit(self, n: Assignment, env: Symtab):
    target = env.get(n.target.name)

    if target is not None:
      n.value.accept(self, env)

      if n.value.type is not None and target.type != n.value.type:
        error(f"Types do not match in {n.target.name}", n.lineno, "Semantic")
    else:
      error(f"'{n.target.name}' is not defined", n.lineno, "Semantic")
    
  def visit(self, n: VarLoc, env: Symtab):
    symbol = env.get(n.name)

    if symbol is None:
      error(f"'{n.name}' is not defined", n.lineno, "Semantic")
    else:
      if hasattr(symbol, 'type'):
        n.type = symbol.type
      else:
        error(f"'{n.name}' has no type information", n.lineno, "Semantic")
  
  def visit(self, n: Node, env: Symtab):
    # env.print()
    pass

if __name__ == '__main__':
  import sys
  from bminor.parser import parse

  if len(sys.argv) != 2:
	  raise SystemExit("Usage: python checker.py <filename>")

  code = open(sys.argv[1], encoding='utf-8').read()
  ast = parse(code)

  Check.checker(ast)