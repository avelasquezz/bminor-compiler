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
      if check_binop('=', n.type, n.value.type if hasattr(n.value, "type") else n.value.accept(self, env)) is None:
        error(f"Types do not match in '{n.name}'", n.lineno, "Semantic")
        
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

    for stmt in n.body:
      stmt.accept(self, func_env)
    
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
        error(f"Function '{func.name}' returns a different type", n.lineno, "Semantic")
    
  def visit(self, n: VarLoc, env: Symtab):
    n.type = env.get(n.name)

    if n.type is None:
      error(f"'{n.name}' is not defined", n.lineno, "Semantic")
  
  def visit(self, n: Node, env: Symtab):
    pass

if __name__ == '__main__':
  import sys
  from bminor.parser import parse

  if len(sys.argv) != 2:
	  raise SystemExit("Usage: python checker.py <filename>")

  code = open(sys.argv[1], encoding='utf-8').read()
  ast = parse(code)

  Check.checker(ast)