from bminor.lexer import Lexer
from bminor.errors import errors_detected

if __name__ == "__main__":
  with open("./test/scanner/sieve.bminor", "r") as file:
    code = file.read()
  
  lexer = Lexer()

  for token in lexer.tokenize(code):
    print(token)
  
  errors_detected()