import sly

from .errors import error, errors_detected
from rich.table import Table
from rich.console import Console 

class Lexer(sly.Lexer):
  tokens = {
    # Reserved words
    ARRAY, AUTO, BOOLEAN, CHAR, ELSE, FALSE, 
    FLOAT, FOR, FUNCTION, IF, INTEGER, PRINT, 
    RETURN, STRING, TRUE, VOID, WHILE,

    # Operators
    NOT, LT, LE, GT, GE, EQ, NE, LAND, LOR, INC, DEC,

    # Other symbols
    ID, INTEGER_LITERAL, FLOAT_LITERAL, CHAR_LITERAL, STRING_LITERAL,
  }

  literals = "+-*/%^=()[]{}:;,"

  ID = r"[a-zA-Z_][a-zA-Z0-9_]*" 

  ID['array'] = ARRAY
  ID['auto'] = AUTO
  ID['boolean'] = BOOLEAN
  ID['char'] = CHAR
  ID['else'] = ELSE
  ID['false'] = FALSE
  ID['float'] = FLOAT
  ID['for'] = FOR
  ID['function'] = FUNCTION
  ID['if'] = IF
  ID['integer'] = INTEGER
  ID['print'] = PRINT
  ID['return'] = RETURN
  ID['string'] = STRING
  ID['true'] = TRUE
  ID['void'] = VOID
  ID['while'] = WHILE

  INTEGER_LITERAL = r"[0-9]+"
  FLOAT_LITERAL = r"[0-9]*\.[0-9]+"
  CHAR_LITERAL = r"'([\x20-\x7E]|\\([abefnrtv\\'\"]|0x[0-9a-fA-F]{2}))'" 
  STRING_LITERAL = r"\"[\x20-\x7E]*\""

  # Relational operators
  NOT = r"!"
  LT = r"<"
  LE = r"<=" 
  GT = r">"
  GE = r">="
  EQ = r"=="
  NE = r"!="

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
    self.lineno = token.value.count('\n')

  def error(self, token):
    error(f"Illegal character {token.value[0]}", token.lineno)
    self.index += 1

def tokenize(code):
  lexer = Lexer()

  table = Table(show_lines = True)
  table.add_column("Type", justify = "center")
  table.add_column("Value", justify = "center")
  table.add_column("Line number", justify = "center")

  for token in lexer.tokenize(code):
    table.add_row(token.type, token.value, str(token.lineno))
  
  console = Console()
  console.print(table)
  
  errors_detected()