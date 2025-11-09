from llvmlite import ir

int_type   = ir.IntType(32)
float_type = ir.DoubleType()
bool_type  = ir.IntType(1)
char_type  = ir.IntType(8)
void_type  = ir.VoidType()

def binary_operation(left, right, oper, builder):
  if left.type == int_type and right.type == int_type:
    match oper:
      case "+":  return builder.add(left, right)
      case "-":  return builder.sub(left, right)
      case "*":  return builder.mul(left, right)
      case "/":  return builder.sdiv(left, right)
      case "%":  return builder.srem(left, right)
      case "<":  return builder.icmp_signed("<", left, right)
      case "<=": return builder.icmp_signed("<=", left, right)
      case ">":  return builder.icmp_signed(">", left, right)
      case ">=": return builder.icmp_signed(">=", left, right)
      case "==": return builder.icmp_signed("==", left, right)
      case "!=": return builder.icmp_signed("!=", left, right)
  elif left.type == float_type and right.type == float_type: 
    match oper:
      case "+":  return builder.fadd(left, right)
      case "-":  return builder.fsub(left, right)
      case "*":  return builder.fmul(left, right)
      case "/":  return builder.fdiv(left, right)
      case "<":  return builder.fcmp_ordered("<", left, right)
      case "<=": return builder.fcmp_ordered("<=", left, right)
      case ">":  return builder.fcmp_ordered(">", left, right)
      case ">=": return builder.fcmp_ordered(">=", left, right)
      case "==": return builder.fcmp_ordered("==", left, right)
      case "!=": return builder.fcmp_ordered("!=", left, right)
  elif left.type == bool_type and right.type == bool_type:
    match oper:
      case "&&": return builder.and_(left, right)
      case "||": return builder.and_(left, right)
      case "==": return builder.icmp_signed("==", left, right)
      case "!=": return builder.icmp_signed("!=", left, right)
  elif left.type == char_type and right.type == char_type:
    match oper:
      case "<":  return builder.icmp_signed("<", left, right)
      case "<=": return builder.icmp_signed("<=", left, right)
      case ">":  return builder.icmp_signed(">", left, right)
      case ">=": return builder.icmp_signed(">=", left, right)
      case "==": return builder.icmp_signed("==", left, right)
      case "!=": return builder.icmp_signed("!=", left, right)
  
def unary_operation(expr, oper, builder):
  if expr.type == int_type:
    match oper:
      case "+":  return builder.add(expr, ir.Constant(int_type, 0))
      case "-":  return builder.sub(ir.Constant(int_type, 0), expr)
      case "++": return builder.add(expr, ir.Constant(int_type, 1))
      case "--": return builder.sub(expr, ir.Constant(int_type, 1))
  elif expr.type == float_type:
    match oper:
      case "+": return builder.fadd(expr, ir.Constant(float_type, 0))
      case "-": return builder.fsub(ir.Constant(float_type, 0), expr)
  elif expr.type == bool_type:
    match oper:
      case "!": return builder.xor(expr, ir.Constant(bool_type, 1))