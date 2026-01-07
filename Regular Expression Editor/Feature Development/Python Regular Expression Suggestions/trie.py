# token-aware Trie
import re
from typing import Dict, List

# Sentinel to mark tokens that are already regex fragments and must not be escaped/split.
_FRAGMENT_SENTINEL = "\x00"

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
            
    def _node_to_regex(self, node: TrieNode) -> str:
        """
        Recursively convert a node into a regex fragment.
        - child token keys are used verbatim; fragment tokens begin with the sentinel.
        - if node.is_end is True, we include the empty alternative (word termination).
        """

        parts = []

        # If node is end-of-word, allow terminating here (empty string alternative)
        if node.is_end:
            parts.append("")
        
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

    def compress_digit_alternation(self, strings: list[str]) -> str | None:
        """
        If all strings are digit-only, return a \d{min,max} pattern.
        Otherwise return None.
        """
        
        if all(s.isdigit() for s in strings):
            lengths = [len(s) for s in strings]
            min_len, max_len = min(lengths), max(lengths)

            if min_len == max_len:
                return rf"\d{{{min_len}}}"
            else:
                return rf"\d{{{min_len},{max_len}}}"
        
        return None

    def _collect_string(self, node):
        """
        Collect literal string from node to its leaves.
        """
        
        if node.is_leaf and not node.children:
            return [node.char] if node.char else []
        result = [node.char] if node.char else []

            
        return result
    
    def _node_to_regex(self, node: TrieNode) -> str:
        """
        Recursively convert a node into a regex fragment.
        - child token keys are used verbatim; fragment tokens begin with the sentinel.
        - if node.is_end is True, we include the empty alternative (word termination).
        """
        
        parts = []

        # If node is end-of-word, allow terminating here (empty string alternative)
        if node.is_end:
            parts.append("")

        # deterministic order
        for token in sorted(node.children.keys()):
            child = node.children[token]
            sub = self._node_to_regex(child)
            if token.startswith(_FRAGMENT_SENTINEL):
                # fragment token; insert verbatim (no escaping)
                frag = token[1:]
                parts.append(frag + sub)
            else:
                # literal token (single character) — escape it
                parts.append(re.escape(token) + sub)

        if not parts:
            return ""   # no alt

        if len(parts) == 1:
            return parts[0]
        return "(?:" + "|".join(parts) + ")"

    def to_regex(self, capturing: bool = False) -> str:
        """Return the regex body for the entire trie. Optionally wrap in a capturing group."""
        
        body = self._node_to_regex(self.root, capturing=capturing, verbose=verbose)
        
        if capturing:
            return f"({body})"
        return body

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


