# Errors management for B-Minor language

from rich.markup import escape
from rich        import print 

_errors_detected = 0

def error(message, lineno = None, error_type = None):
  global _errors_detected
  _errors_detected += 1

  print(f"[red][bold]{error_type + " " if error_type else ""}Error at {lineno}: [/]{message}[/]")
 
def errors_detected():
  global _errors_detected
  return _errors_detected

def clear_errors():
  global _errors_detected
  _errors_detected = 0