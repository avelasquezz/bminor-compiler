from bminor.lexer import tokenize 

if __name__ == "__main__":
  import sys
  
  if len(sys.argv) != 2:
    print("Usage: python lexer.py filename")
    exit(1)
  
  tokenize(open(sys.argv[1], encoding = "utf-8").read())