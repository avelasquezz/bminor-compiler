# Errors management for B-Minor language

from rich import print, Table

_errors_detected = 0

def error(message, lineno = None):
  global _errors_detected
  _errors_detected += 1

  where = f"{lineno}: " if lineno else ""

  print(f"[red]{where}{message}[/red]")
 
def errors_detected():
  global _errors_detected

  print(
      f"[red]Errors: {_errors_detected}[/red]" if _errors_detected 
    else 
      f"[green]Errors: {_errors_detected}[/green]"
  )

def clear_errors():
  global _errors_detected
  _errors_detected = 0