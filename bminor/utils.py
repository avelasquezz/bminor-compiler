def unescape_char(char):
  # Converts the content of a CHAR_LITERAL into a single character.
  escapes = {
    "n": "\n",
    "t": "\t",
    "r": "\r",
    "\\": "\\",
    "'": "'",
    '"': '"',
    "0": "\0"
  }

  # A character without escape
  if len(char) == 1:
    return char

  # Standard scape. Example: '\n'
  if len(char) == 2 and char[0] == "\\" and char[1] in escapes:
    return escapes[char[1]]

  # Hex escape. Example: \0xHH
  if char.startswith("0x") and len(char) == 4:
    try:
      return chr(int(char[2:], 16))
    except ValueError:
      raise ValueError(f"Invalid hex escape: {char}")

  # Default error
  raise ValueError(f"Invalid char literal: {char}")

def unescape_string(string):
  return bytes(string, "utf-8").decode("unicode_escape")