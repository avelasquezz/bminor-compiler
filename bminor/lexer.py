import sly

from bminor.errors import error, errors_detected
from rich.table import Table
from rich.console import Console 
from bminor.utils import unescape_char, unescape_string

class Lexer(sly.Lexer):
  tokens = {
    # Reserved words
    "ARRAY", "AUTO", "BOOLEAN", "CHAR", "ELSE", "FALSE", 
    "FLOAT", "FOR", "FUNCTION", "IF", "INTEGER", "PRINT", 
    "RETURN", "STRING", "TRUE", "VOID", "WHILE", "DO",

    # Operators
    "NOT", "LT", "LE", "GT", "GE", "EQ", "NE", "LAND", "LOR", "INC", "DEC",

    # Other symbols
    "ID", "INTEGER_LITERAL", "FLOAT_LITERAL", "CHAR_LITERAL", "STRING_LITERAL",
  }

  literals = "+-*/%^=()[]{}:;,"

  @_(r"[0-9]+[a-zA-Z][a-zA-Z0-9_]*")
  def error_invalid_identifier(self, token):
    error(f"Illegal identiifer '{token.value}'", token.lineno, "Lexical")
    self.index += 1

  ID = r"[a-zA-Z_][a-zA-Z0-9_]*" 

  ID['array'] = "ARRAY"
  ID['auto'] = "AUTO"
  ID['boolean'] = "BOOLEAN"
  ID['char'] = "CHAR"
  ID['do'] = "DO"
  ID['else'] = "ELSE"
  ID['false'] = "FALSE"
  ID['float'] = "FLOAT"
  ID['for'] = "FOR"
  ID['function'] = "FUNCTION"
  ID['if'] = "IF"
  ID['integer'] = "INTEGER"
  ID['print'] = "PRINT"
  ID['return'] = "RETURN"
  ID['string'] = "STRING"
  ID['true'] = "TRUE"
  ID['void'] = "VOID"
  ID['while'] = "WHILE"

  FLOAT_LITERAL = r"[0-9]*\.[0-9]+"
  INTEGER_LITERAL = r"[0-9]+"
  CHAR_LITERAL = r"'([\x20-\x7E]|\\([abefnrtv\\'\"]|0x[0-9a-fA-F]{2}))'" 
  STRING_LITERAL = r"\"([^\"\\]|\\.)*\""

  # Relational operators
  NOT = r"!"
  LE = r"<=" 
  GE = r">="
  LT = r"<"
  GT = r">"
  NE = r"!="
  EQ = r"=="

  # Logical operators
  LAND = r"&&"
  LOR = r"\|\|"
  
  INC = r"\+\+"
  DEC = r"\-\-"

  # Ignored characters
  ignore = " \t\r"
  ignore_cppcomments = r"//.*"

  @_(r"\n+")
  def ignore_new_line(self, token):
    self.lineno += token.value.count("\n")

  @_(r"/\*(.|\n)*\*/")
  def ignore_multiline_comment(self, token):
    self.lineno += token.value.count('\n')

  @_(r"[0-9]+")
  def INTEGER_LITERAL(self, token):
    token.value = int(token.value)
    return token
  
  @_(r"[0-9]*\.[0-9]+")
  def FLOAT_LITERAL(self, token):
    token.value = float(token.value)
    return token
  
  @_(r"'([\x20-\x7E]|\\([abefnrtv\\'\"]|0x[0-9a-fA-F]{2}))'")
  def CHAR_LITERAL(self, token):
    inner = token.value[1:-1]
    
    try:
      token.value = unescape_char(inner) 
    except ValueError as err:
      error(str(err), token.lineno, "Lexical")
      token.value = None

    return token
  
  @_(r"\"([^\"\\]|\\.)*\"")
  def STRING_LITERAL(self, token):
    inner = token.value[1:-1]
    token.value = unescape_string(inner)

    return token
  
  def error(self, token):
    error(f"Illegal character {token.value[0]}", token.lineno, "Lexical")
    self.index += 1
  
def tokenize(code):
  lexer = Lexer()

  table = Table(show_lines = True)
  table.add_column("Type", justify = "center")
  table.add_column("Value", justify = "center")
  table.add_column("Line number", justify = "center")

  for token in lexer.tokenize(code):
    table.add_row(token.type, str(token.value), str(token.lineno))

  if errors_detected() == 0:
    console = Console()
    console.print(table)