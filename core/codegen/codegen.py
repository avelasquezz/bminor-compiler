from llvmlite import ir
from core.parser.model import Visitor

class CodeGenerator(Visitor):
    def __init__(self):
        self.module = ir.Module(name="bminor_module")
        self.builder = None
        self.symbols = {}

    def visit(self, node, *args, **kwargs):
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, *args, **kwargs)

    def generic_visit(self, node, *args, **kwargs):
        raise NotImplementedError(f"No visit_{node.__class__.__name__} method")

    def visit_Program(self, node):
        main_ty = ir.FunctionType(ir.IntType(32), [])
        main_fn = ir.Function(self.module, main_ty, name="main")
        block = main_fn.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)

        for decl in node.body:
            decl.accept(self)

        self.builder.ret(ir.Constant(ir.IntType(32), 0))

    def visit_VarDecl(self, node):
        int32 = ir.IntType(32)
        ptr = self.builder.alloca(int32, name=node.name)
        self.symbols[node.name] = ptr

        if node.value:
            val = node.value.accept(self)
            self.builder.store(val, ptr)

    def visit_Literal(self, node):
        if node.type == "integer":
            return ir.Constant(ir.IntType(32), int(node.value))
        else:
            raise NotImplementedError(f"Literal type {node.type} not supported")
        
    def visit_VarLoc(self, node):
        """
        Genera el código para acceder al valor de una variable.
        - node.name: nombre de la variable
        """
        if node.name not in self.symbols:
            raise NameError(f"Variable '{node.name}' not declared")

        ptr = self.symbols[node.name]
        # Cargamos el valor almacenado en memoria
        return self.builder.load(ptr, name=node.name)


    def visit_BinOper(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)

        if node.oper == '+':
            return self.builder.add(left, right)
        elif node.oper == '-':
            return self.builder.sub(left, right)
        elif node.oper == '*':
            return self.builder.mul(left, right)
        elif node.oper == '/':
            return self.builder.sdiv(left, right)
        else:
            raise NotImplementedError(f"Operator {node.oper} not supported")
