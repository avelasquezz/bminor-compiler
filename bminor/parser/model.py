from dataclasses import dataclass, field
from multimethod import multimeta 
from typing      import List, Union

class Visitor(metaclass = multimeta):
  pass

# == Base nodes ==

class Node:
  def accept(self, v : Visitor, *args, **kwargs):
    return v.visit(self, *args, **kwargs)

@dataclass
class Statement(Node):
  pass

@dataclass
class Expression(Node):
  pass

@dataclass
class Declaration(Node):
  pass

# == Program ==

@dataclass
class Program(Statement):
  body: List[Statement] = field(default_factory = list)

# == Params ==

@dataclass
class Param(Expression):
  name: str
  type: str 

@dataclass
class VarParam(Param):
  pass

@dataclass
class ArrayParam(Param):
  size: Expression = None

# == Declarations ==

@dataclass
class VarDecl(Declaration):
  name: str
  type: str 
  value: Expression = None

@dataclass
class ArrayDecl(Declaration):
  name: str
  type: str
  size: Expression 
  value: List[Expression] = field(default_factory = list)

@dataclass
class FuncDecl(Declaration):
  name: str
  type: str
  params: List[Param] = field(default_factory = list)
  body: List[Statement] = field(default_factory = list)

# == Statements ==

@dataclass
class IfStmt(Statement):
  condition: Expression
  then_branch: Statement
  else_branch: Statement = None

@dataclass
class ForStmt(Statement):
  init: Expression = None
  condition: Expression = None
  incr: Expression = None
  body: Statement = None

@dataclass
class WhileStmt(Statement):
  condition: Expression = None
  body: Statement = None

@dataclass
class DoWhileStmt(Statement):
  body: Statement = None
  condition: Expression = None

@dataclass
class ReturnStmt(Statement):
  value: Expression = None

@dataclass
class PrintStmt(Statement):
  value: List[Expression] = field(default_factory = list)

@dataclass
class BlockStmt(Statement):
  body: List[Statement] = field(default_factory = list)

# == Location / Assignments ==

@dataclass
class Location(Expression):
  pass

@dataclass
class VarLoc(Location):
  name: str

@dataclass
class ArrayLoc(Location):
  name: str
  index: Expression

@dataclass
class Assignment(Statement):
  target: Location
  value: Expression

# == Expressions ==

@dataclass
class BinOper(Expression):
  oper: str
  left: Expression
  right: Expression

@dataclass
class UnaryOper(Expression):
  oper: str
  expr: Expression

# == Literals ==

@dataclass
class Literal(Expression):
  value: Union[int, float, str, bool]
  type: str

@dataclass
class Increment(Expression):
  expr: Expression
  postfix: bool = True

@dataclass
class Decrement(Expression):
  expr: Expression
  postfix: bool = True

@dataclass
class FuncCall(Expression):
  name: str
  args: List[Expression] = field(default_factory = list)