# bminor.py
'''
usage: main.py [-h] [-v] [--scan | --dot | --sym] [filename]

Compiler for B-Minor programs

options:
  -h, --help      show this help message and exit
  -v, --version   show programs's version number and exit

Formatting options:
  filename        B-Minor program file to compile
  --scan          Store output of lexer
  --dot           Generate AST graph as DOT format
  --sym           Dump the symbol table
'''
import argparse
import sys

from rich  import print
from bminor.lexer import tokenize
from bminor.parser import parse, ast_to_tree
from bminor.dot_render import ASTPrinter

def usage(exit_code = 1):
  print("[blue]Usage: main.py --option filename[/blue]", file = sys.stderr)
  sys.exit(exit_code)

def parse_args():
  cli = argparse.ArgumentParser(
    prog = "main.py",
    description = 'Compiler for B-Minor programs'
  )

  cli.add_argument(
    '-v', '--version',
    action = 'version',
    version = '0.1'
  )

  fgroup = cli.add_argument_group('Formatting options')

  fgroup.add_argument(
    'filename',
    type = str,
    nargs = '?',
    help = 'B-Minor program file to compile'
  )
  
  mutex = fgroup.add_mutually_exclusive_group()

  mutex.add_argument(
    '--scan',
    action = 'store_true',
    default = False,
    help = 'Store output to lexer'
  )

  mutex.add_argument(
    '--dot',
    action = 'store_true',
    default = False,
    help = 'Generate AST graph as DOT format'
  )

  return cli.parse_args()

def main():
  if len(sys.argv) == 1:
    usage()

  args = parse_args()

  if not args.filename:
    print('[red]Error: missing filename[/red]', file = sys.stderr)
    sys.exit(2)

  filename = args.filename

  try:
    with open(filename, encoding = 'utf-8') as file:
      source = file.read()

      if args.scan:
        tokenize(source)
      elif args.dot:
        print(f"[bold]Source code: [magenta]{filename}[/]\n")
        ast = parse(source)
  
        tree = ast_to_tree(ast)
        print(tree)

        dot = ASTPrinter.render(ast)
        dot.render("ast.dot")

        print(f"\n[bold]The AST graph as dot format was created as [blue]./ast.dot[/] and it can be viewed in [blue]./ast.dot.pdf[/]\n")

  except:
    print(f'[red]I/O error:[/red]', file = sys.stderr)

if __name__ == '__main__':
  main()