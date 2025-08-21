# Errors management for B-Minor language

from rich import print

_errors_detected = 0

def error(message, lineno=None):
  global _errors_detected
  if lineno:
    print(f"{lineno}: [red]{message}[/red]")
  else:
    print(f"[red]{message}[/red]")
  _errors_detected += 1
 
def errors_detected():
  global _errors_detected
  if _errors_detected == 0:
    print(f"[green]Errors detected: {_errors_detected}[/green]")
  else:
    print(f"[red]Errors detected: {_errors_detected}[/red]")

def clear_errors():
  global _errors_detected
  _errors_detected = 0