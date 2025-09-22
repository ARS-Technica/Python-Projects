# token-aware Trie
import re
from typing import Dict, List


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False


class Trie:
  pass


# -------------------------------
# Helper function
# -------------------------------
def escape_regex_char(char: str) -> str:
    """
    Escapes regex special characters.
    """
    if re.match(r"[a-zA-Z0-9]", char):
        return char
    else:
        return "\\" + char
