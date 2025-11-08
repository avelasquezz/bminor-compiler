from core.codegen.operations import operation
from core.parser.model       import *
from llvmlite                import ir

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

    printi_ty = ir.FunctionType(void_type, [int_type])
    self.printi = ir.Function(self.module, printi_ty, "_printi")

    printf_ty = ir.FunctionType(void_type, [float_type])
    self.printf = ir.Function(self.module, printf_ty, "_printf")

    printb_ty = ir.FunctionType(void_type, [bool_type])
    self.printb = ir.Function(self.module, printb_ty, "_printb")

    printc_ty = ir.FunctionType(void_type, [char_type])
    self.printc = ir.Function(self.module, printc_ty, "_printc")
  
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

    return operation(left, right, node.oper, self.builder)

  def visit(self, node: FuncDecl):
    param_types = [_typemap[p.type] for p in node.params]

    ty = _typemap[node.type]
    func_ty = ir.FunctionType(ty, param_types)
    func = ir.Function(self.module, func_ty, name=node.name)

    self.symbols[node.name] = func

    block = func.append_basic_block(name="entry")
    self.builder = ir.IRBuilder(block)
  
    for arg, param in zip(func.args, node.params):
      arg.name = param.name
      ptr = self.builder.alloca(arg.type, name=param.name)
      self.builder.store(arg, ptr)
      self.symbols[param.name] = ptr

    for decl in node.body:
      decl.accept(self)

    if ty == void_type:
      self.builder.ret_void()
  
  def visit(self, node: ReturnStmt):
    retval = node.value.accept(self)
    self.builder.ret(retval)
  
  def visit(self, node: WhileStmt):
    func = self.builder.function
    cond_block = func.append_basic_block(name="while.cond")
    body_block = func.append_basic_block(name="while.body")
    after_block = func.append_basic_block(name="while.end")

    self.builder.branch(cond_block)
    self.builder.position_at_end(cond_block)

    cond_val = node.condition.accept(self)

    self.builder.cbranch(cond_val, body_block, after_block)
    self.builder.position_at_end(body_block)

    node.body.accept(self)

    self.builder.branch(cond_block)
    self.builder.position_at_end(after_block)

  def visit(self, node: BlockStmt):
    for stmt in node.body:
      stmt.accept(self)
  
  def visit(self, node: Assignment):
    value = node.value.accept(self)
    ptr = self.symbols[node.target.name]

    self.builder.store(value, ptr)
  
  def visit(self, node: PrintStmt):
    for v in node.value:
      value = v.accept(self)
      ty = value.type

      if ty == int_type:
        self.builder.call(self.printi, [value])
      elif ty == float_type:
        self.builder.call(self.printf, [value])
      elif ty == bool_type:
        self.builder.call(self.printb, [value])
      elif ty == char_type:
        self.builder.call(self.printc, [value])

  def visit(self, node: FuncCall):
    func = self.symbols.get(node.name)

    arg_values = [arg.accept(self) for arg in node.args]
    result = self.builder.call(func, arg_values, name=f"call_{node.name}")

    return result