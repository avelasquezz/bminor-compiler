# Errors management for B-Minor language

from rich import print 
from rich.markup import escape

_errors_detected = 0

def error(message, lineno = None):
  global _errors_detected
  _errors_detected += 1

  where = f"{lineno}: " if lineno else ""

  print(f"[red]{escape(where + message)}[/red]")
 
def errors_detected():
  global _errors_detected
  return _errors_detected

def clear_errors():
  global _errors_detected
  _errors_detected = 0