from core.codegen.operations import * 
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
    self.init_global = True

    printi_ty = ir.FunctionType(void_type, [int_type])
    self.printi = ir.Function(self.module, printi_ty, "_printi")

    printf_ty = ir.FunctionType(void_type, [float_type])
    self.printf = ir.Function(self.module, printf_ty, "_printf")

    printb_ty = ir.FunctionType(void_type, [bool_type])
    self.printb = ir.Function(self.module, printb_ty, "_printb")

    printc_ty = ir.FunctionType(void_type, [char_type])
    self.printc = ir.Function(self.module, printc_ty, "_printc")

  def visit(self, node: Program):
    global_decls = []
    func_decls = []

    for decl in node.body:
      if isinstance(decl, FuncDecl):
        func_decls.append(decl)
      else:
        global_decls.append(decl)

    func_ty = ir.FunctionType(void_type, [])
    func = ir.Function(self.module, func_ty, name="_global_init")
    block = func.append_basic_block(name="entry")
    self.builder = ir.IRBuilder(block)

    for decl in global_decls:
      decl.accept(self)
    
    self.init_global = False

    for decl in global_decls:
      val = decl.value.accept(self)
      ptr = self.symbols.get(f"{decl.name}.global")
      self.builder.store(val, ptr)

    if not self.builder.block.is_terminated:
      self.builder.ret_void()

    for func_decl in func_decls:
      func_decl.accept(self)

  def visit(self, node: VarDecl):
    ty = _typemap[node.type]

    if self.init_global:
      global_var = ir.GlobalVariable(self.module, ty, name=f"{node.name}.global")
      global_var.linkage = "common"
      global_var.initializer = ir.Constant(ty, 0)
      self.symbols[f"{node.name}.global"] = global_var
      return
    
    ptr = self.builder.alloca(ty, name=node.name)

    if node.value:
      val = node.value.accept(self)
      self.builder.store(val, ptr)

    self.symbols[node.name] = ptr
    
  def visit(self, node: ArrayDecl):
    ty = _typemap[node.type]
    size = node.size.accept(self)

    if self.init_global:
      global_var = ir.GlobalVariable(self.module, ty, name=f"{node.name}.global")
      global_var.linkage = "common"
      global_var.initializer = ir.Constant(ty, 0)
      self.symbols[f"{node.name}.global"] = global_var
      return

    arr_ptr = self.builder.alloca(ty, size, name=node.name)
    self.symbols[node.name] = arr_ptr

    if node.value:
      for i, val_node in enumerate(node.value):
        value = val_node.accept(self)
        index = ir.Constant(int_type, i)
        element_ptr = self.builder.gep(arr_ptr, [index])
        self.builder.store(value, element_ptr)
  
  def visit(self, node: ArrayLoc):
    arr_ptr = self.symbols.get(node.name)
    index = node.index.accept(self)
    element_ptr = self.builder.gep(arr_ptr, [index])
    return self.builder.load(element_ptr)

  def visit(self, node: Literal):
    match node.type:
      case "integer":
        return ir.Constant(int_type, int(node.value))
      case "float":
        return ir.Constant(float_type, float(node.value))
      case "boolean":
        return ir.Constant(bool_type, 1 if node.value == True else 0)
      case "char":
        return ir.Constant(char_type, ord(node.value))
        
  def visit(self, node: VarLoc):
    ptr = self.symbols.get(node.name)
    if ptr is None:
      ptr = self.symbols.get(f"{node.name}.global")
    return self.builder.load(ptr, name=node.name)

  def visit(self, node: BinOper):
    left = node.left.accept(self)
    right = node.right.accept(self)

    return binary_operation(left, right, node.oper, self.builder)
  
  def visit(self, node: UnaryOper):
    expr = node.expr.accept(self)

    return unary_operation(expr, node.oper, self.builder)
  
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

    if node.name == "main":
      init_func = self.module.globals.get("_global_init")
      if init_func:
        self.builder.call(init_func, [])

    for decl in node.body:
      decl.accept(self)

    if ty == void_type:
      self.builder.ret_void()
  
  def visit(self, node: ReturnStmt):
    retval = node.value.accept(self)
    self.builder.ret(retval)
  
  def visit(self, node: IfStmt):
    func = self.builder.function
    cond = node.condition.accept(self)

    then_block = func.append_basic_block(name="if.then")
    merge_block = func.append_basic_block(name="if.merge")
    
    if node.else_branch is not None:
      else_block = func.append_basic_block(name="if.else")

      self.builder.cbranch(cond, then_block, else_block)

      self.builder.position_at_end(else_block)
      node.else_branch.accept(self)
      if not self.builder.block.is_terminated:
        self.builder.branch(merge_block)
    else:
      self.builder.cbranch(cond, then_block, merge_block)

    self.builder.position_at_end(then_block)
    node.then_branch.accept(self)

    if not self.builder.block.is_terminated:
      self.builder.branch(merge_block)

    self.builder.position_at_end(merge_block)

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

  def visit(self, node: ForStmt):
    node.init.accept(self)

    func = self.builder.function
    cond_block = func.append_basic_block(name="for.cond")
    body_block = func.append_basic_block(name="for.body")
    after_block = func.append_basic_block(name="for.end")

    self.builder.branch(cond_block)
    self.builder.position_at_end(cond_block)

    cond_val = node.condition.accept(self)

    self.builder.cbranch(cond_val, body_block, after_block)
    self.builder.position_at_end(body_block)

    node.body.accept(self)

    val = node.incr.accept(self)

    var = None
    if hasattr(node.incr, "expr"):
      var = node.incr.expr.name
    else:
      var = node.incr.target.name

    ptr = self.symbols.get(var)
    self.builder.store(val, ptr)

    self.builder.branch(cond_block)
    self.builder.position_at_end(after_block)

  def visit(self, node: DoWhileStmt):
    func = self.builder.function
    body_block = func.append_basic_block(name="dowhile.body")
    cond_block = func.append_basic_block(name="dowhile.cond")
    after_block = func.append_basic_block(name="dowhile.end")

    self.builder.branch(body_block)
    self.builder.position_at_end(body_block)

    node.body.accept(self)

    self.builder.branch(cond_block)

    self.builder.position_at_end(cond_block)
    cond_val = node.condition.accept(self)
    self.builder.cbranch(cond_val, body_block, after_block)

    self.builder.position_at_end(after_block)

  def visit(self, node: BlockStmt):
    for stmt in node.body:
      stmt.accept(self)
  
  def visit(self, node: Assignment):
    value = node.value.accept(self)
    ptr = self.symbols[node.target.name]

    if (node.target.__class__.__name__ == "ArrayLoc"):
      arr_ptr = self.symbols.get(node.target.name)
      index = node.target.index.accept(self)
      ptr = self.builder.gep(arr_ptr, [index])

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