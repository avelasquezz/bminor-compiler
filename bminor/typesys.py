class CheckError(Exception):
	pass
	
typenames = { 'integer', 'float', 'char', 'boolean', 'string' }

# Capabilities
_bin_ops = {
	# Integer operations
	('integer', '+', 'integer') : 'integer',
	('integer', '-', 'integer') : 'integer',
	('integer', '*', 'integer') : 'integer',
	('integer', '/', 'integer') : 'integer',
	('integer', '%', 'integer') : 'integer',

	('integer', '=', 'integer') : 'integer',

	('integer', '<', 'integer')  : 'boolean',
	('integer', '<=', 'integer') : 'boolean',
	('integer', '>', 'integer')  : 'boolean',
	('integer', '>=', 'integer') : 'boolean',
	('integer', '==', 'integer') : 'boolean',
	('integer', '!=', 'integer') : 'boolean',

	# Float operations
	('float', '+', 'float') : 'float',
	('float', '-', 'float') : 'float',
	('float', '*', 'float') : 'float',
	('float', '/', 'float') : 'float',

	('float', '=', 'float') : 'float',

	('float', '<', 'float')  : 'boolean',
	('float', '<=', 'float') : 'boolean',
	('float', '>', 'float')  : 'boolean',
	('float', '>=', 'float') : 'boolean',
	('float', '==', 'float') : 'boolean',
	('float', '!=', 'float') : 'boolean',

	# Bools
	('boolean', '&&', 'boolean') : 'boolean',
	('boolean', '||', 'boolean') : 'boolean',
	('boolean', '==', 'boolean') : 'boolean',
	('boolean', '!=', 'boolean') : 'boolean',

	# Char
	('char', '=', 'char')  : 'char',

	('char', '<', 'char')  : 'boolean',
	('char', '<=', 'char') : 'boolean',
	('char', '>', 'char')  : 'boolean',
	('char', '>=', 'char') : 'boolean',
	('char', '==', 'char') : 'boolean',
	('char', '!=', 'char') : 'boolean',

	# Strings
	('string', '+', 'string')  : 'string',		# Concatenate 

	('string', '=', 'string')  : 'string',

	('string', '<', 'string')  : 'boolean',
	('string', '<=', 'string') : 'boolean',
	('string', '>', 'string')  : 'boolean',
	('string', '>=', 'string') : 'boolean',
	('string', '==', 'string') : 'boolean',
	('string', '!=', 'string') : 'boolean',
}

_unary_ops = {
	('+', 'integer') : 'integer',
	('-', 'integer') : 'integer',
	('^', 'integer') : 'integer',

	('+', 'float') : 'float',
	('-', 'float') : 'float',

	('!', 'boolean') : 'boolean',
}

# Check if a binary operator is supported. Returns the
# result type or None (if not supported). Type checker
# uses this function.

def loockup_type(name):
	'''
  Given the name of a primitive type, the appropriate "type" object is searched for.
  Initially, types are just names, but later they can become
  more advanced objects.
	'''
	if name in typenames:
		return name
	else:
		return None
		
def check_binop(op, left_type, right_type):
	return _bin_ops.get((left_type, op, right_type))

def check_unaryop(op, operand_type):
	return _unary_ops.get((op, operand_type))