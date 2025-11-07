from core.parser.model import *
from llvmlite          import ir

# LLVM types corresponding to the B-Minor types
int_type   = ir.IntType(32)
float_type = ir.DoubleType()
bool_type  = ir.IntType(1)
char_type  = ir.IntType(8)
void_type  = ir.VoidType()

_typemap = {
	"integer": int_type,
	"float"  : float_type,
	"boolean": bool_type,
	"char"   : char_type,
  "void"   : void_type
}

class CodeGenerator(Visitor):
  def __init__(self):
    self.module = ir.Module(name="bminor_module")
    self.builder = None
    self.symbols = {}
  
  def visit(self, n: Node):
    print(f"Node '{n.__class__.__name__}' not implemented")

  def visit(self, node: Program):
    for decl in node.body:
      decl.accept(self)

  def visit(self, node: VarDecl):
    ty = _typemap[node.type]

    if self.builder is None:
      global_var = ir.GlobalVariable(self.module, ty, name=node.name)
      global_var.linkage = 'common'
      global_var.initializer = node.value.accept(self) if node.value else ir.Constant(ty, None)
      self.symbols[node.name] = global_var
      return

    ptr = self.builder.alloca(ty, name=node.name)
    self.symbols[node.name] = ptr

    if node.value:
      val = node.value.accept(self)
      self.builder.store(val, ptr)

  def visit(self, node: Literal):
    match node.type:
      case "integer":
        return ir.Constant(int_type, int(node.value))
      case "float":
        return ir.Constant(float_type, float(node.value))
      case "boolean":
        return ir.Constant(bool_type, 1 if node.value == "true" else 0)
      case "char":
        return ir.Constant(char_type, ord(node.value))
        
  def visit(self, node: VarLoc):
    ptr = self.symbols[node.name]
    return self.builder.load(ptr, name=node.name)

  def visit(self, node: BinOper):
    left = node.left.accept(self)
    right = node.right.accept(self)

    match node.oper:
      case "+":
        return self.builder.add(left, right)
      case "-":
        return self.builder.sub(left, right)
      case "*":
        return self.builder.mul(left, right)
      case "/":
        return self.builder.sdiv(left, right)
  
  def visit(self, node: FuncDecl):
    param_types = [_typemap[p.type] for p in node.params]

    ty = _typemap[node.type]
    func_ty = ir.FunctionType(ty, param_types)
    func = ir.Function(self.module, func_ty, name=node.name)
    block = func.append_basic_block(name="entry")
    self.builder = ir.IRBuilder(block)
  
    for arg, param in zip(func.args, node.params):
      arg.name = param.name
      ptr = self.builder.alloca(arg.type, name=param.name)
      self.builder.store(arg, ptr)
      self.symbols[param.name] = ptr

    for decl in node.body:
      decl.accept(self)

    if not self.builder.block.is_terminated:
      if ty == void_type:
        self.builder.ret_void()
      else:
        self.builder.ret(ir.Constant(ty, 0))
  
  def visit(self, node: ReturnStmt):
    retval = node.value.accept(self)
    self.builder.ret(retval)