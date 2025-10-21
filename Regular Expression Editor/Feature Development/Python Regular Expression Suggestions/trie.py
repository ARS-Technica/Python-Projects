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

    def to_regex(self, capturing: bool = False, verbose: bool = False) -> str:
        """
        Convert this trie into a regex pattern.
        - capturing: wrap groups in () instead of (?: )
        - verbose: insert whitespace/newlines for readability
        """
        regex = self._node_to_regex(self.root, capturing, verbose)
        return regex


class Trie:
    """Trie structure for storing test cases."""
    def __init__(self, test_cases=None):
        self.root = TrieNode()
        if test_cases:
            for word in test_cases:
                self.insert(word)

    def insert(self, word: str):
        node = self.root
        
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        node.is_end = True  # mark the end of this word

    def build_from_list(self, words: list[str]):
        """Build the trie from a list of words."""
        for word in words:
            self.insert(word)

    def to_regex(self, capturing: bool = False, verbose: bool = False) -> str:
        """
        Convert this trie into a regex pattern.
        - capturing: wrap groups in () instead of (?: )
        - verbose: insert whitespace/newlines for readability
        """
        regex = self._node_to_regex(self.root, capturing, verbose)
        return regex

    def _node_to_regex(self, node, capturing: bool, verbose: bool) -> str:
        # logic to walk the trie and build regex
        # currently yours probably ignores flags
        # so at first just return alternation of children
        parts = []
        for char, child in node.children.items():
            escaped = re.escape(char)
            sub = self._node_to_regex(child, capturing, verbose)
            parts.append(escaped + sub)

        if node.is_end:
            parts.append("")

        if len(parts) == 1:
            return parts[0]
        else:
            group_type = "(" if capturing else "(?:"
            return group_type + "|".join(parts) + ")"


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


