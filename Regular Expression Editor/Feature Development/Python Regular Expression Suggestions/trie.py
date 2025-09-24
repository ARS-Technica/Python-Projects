# token-aware Trie
import re
from typing import Dict, List


class TrieNode:
    """A Trie is a tree where each edge represents a character. 
    Leaf nodes mark the end of a string. This structure allows 
    us to efficiently represent shared prefixes among test cases.
    """

    def __init__(self):
        self.children = {} # key: character, value: TrieNode
        self.is_end = False


class Trie:
    """Trie structure for storing test cases."""
    def __init__(self):
        self.root = TrieNode()
  
    pass

    def insert(self, word: str):
        """Insert a word into the Trie.""" 

        pass

    def build_from_list(self, words: list[str]):
        """Build the trie from a list of words."""
        for word in words:
            self.insert(word)


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
