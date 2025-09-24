# token-aware Trie
import re
from typing import Dict, List


class TrieNode:
    """A node in the Trie."""

    def __init__(self):
        self.children = {} # key: character, value: TrieNode
        self.is_end = False


class Trie:
    """Trie structure for storing test cases."""
    def __init__(self):
        self.root = TrieNode()
  
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
