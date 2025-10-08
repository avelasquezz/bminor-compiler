import sly

from bminor.lexer import Lexer
from bminor.model import *
from rich.tree import Tree
from rich import print
from dataclasses import is_dataclass, fields

def _L(node, lineno):
  node.lineno = lineno
  return node

class Parser(sly.Parser):
  tokens = Lexer.tokens

  # == Program ==
  @_("decl_list")
  def prog(self, p):
    return _L(Program(p.decl_list), p.lineno)
  
  # == decl_list ==
  @_("decl decl_list")
  def decl_list(self, p):
    return [p.decl] + p.decl_list
  
  @_("empty")
  def decl_list(self, p):
    return []
  
  # == Types ==
  @_("INTEGER")
  def type_simple(self, p):
    return "integer"

  @_("FLOAT")
  def type_simple(self, p):
    return "float" 

  @_("STRING")
  def type_simple(self, p):
    return "string"

  @_("CHAR")
  def type_simple(self, p):
    return "char"

  @_("BOOLEAN")
  def type_simple(self, p):
    return "boolean"
  
  @_("VOID")
  def type_simple(self, p):
    return "void" 
  
  # Array types (solo con tamaño opcional)
  @_("ARRAY '[' opt_expr ']' type_simple")
  def type_array_sized(self, p):
    return (p.type_simple, p.opt_expr)

  @_("ARRAY '[' opt_expr ']' type_array_sized")
  def type_array_sized(self, p):
    return (p.type_simple, p.opt_expr)
  
  # Function types
  @_("FUNCTION type_simple '(' opt_param_list ')'")
  def type_func(self, p):
    return (p.type_simple, p.opt_param_list)

  @_("FUNCTION type_array_sized '(' opt_param_list ')'")
  def type_func(self, p):
    return (p.type_array_sized[0], p.opt_param_list)
  
  # == Declarations ==
  @_("ID ':' type_simple ';'")
  def decl(self, p):
    return _L(VarDecl(name=p.ID, type=p.type_simple), p.lineno)

  @_("ID ':' type_array_sized ';'")
  def decl(self, p):
    return _L(ArrayDecl(
      name=p.ID, 
      base=p.type_array_sized[0], 
      size=p.type_array_sized[1]
    ), p.lineno)

  @_("ID ':' type_func ';'")
  def decl(self, p):
    return _L(FuncDecl(
      name=p.ID, 
      type=p.type_func[0],
      params=p.type_func[1],
      body=[]
    ), p.lineno)
  
  # decl_init
  @_("ID ':' type_simple '=' expr ';'")
  def decl(self, p):
    return _L(VarDecl(name=p.ID, type=p.type_simple, value=p.expr), p.lineno)
  
  @_("ID ':' type_array_sized '=' '{' opt_expr_list '}' ';'")
  def decl(self, p):
    return _L(ArrayDecl(
      name=p.ID, 
      base=p.type_array_sized[0], 
      size=p.type_array_sized[1],
      value=p.opt_expr_list
    ), p.lineno)
  
  @_("ID ':' type_func '=' '{' opt_stmt_list '}' ';'")
  def decl(self, p):
    return _L(FuncDecl(
      name=p.ID, 
      type=p.type_func[0],
      params=p.type_func[1],
      body=p.opt_stmt_list
    ), p.lineno)
  
  # == Statements ==
  @_("stmt_list")
  def opt_stmt_list(self, p):
    return p.stmt_list
  
  @_("empty")
  def opt_stmt_list(self, p):
    return []
  
  @_("stmt stmt_list")
  def stmt_list(self, p):
    return [p.stmt] + p.stmt_list
  
  @_("stmt")
  def stmt_list(self, p):
    return [p.stmt]
  
  @_("open_stmt")
  @_("closed_stmt")
  @_("decl")
  def stmt(self, p):
    return p[0]

  @_("if_stmt_closed")
  @_("for_stmt_closed")
  @_("while_stmt_closed")
  @_("do_while_stmt_closed")
  @_("simple_stmt")
  def closed_stmt(self, p):
    return p[0]

  @_("if_stmt_open")
  @_("for_stmt_open")
  @_("while_stmt_open")
  @_("do_while_stmt_open")
  def open_stmt(self, p):
    return p[0]

  @_("WHILE '(' opt_expr ')'")
  def while_cond(self, p):
    return p.opt_expr
  
  @_("while_cond closed_stmt")
  def while_stmt_closed(self, p):
    return _L(WhileStmt(condition=p.while_cond, body=p.close_stmt), p.lineno)

  @_("while_cond stmt")
  def while_stmt_open(self, p):
    return _L(WhileStmt(condition=p.while_cond, body=p.stmt), p.lineno)

  @_("DO closed_stmt while_cond")
  def do_while_stmt_closed(self, p):
    return _L(DoWhileStmt(body=p.closed_stmt, condition=p.while_cond), p.lineno)

  @_("DO stmt while_cond")
  def do_while_stmt_open(self, p):
    return _L(DoWhileStmt(body=p.stmt, condition=p.while_cond), p.lineno)
  
  @_("IF '(' opt_expr ')'")
  def if_cond(self, p):
    return p.opt_expr
  
  @_("if_cond closed_stmt ELSE closed_stmt")
  def if_stmt_closed(self, p):
    return _L(IfStmt(condition=p.if_cond, then_branch=p[1], else_branch=p[3]), p.lineno)
  
  @_("if_cond stmt")
  def if_stmt_open(self, p):
    return _L(IfStmt(condition=p.if_cond, then_branch=p.stmt), p.lineno)
  
  @_("if_cond closed_stmt ELSE if_stmt_open")
  def if_stmt_open(self, p):
    return _L(IfStmt(condition=p.if_cond, then_branch=p[1], else_branch=p[3]), p.lineno)
  
  @_("FOR '(' opt_expr ';' opt_expr ';' opt_expr ')'")
  def for_header(self, p):
    return (p.opt_expr0, p.opt_expr1, p.opt_expr2)
  
  @_("for_header open_stmt")
  def for_stmt_open(self, p):
    init, condition, incr = p.for_header
    return _L(ForStmt(init=init, condition=condition, incr=incr, body=p.open_stmt), p.lineno)

  @_("for_header closed_stmt")
  def for_stmt_closed(self, p):
    init, condition, incr = p.for_header
    return _L(ForStmt(init=init, condition=condition, incr=incr, body=p.closed_stmt), p.lineno)
  
  # simple_stmt
  @_("print_stmt")
  @_("return_stmt")
  @_("block_stmt")
  @_("expr ';'")
  def simple_stmt(self, p):
    return p[0]

  @_("RETURN opt_expr ';'")
  def return_stmt(self, p):
    return _L(ReturnStmt(value=p.opt_expr), p.lineno)
  
  @_("PRINT opt_expr_list ';'")
  def print_stmt(self, p):
    return _L(PrintStmt(value=p.opt_expr_list), p.lineno)
  
  @_("'{' stmt_list '}'")
  def block_stmt(self, p):
    return _L(BlockStmt(body=p.stmt_list), p.lineno)
  
  # == Expression helpers ==
  @_("empty")
  def opt_expr_list(self, p):
    return []
  
  @_("expr_list")
  def opt_expr_list(self, p):
    return p.expr_list
  
  @_("expr ',' expr_list")
  def expr_list(self, p):
    return [p.expr] + p.expr_list
  
  @_("expr")
  def expr_list(self, p):
    return [p.expr]
  
  @_("empty")
  def opt_expr(self, p):
    return None
  
  @_("expr")
  def opt_expr(self, p):
    return p.expr
  
  @_("expr1")
  def expr(self, p):
    return p.expr1

  @_('lval INC')
  def expr(self, p):
    return _L(UnaryOper(oper="++", expr=p.lval), p.lineno)

  @_('lval DEC')
  def expr(self, p):
    return _L(UnaryOper(oper="--", expr=p.lval), p.lineno)

  @_('INC lval')
  def expr(self, p):
    return _L(UnaryOper(oper="++", expr=p.lval), p.lineno)

  @_('DEC lval')
  def expr(self, p):
    return _L(UnaryOper(oper="--", expr=p.lval), p.lineno)

  @_("ID '[' expr ']'")
  def expr(self, p):
    return _L(ArrayLoc(name=p.ID, index=p.expr), p.lineno)

  @_("lval '=' expr1")
  def expr1(self, p):
    return _L(Assignment(target=p.lval, value=p.expr1), p.lineno)
  
  @_("expr2")
  def expr1(self, p):
    return p.expr2

  @_("ID")
  def lval(self, p):
    return _L(VarLoc(name=p.ID), p.lineno)
  
  @_("ID '[' expr ']'")
  def lval(self, p):
    return _L(ArrayLoc(name=p.ID, index=p.expr), p.lineno)
  
  @_("expr2 LOR expr3")
  def expr2(self, p):
    return _L(BinOper(oper="||", left=p.expr2, right=p.expr3), p.lineno)
  
  @_("expr3")
  def expr2(self, p):
    return p.expr3
  
  @_("expr3 LAND expr4")
  def expr3(self, p):
    return _L(BinOper(oper="&&", left=p.expr3, right=p.expr4), p.lineno)
  
  @_("expr4")
  def expr3(self, p):
    return p.expr4

  @_("expr4 EQ expr5")
  @_("expr4 NE expr5")
  @_("expr4 LT expr5")
  @_("expr4 LE expr5")
  @_("expr4 GT expr5")
  @_("expr4 GE expr5")
  def expr4(self, p):
    return _L(BinOper(oper=p[1], left=p.expr4, right=p.expr5), p.lineno)
  
  @_("expr5")
  def expr4(self, p):
    return p.expr5

  @_("expr5 '+' expr6")
  @_("expr5 '-' expr6")
  def expr5(self, p):
    return _L(BinOper(oper=p[1], left=p.expr5, right=p.expr6), p.lineno)

  @_("expr6")
  def expr5(self, p):
    return p.expr6

  @_("expr6 '*' expr7")
  @_("expr6 '/' expr7")
  @_("expr6 '%' expr7")
  def expr6(self, p):
    return _L(BinOper(oper=p[1], left=p.expr6, right=p.expr7), p.lineno)

  @_("expr7")
  def expr6(self, p):
    return p.expr7

  @_("expr7 '^' expr8")
  def expr7(self, p):
    return _L(BinOper(oper="^", left=p.expr7, right=p.expr8), p.lineno)

  @_("expr8")
  def expr7(self, p):
    return p.expr8

  @_("'-' expr8")
  @_("NOT expr8")
  def expr8(self, p):
    return _L(UnaryOper(oper=p[0], expr=p.expr8), p.lineno)

  @_("expr9")
  def expr8(self, p):
    return p.expr9

  @_("'(' expr ')'")  
  def expr9(self, p):
    return p.expr

  @_("ID '(' opt_expr_list ')'")  
  def expr9(self, p):
    return _L(FuncCall(name=p.ID, args=p.opt_expr_list), p.lineno)

  @_("ID")
  def expr9(self, p):
    return _L(VarLoc(name=p.ID), p.lineno)

  @_("ID '[' expr ']'")
  def expr9(self, p):
    return _L(ArrayLoc(name=p.ID, index=p.expr), p.lineno)

  # == Literals ==
  @_("INTEGER_LITERAL")
  def expr9(self, p):
    return _L(Literal(value=int(p.INTEGER_LITERAL), type="integer"), p.lineno)

  @_("FLOAT_LITERAL")
  def expr9(self, p):
    return _L(Literal(value=float(p.FLOAT_LITERAL), type="float"), p.lineno)
  
  @_("STRING_LITERAL")
  def expr9(self, p):
    value = p.STRING_LITERAL
    if len(value) >= 2 and value[0] == '"' and value[-1] == value[0]:
      value = value[1:-1]
    return _L(Literal(value=value, type="string"), p.lineno)

  @_("CHAR_LITERAL")
  def expr9(self, p):
    value = p.CHAR_LITERAL
    if len(value) >= 2 and value[0] == "'" and value[-1] == value[0]:
      value = value[1:-1]
    return _L(Literal(value=value, type="char"), p.lineno)
  
  @_("TRUE")
  def expr9(self, p):
    return _L(Literal(value=True, type="boolean"), p.lineno)

  @_("FALSE")
  def expr9(self, p):
    return _L(Literal(value=False, type="boolean"), p.lineno)
  
  # == Parameters ==  
  @_("empty")
  def opt_param_list(self, p):
    return []

  @_("param_list")
  def opt_param_list(self, p):
    return p.param_list

  @_("param_list ',' param")
  def param_list(self, p):
    return p.param_list + [p.param]

  @_("param")
  def param_list(self, p):
    return [p.param]

  @_("ID ':' type_simple")
  def param(self, p):
    return _L(VarParam(name=p.ID, type=p.type_simple), p.lineno)

  @_("ID ':' type_array_sized")
  def param(self, p):
    return _L(ArrayParam(name=p.ID, type=p.type_array_sized, size=p.type_array_sized.size), p.lineno)

  @_("")
  def empty(self, p):
    return None

  def error(self, p):
    lineno = p.lineno if p else "EOF"
    value = repr(p.value) if p else "EOF"
    raise SyntaxError(f"Syntax error at {value} (line {lineno})")

def parse(code):
  l = Lexer()
  p = Parser()
  return p.parse(l.tokenize(code))

def ast_to_tree(node, name="root"):
  label = f"[bold blue]{name}[/]"

  if is_dataclass(node):
    tree = Tree(f"{label} [cyan]{node.__class__.__name__}[/]")

    for f in fields(node):
      value = getattr(node, f.name)

      if is_dataclass(value) or isinstance(value, (list, tuple)):
        subtree = ast_to_tree(value, f.name)
        tree.add(subtree)
      else:
        tree.add(f"[green]{f.name}[/] = [yellow]{value}[/]")
    return tree

  elif isinstance(node, list):
    tree = Tree(f"{label} [magenta]list[/]")
    for i, item in enumerate(node):
      subtree = ast_to_tree(item, f"[{i}]")
      tree.add(subtree)
    return tree

  elif isinstance(node, tuple):
    tree = Tree(f"{label} [magenta]tuple[/]")
    for i, item in enumerate(node):
      subtree = ast_to_tree(item, f"[{i}]")
      tree.add(subtree)
    return tree

  else:
    return Tree(f"{label} = [yellow]{repr(node)}[/]")