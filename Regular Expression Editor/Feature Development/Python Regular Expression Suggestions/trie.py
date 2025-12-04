# token-aware Trie
import re
from typing import Dict, List


class TrieNode:
    """A Trie is a tree where each edge represents a character. 
    Leaf nodes mark the end of a string. This structure allows 
    us to efficiently represent shared prefixes among test cases.
    """

    def __init__(self):
        self.children = {}
        self.is_end = False

    def insert(self, word: str):
        """Insert a word into the Trie."""
        node = self.root
        
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        node.is_end = True

    def build_from_list(self, words):
        """Insert a list of words into the Trie."""
        
        for word in words:
            self.insert(word)

    def to_regex(self, capturing: bool = False, verbose: bool = False) -> str:
        """
        Convert the Trie into a regex pattern.
        :param capturing: wrap pattern in capturing group if True
        :param verbose: not used directly here but could control spacing/comments
        :return: regex string
        """
        
        body = self._node_to_regex(self.root, capturing, verbose)
        if capturing:
            return f"({body})"

        return body
            
    def _node_to_regex(self, node: TrieNode, capturing: bool, verbose: bool) -> str:
        """Recursive helper to convert a node and its children to regex."""

        parts = []
        
        for char, child in node.children.items():
            # Recursively build regex for children
            sub = self._node_to_regex(child, capturing, verbose)
            # Escape only literal characters
            parts.append(re.escape(char) + sub)
            
        if node.is_end:
            # Empty string indicates this node can terminate a word
            parts.append("")

        if not parts:
            return ""
        elif len(parts) == 1:
            return parts[0]
        else:
            return "(?:" + "|".join(parts) + ")"
        

class Trie:
    """Trie structure for storing test cases."""
    
    def __init__(self, words=None):
        self.root = TrieNode()
        if words:
            for word in words:
                self.insert(word)

    def insert(self, word: str):
        """Insert a word into the trie."""
        
        node = self.root
        
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            
        node.is_end = True

    def to_regex(self, capturing: bool = False, verbose: bool = False) -> str:
        """
        Convert the Trie into a regex pattern.
        :param capturing: wrap pattern in capturing group if True
        :param verbose: not used directly here but could control spacing/comments
        :return: regex string
        """
        
        return none
    
    def _node_to_regex(self, node, capturing: bool, verbose: bool):
        """Recursive helper to convert a node and its children to regex."""
        
        parts = []
        
        for char, child in node.children.items():
            sub = self._node_to_regex(child, capturing, verbose)
            parts.append(re.escape(char) + sub)

        if node.is_end:
            parts.append("")  # allow ending here

        if not parts:
            return ""

        if len(parts) == 1:
            return parts[0]
        else:
            inner = "|".join(parts)
            if verbose:
                inner = "\n  " + "\n  | ".join(parts) + "\n"
            return f"(?:{inner})"

    def to_regex(self, capturing: bool = False, verbose: bool = False) -> str:
        """Convert the entire trie into a regex."""
        if not node:
            return ""
            
        parts = []
        
        for char, child in node.items():
            # Escape only literal chars
            if len(char) == 1:  # a single input symbol
                escaped = re.escape(char)
            else:
                # Already a regex fragment (like "(?:abc){2}")
                escaped = char
            parts.append(escaped + to_regex(child))

        """
        # Case-insensitive mode → lowercase normalization
        if config.is_case_insensitive_matching:
            lowered = [t.lower() for t in test_cases]
            unique = sorted(set(lowered))
            pattern_body = "|".join(unique)   # 🔥 no re.escape
            flags = "(?i)"
        else:
            unique = sorted(set(test_cases))
            pattern_body = "|".join(unique)   # 🔥 no re.escape
            flags = ""
        """
            
        return "(?:" + "|".join(parts) + ")"


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

"""
# Test Usage for Debugging

trie = Trie()
trie.build_from_list(["123", "45", "7"])
pattern = trie.to_regex()
print(pattern)

# Output: ^(?:123|45|7)$
"""


