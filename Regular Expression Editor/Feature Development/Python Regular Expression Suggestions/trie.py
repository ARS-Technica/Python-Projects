# token-aware Trie
import re
from typing import Dict, List

# Sentinel to mark tokens that are already regex fragments and must not be escaped/split.
_FRAGMENT_SENTINEL = "\x00"

class TrieNode:
    """
    Token-aware Trie.
    Each inserted item is a sequence of tokens. A token is either:
      - a single literal character (e.g. 'a'), OR
      - a *regex fragment token* (prefixed with _FRAGMENT_SENTINEL) that is treated as atomic
        (e.g. '\x00(?:abc){2}' or '\x00\d{1,3}').
    The Trie builds alternations over token sequences and outputs a regex string where:
      - literal-character tokens are escaped (re.escape),
      - fragment tokens are inserted verbatim (no escaping).
    """

    def __init__(self, token_lists: List[List[str]] = None):
        self.root = TrieNode()
        if token_lists:
            for tokens in token_lists:
                self.insert_tokens(tokens)


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

    def _node_to_regex(self, node, capturing: bool = False, verbose: bool = False):
            """
            Recursive helper to convert a TrieNode and its children to a regex string.
            Escapes only literal character tokens. Leaves atomic regex fragments intact.
            """
            parts = []
        
            for token, child in node.children.items():
                # Recurse into child nodes
                sub = self._node_to_regex(child, capturing=capturing, verbose=verbose)

                # CRITICAL CHECK: If the token starts with a non-capturing group (?:, it's an atomic fragment.
                if token.startswith("(?:") or re.match(r"^\\[dwsDWS]", token) or re.match(r"^\.\\*$", token):
                    parts.append(token + sub)
                else:
                    parts.append(re.escape(token) + sub)

            if not parts:
                return ""
                if len(parts) == 1:
                    return parts[0]
                return "(?:" + "|".join(parts) + ")"

    def to_regex(self, capturing=False, verbose=False):
        """Return the regex body for the entire trie. Optionally wrap in a capturing group.
        Pass verbose=True to include spaces for verbose regex mode."""
        
        # Get the regex from the root
        body = self._node_to_regex(self.root, capturing, verbose)
        
        # Wrap in capturing group if requested
        if capturing:
            return f"({body})"
        
        return body

    def _collect_string(self, node):
        """
        Collect literal string from node to its leaves.
        """
        if node.is_leaf and not node.children:
            return [node.char] if node.char else []
            
        result = [node.char] if node.char else []
        
        for child in node.children.values():
            result.extend(self._collect_string(child))
            
        return result    
    
    def compress_digit_alternation(regex: str) -> str:
        """
        If the regex is an alternation of pure digits (e.g. (?:123|45|7)),
        compress it into a \d{min,max} form.
        Otherwise return it unchanged.
        """

        # Match things like (?:123|45|7)
        m = re.fullmatch(r"\(\?:([0-9]+(?:\|[0-9]+)*)\)", regex)
        
        if not m:
            return regex

        parts = m.group(1).split("|")
        if all(part.isdigit() for part in parts):
            lengths = [len(p) for p in parts]
            min_len, max_len = min(lengths), max(lengths)
            if min_len == max_len:
                return rf"\d{{{min_len}}}"
            return rf"\d{{{min_len},{max_len}}}"

        return regex

