from core.parser.model import *

from graphviz import Digraph

class ASTPrinter(Visitor):
  node_defaults = {
    'shape' : 'box',
    'color' : 'deepskyblue',
    'style' : 'filled'
  }

  edge_defaults = {
    'arrowhead' : 'none'
  }

  color_defaults = [
    'chartreuse',
    'darksalmon',
    'dodgerblue',
    'lightgrey'
  ]

  def __init__(self):
    self.dot = Digraph('AST')
    self.dot.attr('node', **self.node_defaults)
    self.dot.attr('edge', **self.edge_defaults)
    self._seq = 0
    
  def __repr__(self):
    return self.dot.source

  @property
  def name(self):
    self._seq += 1
    return f'n{self._seq:02d}'
    
  @classmethod
  def render(cls, n: Node):
    dot = cls()
    n.accept(dot)
    return dot.dot
    
  def visit(self, n: Program):
    name = self.name
    self.dot.node(name, label='Program')

    for stmt in n.body:
      self.dot.edge(name, stmt.accept(self))

    return name
  
  def visit(self, n: VarDecl):
    name = self.name
    var_type = self.name

    self.dot.node(name, label=f"VarDecl: {n.name}")
    self.dot.node(var_type, label=f"Type: {n.type}")

    self.dot.edge(name, var_type)

    if n.value:
      self.dot.edge(name, n.value.accept(self))

    return name
  
  def visit(self, n: ArrayDecl):
    name = self.name
    array_type = self.name

    self.dot.node(name, label=f"ArrayDecl: {n.name}")
    self.dot.node(array_type, label=f"Type: {n.type}")

    self.dot.edge(name, array_type)

    for value in n.value:
      self.dot.edge(name, value.accept(self))

    return name

  def visit(self, n: FuncDecl):
    name = self.name
    function_type = self.name

    self.dot.node(name, label=f"FuncDecl: {n.name}")
    self.dot.node(function_type, label=f"Type: {n.type}")

    self.dot.edge(name, function_type)

    for stmt in n.body:
      self.dot.edge(name, stmt.accept(self))

    return name
  
  def visit(self, n: VarParam):
    name = self.name

    self.dot.node(name, label=f"{n.name}")

    self.dot.edge(name, n.type.accept(self))
  
    return name
  
  def visit(self, n: ArrayParam):
    name = self.name

    self.dot.node(name, label=f"{n.name}")

    self.dot.edge(name, n.type.accept(self))
    
    if n.size:
      self.dot.edge(name, n.size.accept(self))

    return name
  
  def visit(self, n: Assignment):
    name = self.name

    self.dot.node(name, label="Assignment")

    self.dot.edge(name, n.target.accept(self))
    self.dot.edge(name, n.value.accept(self))

    return name
  
  def visit(self, n: VarLoc):
    name = self.name

    self.dot.node(name, label=f"VarLoc: {n.name}")

    return name
    
  def visit(self, n: ArrayLoc):
    name = self.name

    self.dot.node(name, label=f"ArrayLoc: {n.name}")
    
    self.dot.edge(name, n.index.accept(self))

    return name
  
  def visit(self, n: BinOper):
    name = self.name
    self.dot.node(name, label=f'{n.oper}', shape='circle', color=self.color_defaults[2])
    self.dot.edge(name, n.left.accept(self))
    self.dot.edge(name, n.right.accept(self))

    return name
  
  def visit(self, n: UnaryOper):
    name = self.name
    self.dot.node(name, label=f'{n.oper}', shape='circle', color=self.color_defaults[0])
    self.dot.edge(name, n.expr.accept(self))

    return name
  
  def visit(self, n: Literal):
    name = self.name
    literal_type = self.name
    literal_value = self.name

    if isinstance(n.value, str) and n.value == '\n':
      value = r"'\\n'"
    else:
      value = n.value

    self.dot.node(name, label="Literal", color=self.color_defaults[1])
    self.dot.node(literal_type, label=f"Type: {n.type}")
    self.dot.node(literal_value, label=str(n.value))

    self.dot.edge(name, literal_type)
    self.dot.edge(name, literal_value)

    return name
  
  def visit(self, n: BlockStmt):
    name = self.name

    self.dot.node(name, label=f"BlockStmt", color=self.color_defaults[3])

    for stmt in n.body:
      self.dot.edge(name, stmt.accept(self))
    
    return name
  
  def visit(self, n: WhileStmt):
    name = self.name

    self.dot.node(name, label=f"WhileStmt")

    if n.condition:
      self.dot.edge(name, n.condition.accept(self))

    if n.body:
      self.dot.edge(name, n.body.accept(self))

    return name

  def visit(self, n: ForStmt):
    name = self.name

    self.dot.node(name, label=f"ForStmt")

    if n.init:
      self.dot.edge(name, n.init.accept(self))

    if n.condition:
      self.dot.edge(name, n.condition.accept(self))

    if n.incr:
      self.dot.edge(name, n.incr.accept(self))

    if n.body:
      self.dot.edge(name, n.body.accept(self))

    return name
  
  def visit(self, n: IfStmt):
    name = self.name

    self.dot.node(name, label=f"IfStmt")

    if n.condition:
      self.dot.edge(name, n.condition.accept(self))

    if n.then_branch is not None:
      self.dot.edge(name, n.then_branch.accept(self))

    if n.else_branch is not None:
      self.dot.edge(name, n.else_branch.accept(self))

    return name

  def visit(self, n: PrintStmt):
    name = self.name

    self.dot.node(name, label="PrintStmt")

    for stmt in n.value:
      self.dot.edge(name, stmt.accept(self))

    return name
  
  def visit(self, n: ReturnStmt):
    name = self.name

    self.dot.node(name, label="ReturnStmt")

    self.dot.edge(name, n.value.accept(self))

    return name
  
  def visit(self, n: FuncCall):
    name = self.name

    self.dot.node(name, label=f"FuncCall: {n.name}")

    for arg in n.args:
      self.dot.edge(name, arg.accept(self))

    return name

  def visit(self, n: Node):
    name = self.name
    print(n.__class__.__name__)
    self.dot.node(name, label=n.__class__.__name__)

    for child in getattr(n, "children", []):
        self.dot.edge(name, child.accept(self))

    return name

if __name__ == '__main__':
  import sys
  from bminor.parser import parse

  if len(sys.argv) != 2:
	  raise SystemExit("Usage: python dotrender.py <filename>")

  txt = open(sys.argv[1], encoding='utf-8').read()
  ast = parse(txt)
  
  dot = ASTPrinter.render(ast)
  dot.render("ast.dot")