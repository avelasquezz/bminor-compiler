from bminor.parser.model import Node

from rich.console import Console
from rich.table 	import Table
from rich 		    import print

class Symtab:
	class SymbolDefinedError(Exception):
		'''
    An exception is thrown when code attempts to add a
    symbol to a table where the symbol has already been defined.
		'''
		pass
		
	class SymbolConflictError(Exception):
		'''
    An exception occurs when code attempts to add
    a symbol to a table where the symbol already exists and its type
    differs from the previously existing one.
		'''
		pass
		
	def __init__(self, name, parent=None):
		'''
    Create a empty symbols table with a given parent table.
		'''
		self.name = name
		self.entries = {}
		self.parent = parent

		if self.parent:
			self.parent.children.append(self)

		self.children = []

	def __getitem__(self, name):
		return self.entries[name]

	def __setitem__(self, name, value):
		self.entries[name] = value

	def __delitem__(self, name):
		del self.entries[name]

	def __contains__(self, name):
		if name in self.entries:
			return self.entries[name]
		return False

	def add(self, name, value):
		'''
    Adds a symbol with the given value to the symbol table.
    The value is usually an AST node representing the declaration
    or definition of a function or variable (e.g., Declaration
    or FuncDeclaration)
		'''
		if name in self.entries:
			if self.entries[name].type != value.type:
				raise Symtab.SymbolConflictError()
			else:
				raise Symtab.SymbolDefinedError()

		self.entries[name] = value
		
	def get(self, name):
		'''
    Retrieves the symbol with the given name from the symbol table, 
    traversing upwards through the main symbol tables if it is not 
    found in the current one.
		'''
		if name in self.entries:
			return self.entries[name]
		elif self.parent:
			return self.parent.get(name)

		return None
		
	def print(self):
		table = Table(title = f"\nSymbol Table: '{self.name}'")
		table.add_column('key', style='cyan')
		table.add_column('value', style='bright_green')
		
		for k, v in self.entries.items():
			value = f"{v.__class__.__name__}({v.name})" if isinstance(v, Node) else f"{v}"
			table.add_row(k, value)

		print(table)
		
		for child in self.children:
			child.print()