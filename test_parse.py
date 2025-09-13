from bminor.parser import parse

code = """
 x : function integer () = { };
"""

ast = parse(code)
print(ast)
