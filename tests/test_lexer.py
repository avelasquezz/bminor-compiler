import pytest
from bminor.lexer import tokenize, Lexer
from bminor.errors import clear_errors, errors_detected

def lex(code):
  """
    Utility: run the lexer and return the tokens as a list of tuples (type, value, lineno).
  """
  clear_errors()
  lexer = Lexer()
  return [(t.type, t.value, t.lineno) for t in lexer.tokenize(code)]

# 10 good test 
def test_integer_literal():
  tokens = lex("x: integer = 123;")
  assert ("INTEGER_LITERAL", 123, 1) in tokens
  assert errors_detected() == 0

def test_string_literal_simple():
  tokens = lex('msg: string = "Hello";')
  assert ("STRING_LITERAL", "Hello", 1) in tokens
  assert errors_detected() == 0

def test_char_literal_escape():
  tokens = lex(r"c: char = '\0x41';")
  assert ("CHAR_LITERAL", "A", 1) in tokens
  assert errors_detected() == 0

def test_string_literal_escape():
  tokens = lex("msg: string = \"Hola\nMundo\";") 
  assert errors_detected() == 0

def test_increase_operator():
  tokens = lex("a++;") 
  assert ("INC", "++", 1) in tokens
  assert errors_detected() == 0

def test_decrease_operator():
  tokens = lex("b--;") 
  assert ("DEC", "--", 1) in tokens
  assert errors_detected() == 0