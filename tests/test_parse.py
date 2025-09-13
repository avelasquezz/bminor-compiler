import sys

from bminor.parser import parse, ast_to_tree
from rich import print

code1 = ""
code2 = ""
code3 = ""

try:
  with open("./examples/sieve.bminor", encoding = 'utf-8') as file:
    code1 = file.read()
except:
  print(f'[red]I/O error:[/red]', file = sys.stderr)

try:
  with open("./examples/knight.bminor", encoding = 'utf-8') as file:
    code2 = file.read()
except:
  print(f'[red]I/O error:[/red]', file = sys.stderr)

try:
  with open("./examples/mandel.bminor", encoding = 'utf-8') as file:
    code3 = file.read()
except:
  print(f'[red]I/O error:[/red]', file = sys.stderr)

ast = parse(code3)
tree = ast_to_tree(ast, "AST")
print(tree)