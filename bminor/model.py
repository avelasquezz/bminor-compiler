from dataclasses import dataclass, field
from typing import List, Union

# == Base nodes ==

@dataclass
class Statement:
  pass

@dataclass
class Expression:
  pass

@dataclass
class Declaration:
  pass

# == Program ==

@dataclass
class Program(Statement):
  body: List[Statement] = field(default_factory = list)

# == Types ==

@dataclass
class Type(Expression):
  pass

@dataclass
class PrimitiveType(Type):
  pass 

@dataclass
class IntegerType(PrimitiveType):
  pass

@dataclass
class FloatType(PrimitiveType):
  pass

@dataclass
class StringType(PrimitiveType):
  pass

@dataclass
class CharType(PrimitiveType):
  pass

@dataclass
class BooleanType(PrimitiveType):
  pass

@dataclass
class VoidType(PrimitiveType):
  pass

@dataclass
class ArrayType(Type):
  base: Type
  size: Expression = None

@dataclass
class FuncType(Type):
  ret: Type
  params: List["Param"]

# == Params ==

@dataclass
class Param:
  name: str
  type: Expression

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
  type: Expression
  value: Expression = None

@dataclass
class ArrayDecl(Declaration):
  name: str
  type: Expression
  value: List[Expression] = field(default_factory = list)

@dataclass
class FuncDecl(Declaration):
  name: str
  type: Expression
  params: List[Param]
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

@dataclass
class Integer(Literal):
  value: int

  def __post_init__(self):
    assert isinstance(self.value, int), "Value must be an integer"

@dataclass
class Float(Literal):
  value: float 

  def __post_init__(self):
    assert isinstance(self.value, float), "Value must be a float"

@dataclass
class String(Literal):
  value: str

  def __post_init__(self):
    assert isinstance(self.value, str), "Value must be a string"

@dataclass
class Char(Literal):
  value: str

  def __post_init__(self):
    assert isinstance(self.value, str) and len(self.value) == 1, "Value must be a char"

@dataclass
class Boolean(Literal):
  value: bool

  def __post_init__(self):
    assert isinstance(self.value, bool), "Value must be a boolean"

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