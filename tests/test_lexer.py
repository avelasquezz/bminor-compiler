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

def test_float_literal():
  tokens = lex("number: float = .59;")
  assert ("FLOAT_LITERAL", 0.59, 1) in tokens
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

def test_and_logical():
  tokens = lex("a&&b;") 
  assert ("LAND", "&&", 1) in tokens
  assert errors_detected() == 0

def test_array_literal():
  tokens = lex("a: array[3] integer") 
  assert ("ARRAY", "array", 1) in tokens
  assert errors_detected() == 0


# 10 bad tests

def test_illegal_character():
  tokens = lex("x = 5 # y;")
  assert ("#", '#', 1) not in tokens
  assert errors_detected() > 0

def test_invalid_identifier_number_prefix():
  tokens = lex("1a: integer;")
  assert ("ID", "1a", 1) not in tokens
  assert errors_detected() == 1

def test_invalid_float_literal():
  tokens = lex("number: float = 27.;")
  assert ("FLOAT_LITERAL", 27., 1) not in tokens
  assert errors_detected() > 0 

def test_invalid_string_literal_unclosed():
  tokens = lex("s: string = \"hello;")
  assert not ("STRING_LITERAL", "hello", 1) in tokens
  assert errors_detected() > 0

def test_invalid_char_literal():
  tokens = lex("c: char = 'ab';")
  assert ("CHAR_LITERAL", "ab", 1) not in tokens
  assert errors_detected() > 0

def test_invalid_char_literal():
  tokens = lex("c: char = 'ab';")
  assert ("CHAR_LITERAL", "ab", 1) not in tokens
  assert errors_detected() > 0

def test_multiple_lexical_errors():
  # Este código contiene 3 errores:
  # 1. Un identificador que comienza con un número: '1var'
  # 2. Un carácter ilegal: '#'
  # 3. Un literal de cadena sin cerrar: "cadena_rota
  code_with_errors = """ 
  1var: integer = 1; 
  y = 2#; 
  s: string = "hello;
  """
  tokens = lex(code_with_errors)
  assert ("ID", "1var", 2) not in tokens
  assert ("#", "#", 3) not in tokens
  assert ("STRING_LITERAL", "hello", 4) not in tokens
  assert errors_detected() == 3

def test_invalid_char_literal_bad_escape():
  tokens = lex("c: char = '\\q';")
  assert ("STRING_LITERAL", "\q", 1) not in tokens
  assert errors_detected() > 0

def test_invalid_hex_escape_in_char():
  tokens = lex("c: char = '\\0xC8';")
  assert errors_detected() > 0

# def test_unclosed_multiline_comment():
#   tokens = lex("/* This comment is never closed")
#   assert errors_detected() > 0

def test_or_logical():
  tokens = lex("a | b")
  assert ("LOR", "|", 1) not in tokens
  assert errors_detected() == 1

def test_function_definition_error():
  code = """
  my_func: function @ integer (x: integer) = {
    return 1;
  }
  """
  tokens = lex(code)
  assert ("@", "@", 2) not in tokens
  assert errors_detected() > 0