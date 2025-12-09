# token-aware Trie
import re
from typing import Dict, List


class TrieNode:
    """A Trie is a tree where each edge represents a character. 
    Leaf nodes mark the end of a string. This structure allows 
    us to efficiently represent shared prefixes among test cases.
    """

    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end: bool = False

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
        
        for char, child in sorted(node.children.items()):
            sub = self._node_to_regex(child, capturing, verbose)
            # Escape only the current char (literal) if sub is empty (leaf)
            if child.is_end and not child.children:
                parts.append(re.escape(char) + sub)
            else:
                parts.append(char + sub)
                
        if len(parts) == 1:
            return parts[0]
        else:
            return "(?:" + "|".join(parts) + ")"
        

class Trie:
    """Trie structure for storing test cases."""
    
    def __init__(self, token_lists: List[List[str]] = None):
        self.root = TrieNode()
        if token_lists:
            for tokens in token_lists:
                self.insert_tokens(tokens)

    def insert_tokens(self, tokens: List[str]):
        """Insert a token sequence into the trie."""
        node = self.root
        for token in tokens:
            if token not in node.children:
                node.children[token] = TrieNode()
            node = node.children[token]
        node.is_end = True

    def to_regex(self, capturing: bool = False, verbose: bool = False) -> str:
        """
        Convert the trie into a regex string.
        Only leaf nodes are escaped, internal nodes are treated as literals.
        """
        
        pattern = self._node_to_regex(self.root, capturing, verbose)
        
        if capturing:
            return f"({pattern})"
        else:
            return f"(?:{pattern})"
    
    def _node_to_regex(self, node: TrieNode, capturing: bool, verbose: bool) -> str:
        """Recursive helper to convert a node and its children to regex."""
        
        if node.is_end and not node.children:
            # Leaf node → no further children, safe to escape
            return ""

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


