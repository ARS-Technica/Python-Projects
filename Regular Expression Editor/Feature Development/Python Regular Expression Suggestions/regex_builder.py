"""
A Python module to generate regular expressions from example strings.

This module provides a RegExpBuilder class to:
- Accept example test cases
- Configure regex generation rules
- Build the most specific regular expression matching the examples

The module mirrors the functionality of the Grex Rust library.
"""

 
from collections import defaultdict
from pathlib import Path
import re
from trie import Trie, _FRAGMENT_SENTINEL
from regex_builder import RegExpConfig
from typing import List, Optional, Union

 
# ---------------- RegExpConfig ----------------

'''
class RegExpConfig:
    def __init__(self):
    """
    Holds all configuration options for regex generation.
    Mirrors the settings from the Rust version of grex.

    Attributes mirror the settings used in the Rust version:
    - digit conversion
    - whitespace conversion
    - word conversion
    - repetition detection
    - case-insensitivity
    - start/end anchors
    - capturing groups
    - verbose mode
    - non-ASCII escaping
    """
 
        # Case-insensitive matching
        self.is_case_insensitive_matching = False

        # Verbose mode
        self.is_verbose_mode_enabled = False

        # Capturing groups
        self.is_capturing_group_enabled = False

        # Anchors
        self.is_start_anchor_disabled = False
        self.is_end_anchor_disabled = False

        # Character classes
        self.is_digit_class_enabled = False
        self.is_word_class_enabled = False
        self.is_whitespace_class_enabled = False

        # Repetition detection
        self.minimum_repetitions = 2
        self.minimum_substring_length = 1

        # Character conversions
        self.is_digit_converted = False
        self.is_non_digit_converted = False
        self.is_space_converted = False
        self.is_non_space_converted = False
        self.is_word_converted = False
        self.is_non_word_converted = False

        # Pattern optimizations
        self.is_repetition_converted = False
        self.minimum_repetitions = 2
        self.minimum_substring_length = 1

        # Matching behavior
        self.is_case_insensitive_matching = False
        self.is_capturing_group_enabled = False
        self.is_verbose_mode_enabled = False

        # Anchors
        self.is_start_anchor_disabled = False
        self.is_end_anchor_disabled = False

        # Escaping
        self.is_non_ascii_char_escaped = False
        self.is_astral_code_point_converted_to_surrogate = False
'''

class RegexConfig:
    def __init__(self, case_insensitive=False, digits_only=False, verbose=False, capturing=False):
        self.case_insensitive = case_insensitive
        self.digits_only = digits_only
        self.verbose = verbose
        self.capturing = capturing

 
# ---------- Helpers ----------

def _is_regex_fragment_token(s: str) -> bool:
    """Rudimentary check: treat strings containing backslash, parentheses, braces,
    or '?:' as already-formed regex fragments."""
 
    # This is conservative: if the string contains any of these characters, we will
    # treat it as a fragment token (atomic) and not escape/split it.
    return any(ch in s for ch in ("\\", "(", ")", "{", "}", "[", "]", "?"))


def _tokenize_fragment(fragment: str, is_regex: bool):
    """
    Convert a string fragment into a list of tokens for the Trie.
    
    - Regex fragments are treated as atomic single tokens.
    - Literal fragments are split into characters.
    """

    if is_regex:
        # Atomic token: keep as-is
        return [fragment]
    else:
        # Split literal into individual characters
        return list(fragment)
 

def _all_digits_fastpath(test_cases: List[str]) -> Tuple[bool, int, int]:
    """Return (all_digits, min_len, max_len)."""
 
    if not test_cases:
        return (False, 0, 0)
     
    lens = []
 
    for s in test_cases:
        if not s.isdigit():
            return (False, 0, 0)
        lens.append(len(s))
     
    return (True, min(lens), max(lens))


def _common_two_word_pattern(test_cases: List[str]) -> bool:
    """True if every test case is two whitespace-separated alphabetic tokens."""

    for s in test_cases:

        parts = s.split()

        if len(parts) != 2:
            return False
        if not (parts[0].isalpha() and parts[1].isalpha()):
            return False

    return True


def _alpha_prefix_digit_suffix_pattern(test_cases: List[str]) -> Tuple[bool, int]:
    """
    Detect patterns like letters+digits where every example matches ([A-Za-z]+)(\d+)
    and all digit suffixes have equal length. Returns (True, digits_len) or (False,0).
    """
 
    suf_len = None

    for s in test_cases:
        m = re.match(r"^([A-Za-z]+)(\d+)$", s)

        if not m:
            return (False, 0)
        
        dlen = len(m.group(2))

        if suf_len is None:
            suf_len = dlen
        elif suf_len != dlen:
            return (False, 0)

    return (True, suf_len or 0)


def _node_to_regex(node, capturing: bool = False, verbose: bool = False):
    """
    Recursive helper to convert a TrieNode and its children to a regex string.

    - Escapes only literal character tokens
    - Leaves atomic regex fragments (from detect_repetition or digits) intact
    """

    parts = []

    for token, child in node.children.items():
        # Recurse into child nodes
        sub = _node_to_regex(child, capturing=capturing, verbose=verbose)

        # Determine if token is an atomic regex fragment (starts with (?: or \d)
        if token.startswith("(?:") or re.match(r"\\[dws]", token):
            parts.append(token + sub)
        else:
            parts.append(re.escape(token) + sub)

    if not parts:
        return ""
    
    if len(parts) == 1:
        return parts[0]
    
    return "(?:" + "|".join(parts) + ")"
 

class RegExpBuilder:
    """
    Builds regexes from test cases using the configured settings.
    """
     
    MISSING_TEST_CASES_MESSAGE = "No test cases have been provided for regular expression generation"
    MINIMUM_REPETITIONS_MESSAGE = "Quantity of minimum repetitions must be greater than zero"
    MINIMUM_SUBSTRING_LENGTH_MESSAGE = "Minimum substring length must be greater than zero"

    def __init__(self, test_cases: list[str], config: RegexConfig | None = None):
        self.test_cases = test_cases
        self.config = config or RegexConfig()

    @classmethod
    def from_test_cases(cls, data, config: RegexConfig | None = None) -> "RegExpBuilder":
        """
        Factory method that takes either:
        - a multi-line string of test cases, or
        - a list of test case strings.
    
        Returns a RegExpBuilder instance.
        """
     
        if isinstance(data, str):
            samples = [line.strip() for line in data.splitlines() if line.strip()]
        elif isinstance(data, list):
            samples = [s.strip() for s in data if isinstance(s, str) and s.strip()]
        else:
            raise TypeError(f"Unsupported input type for from_test_cases: {type(data)}")
        
        return cls(samples, config=config)

    def generate(self) -> str:
        """Build the regex string using the config settings."""
        from trie import Trie

        # special cases first
        if self.config.digits_only and all(s.isdigit() for s in self.samples):
            lengths = sorted({len(s) for s in self.samples})
            return f"^\\d{{{min(lengths)},{max(lengths)}}}$"

        if self.config.case_insensitive and len(set(s.lower() for s in self.samples)) == 1:
            return f"(?i)^{self.samples[0].lower()}$"

        if self.config.verbose:
            # very rough heuristic for verbose — example only
            return "(?x)^(" + r"\w+\s\w+" + ")$"

        # fallback: build a trie
        trie = Trie()
     
        for sample in self.samples:
            trie.insert(sample)
         
        regex_body = trie.to_regex(
            capturing=self.config.capturing,
            verbose=self.config.verbose,
        )

        prefix = ""
     
        if self.config.case_insensitive:
            prefix += "(?i)"
        if self.config.verbose:
            prefix += "(?x)"

        return f"{prefix}^{regex_body}$"

    # -------------------------------
    # Conversion methods
    # -------------------------------
    def with_conversion_of_digits(self, enabled: bool = True):
        self.config.is_digit_conversion_enabled = enabled
        return self
     
    def with_case_insensitive(self, enabled: bool = True):
        self.config.is_case_insensitive_matching = enabled
        return self

    def with_verbose_mode(self, enabled: bool = True):
        self.config.is_verbose_mode = enabled
        return self
      
    def with_conversion_of_whitespace(self):
        self.config.convert_whitespace = True
        return self

    def with_conversion_of_non_whitespace(self):
        self.config.convert_non_whitespace = True
        return self

    def with_conversion_of_words(self):
        self.config.convert_words = True
        return self

    def with_conversion_of_non_words(self):
        self.config.convert_non_words = True
        return self

    # -------------------------------
    # Repetition & substring methods
    # -------------------------------
    def with_conversion_of_repetitions(self, enabled: bool = True):
        self.config.is_repetition_conversion_enabled = enabled
        return self

    def with_minimum_repetitions(self, quantity: int):
        if quantity <= 0:
            raise ValueError(self.MINIMUM_REPETITIONS_MESSAGE)
        self.config.minimum_repetitions = quantity
        return self

    def with_minimum_substring_length(self, length: int):
        if length <= 0:
            raise ValueError(self.MINIMUM_SUBSTRING_LENGTH_MESSAGE)
        self.config.minimum_substring_length = length
        return self

    # -------------------------------
    # Matching and group methods
    # -------------------------------
    def with_case_insensitive_matching(self):
        self.config.case_insensitive = True
        return self

    def with_capturing_groups(self):
        self.config.capturing_groups = True
        return self

    # -------------------------------
    # Anchors
    # -------------------------------
    def with_anchors(self, enabled: bool = True):
        self.config.is_anchor_enabled = enabled
        return self
      
    def without_start_anchor(self):
        self.config.start_anchor = False
        return self

    def without_end_anchor(self):
        self.config.end_anchor = False
        return self

    def without_anchors(self):
        self.config.start_anchor = False
        self.config.end_anchor = False
        return self

    # -------------------------------
    # Misc
    # -------------------------------
    def with_escaping_of_non_ascii_chars(self, use_surrogate_pairs: bool = False):
        self.config.escape_non_ascii = True
        self.config.use_surrogate_pairs = use_surrogate_pairs
        return self

    def with_verbose_mode(self, enabled: bool = True):
        self.config.is_verbose_mode = enabled
        return self

    def with_repetitions(self, enabled: bool = True):
        self.config.is_repetition_enabled = enabled
        return self
     
    # -------------------------------
    # Core build method
    # -------------------------------
    def build(self) -> str:
        # Step 1: Build raw regex from Trie
        trie = Trie()
        trie.build_from_list(self.test_cases)
        regex = trie.to_regex()
    
        # Step 2: Apply character conversions
        regex = self.apply_character_conversions(regex)
    
        # Step 3: Apply repetition detection
        if self.config.convert_repetitions:
            regex = self.apply_repetitions(regex)
    
        # Step 4: Simplify alternations
        regex = self.simplify_alternations(regex)
    
        # Step 5: Compress character ranges
        regex = self.compress_character_ranges(regex)
    
        # Step 6: Handle anchors
        if not self.config.start_anchor:
            regex = regex.lstrip("^")
        if not self.config.end_anchor:
            regex = regex.rstrip("$")
    
        # Step 7: Escape non-ASCII characters
        if self.config.escape_non_ascii:
            regex = self.escape_non_ascii(regex)
    
        # Step 8: Apply verbose mode formatting
        regex = self.apply_verbose_mode(regex)
    
        # Step 9: Apply case-insensitive flag
        if self.config.case_insensitive:
            regex = "(?i)" + regex
    
        return regex

    # -------------------------------
    # Helper methods for build()
    # -------------------------------
    def apply_character_conversions(self, regex: str) -> str:
        """
        Apply character conversions based on config.
        """
        # Digits
        if self.config.convert_digits:
            regex = re.sub(r"[0-9]", r"\\d", regex)
        if self.config.convert_non_digits:
            regex = re.sub(r"[^0-9]", r"\\D", regex)
        
        # Whitespace
        if self.config.convert_whitespace:
            regex = re.sub(r"\s", r"\\s", regex)
        if self.config.convert_non_whitespace:
            regex = re.sub(r"\S", r"\\S", regex)
         
        # Word characters
        if self.config.convert_words:
            regex = re.sub(r"[a-zA-Z0-9_]", r"\\w", regex)
        if self.config.convert_non_words:
            regex = re.sub(r"[^a-zA-Z0-9_]", r"\\W", regex)

        return regex

    def apply_repetitions(self, regex: str) -> str:
        """
        Detect repeated substrings (including overlapping) and convert them to {min,max} quantifiers.
        Uses longest substring first for optimal compression.
        """
        min_len = self.config.minimum_substring_length
        min_rep = self.config.minimum_repetitions
        use_capturing = self.config.capturing_groups
     
        if len(regex) < min_len:
            return regex

        changed = True
     
        while changed:
            changed = False
            max_sub_len = len(regex) // 2

            best_start = best_len = best_count = 0

            # Find the substring with maximum compression
            for sub_len in range(max_sub_len, min_len - 1, -1):
                for i in range(len(regex) - sub_len + 1):
                    sub = regex[i:i + sub_len]
                    count = 1
                    # Detect overlapping repetitions
                    j = i + sub_len
                    while regex[j:j + sub_len] == sub:
                        count += 1
                        j += sub_len
                    # Check if repetition count meets minimum
                    if count >= min_rep:
                        # Compare "compression score": substring length * repeats
                        score = sub_len * count
                        best_score = best_len * best_count
                        if score > best_score:
                            best_start, best_len, best_count = i, sub_len, count
                         
            # Apply the best repetition found
            if best_count >= min_rep:
                sub = regex[best_start:best_start + best_len]
                group = f"({sub})" if use_capturing else f"(?:{sub})"
                replacement = f"{group}{{{best_count}}}"
                regex = regex[:best_start] + replacement + regex[best_start + best_len * best_count:]
                changed = True

        return regex

    def apply_verbose_mode(self, regex: str) -> str:
        """
        Apply verbose formatting for readability.
        """
        if not self.config.verbose_mode:
            return regex

        # Insert spaces around alternations for readability
        regex = regex.replace("|", " |\n")
        # Optionally, indent repeated groups
        regex = re.sub(r"(\(\?:.*?\)\{\d+\})", r"  \1", regex)
        return regex

    def compress_character_ranges(self, regex: str) -> str:
        """
        # Scans the regex for character classes and compresses sequences of consecutive characters.
        Compress character classes with consecutive characters into ranges.
        Example: [0123456789] -> [0-9], [abcdef] -> [a-f]
        """
        def compress_class(match):
            chars = sorted(match.group(1))
            result = []
            i = 0
            while i < len(chars):
                start = chars[i]
                end = start
                # Extend range as long as consecutive
                while i + 1 < len(chars) and ord(chars[i + 1]) == ord(chars[i]) + 1:
                    i += 1
                    end = chars[i]
                if start == end:
                    result.append(re.escape(start))
                else:
                    result.append(f"{re.escape(start)}-{re.escape(end)}")
                i += 1
            return "[" + "".join(result) + "]"
         
        # Match character classes
        return re.sub(r"\[([^\]]+)\]", compress_class, regex)

    def simplify_alternations(self, regex: str) -> str:
        """
        Hoist common prefixes in alternations and simplify single-character differences into character classes.
        Example: "abc|abd|abe" -> "ab[cde]"
        """
        # Match top-level alternations not inside groups
        def split_alternatives(s):
            parts = []
            depth = 0
            last = 0
            for i, c in enumerate(s):
                if c == "(":
                    depth += 1
                elif c == ")":
                    depth -= 1
                elif c == "|" and depth == 0:
                    parts.append(s[last:i])
                    last = i + 1
            parts.append(s[last:])
            return part
          
        # Only apply if top-level alternations exist
        if "|" not in regex:
            return regex

        alternatives = split_alternatives(regex)
        if len(alternatives) <= 1:
            return regex

        # Find longest common prefix
        prefix = alternatives[0]
        for alt in alternatives[1:]:
            i = 0
            while i < len(prefix) and i < len(alt) and prefix[i] == alt[i]:
                i += 1
            prefix = prefix[:i]

        # If prefix exists, hoist it
        if prefix:
            suffixes = [alt[len(prefix):] for alt in alternatives]
            # Try to convert single-character differences to character class
            if all(len(s) == 1 for s in suffixes):
                char_class = "[" + "".join(suffixes) + "]"
                return prefix + char_class
            else:
                # Otherwise, join suffixes with | again
                return prefix + "(?:" + "|".join(suffixes) + ")"

        return regex

    def escape_non_ascii(self, regex: str) -> str:
        """
        Escape all non-ASCII characters as Unicode code points.
        """
        def repl(match):
            return f"\\u{ord(match.group(0)):04X}"
        return re.sub(r"[^\x00-\x7F]", repl, regex)

def auto_generate_sample():
    pattern = regex_input.get("1.0", "end-1c").strip()
    sample = sample_input.get("1.0", "end-1c").strip()

    if not sample and pattern:
        generated = generate_sample_from_regex(pattern)
        sample_input.delete("1.0", "end")
        sample_input.insert("1.0", generated)

def _make_verbose(regex: str) -> str:
    """Turn a regex string into verbose mode formatting for readability."""
 
    parts = []
    indent = 0
 
    for ch in regex:
        if ch == "(":
            parts.append("\n" + "  " * indent + ch)
            indent += 1
        elif ch == ")":
            indent -= 1
            parts.append("\n" + "  " * indent + ch)
        elif ch == "|":
            parts.append("\n" + "  " * indent + ch)
        else:
            parts.append(ch)
         
    return "(?x)" + "".join(parts)

# ============================================================
# Core generation logic
# ============================================================

def detect_uniform_class(samples: List[str]) -> Optional[str]:
    """
    Detect if all samples belong to the same character class.
    Returns regex string if match, otherwise None.
    """

    if not samples:
        return None

    # Digits
    if all(s.isdigit() for s in samples):
        min_len = min(len(s) for s in samples)
        max_len = max(len(s) for s in samples)

        if min_len == max_len:
            return rf"\d{{{min_len}}}"
        return rf"\d{{{min_len},{max_len}}}"

    # Whitespace
    if all(s.isspace() for s in samples):
        min_len = min(len(s) for s in samples)
        max_len = max(len(s) for s in samples)
        if min_len == max_len:
            return rf"\s{{{min_len}}}"
        return rf"\s{{{min_len},{max_len}}}"
   
    # Word characters (letters, digits, underscore)
    if all(re.fullmatch(r"\w+", s) for s in samples):
        min_len = min(len(s) for s in samples)
        max_len = max(len(s) for s in samples)
        if min_len == max_len:
            return rf"\w{{{min_len}}}"
        return rf"\w{{{min_len},{max_len}}}"

    return None


# Helper function: detect repeated substrings 
def detect_repetition(s: str, min_repetitions: int = 2, min_sub_len: int = 1):
    """
    Detect repeated substrings in a string.
    
    Returns a tuple (regex_fragment, True) if the string is a repeated substring.
    Otherwise returns None.

    Example:
        "abcabc" -> ("(?:abc){2}", True)
        "aaaa" -> ("(?:a){4}", True)
        "xyz" -> None
    """

    n = len(s)
 
    for sub_len in range(min_sub_len, n // min_repetitions + 1):
        sub = s[:sub_len]
        count = n // sub_len

        if sub * count == s and count >= min_repetitions:
            return (f"(?:{re.escape(sub)}){{{count}}}", True)

    return None


# Simplified generate_regex function for testing
def generate_regex(test_cases: list[str], config) -> str:
    """
    Generate a regex pattern from test cases, applying transformations
    based on the configuration flags.

    Rules:
    1) Fast-path global detections (all digits; case-insensitive single unique; simple two-word; alpha+digit suffix)
    2) Per-case preprocessing:
       - if repetition conversion is enabled -> detect full-string repeated substrings -> convert to non-capturing {k}
       - otherwise keep literal
       - case-normalize literal fragments if case-insensitive
    3) Tokenize fragments: atomic regex fragments remain atomic; literals split to characters
    4) Build token trie and produce regex body (escaping only literal character tokens)
    5) Wrap with capturing / anchors and inline flags (flags at start)
    """

    if not test_cases:
        raise ValueError("No test cases provided")

     # Make a shallow copy and ensure strings
    cases = [str(s) for s in test_cases]

    # Inline flags
    # Build inline flags string (must be at very beginning of the final regex)
    flags_parts = []

    if getattr(config, "is_case_insensitive_matching", False):
        flags_parts.append("i")
    if getattr(config, "is_verbose_mode_enabled", False):
        flags_parts.append("x")
    
    flags = f"(?{''.join(flags_parts)})" if flags_parts else ""

    # Anchors
    prefix = "" if getattr(config, "is_start_anchor_disabled", False) else "^"
    suffix = "" if getattr(config, "is_end_anchor_disabled", False) else "$"
 
    # 1. Handle pure digits
 
    # a) All digits
    if getattr(config, "is_digit_converted", False):
        all_digits, min_len, max_len = _all_digits_fastpath(cases)
     
        if all_digits:
            body = rf"\d{{{min_len}}}" if min_len == max_len else rf"\d{{{min_len},{max_len}}}"
         
            if getattr(config, "is_capturing_group_enabled", False):
                body = f"({body})"
             
            return f"{flags}{prefix}{body}{suffix}"

    # b) Case-insensitive single unique
    if getattr(config, "is_case_insensitive_matching", False):
        lowered = [s.lower() for s in cases]
     
        if len(set(lowered)) == 1:         
            body = re.escape(lowered[0])
         
            if getattr(config, "is_capturing_group_enabled", False):
                body = f"({body})"
             
            return f"{flags}{prefix}{body}{suffix}"

    # c) Common two-word pattern
    if _common_two_word_pattern(cases):
        body = r"\w+\s\w+"
     
        if getattr(config, "is_capturing_group_enabled", False):
            body = f"({body})"
         
        return f"{flags}{prefix}{body}{suffix}" 


    # d) Alpha-prefix + fixed-digit-suffix
    ok_alpha_digit, digit_suffix_len = _alpha_prefix_digit_suffix_pattern(cases)
 
    if ok_alpha_digit:
        body = rf"\w+\d{{{digit_suffix_len}}}"
     
        if getattr(config, "is_capturing_group_enabled", False):
            body = f"({body})"
         
        return f"{flags}{prefix}{body}{suffix}"
     
    """
    if config.is_digit_conversion_enabled and all(s.isdigit() for s in test_cases):
        min_len = min(len(s) for s in test_cases)
        max_len = max(len(s) for s in test_cases)
     
        if min_len == max_len:
            body = rf"\d{{{min_len}}}"
        else:
            body = rf"\d{{{min_len},{max_len}}}"
        
        return f"^{body}$"
    """

    # 2. Per-case preprocessing (Handle repetitions)
    processed_tokens = []
    seen_fragments = set()
 
    for s in cases:
        frag_str = None
        frag_is_regex = False

        # Repetition detection
        if getattr(config, "is_repetition_converted", False):
            rep = detect_repetition(
                s,
                min_repetitions=getattr(config, "minimum_repetitions", 2),
                min_sub_len=getattr(config, "minimum_substring_length", 1)
            )
         
            if rep:
                frag_str, frag_is_regex = rep  # rep returns (fragment, True)
             
         # If not converted, treat as literal
        if frag_str is None:
            frag_str = s.lower() if getattr(config, "is_case_insensitive_matching", False) else s
            frag_is_regex = False

         # Tokenize: regex fragments stay atomic
        tokens = _tokenize_fragment(frag_str, frag_is_regex)

        # Avoid duplicates
        key = tuple(tokens)
        if key not in seen_fragments:
            seen_fragments.add(key)
            processed_tokens.append(tokens)

    #3 Build token trie 
        trie = Trie(processed_tokens)

    #4 Convert trie to regex body
    body = trie.to_regex(capturing=getattr(config, "is_capturing_group_enabled", False))

    # Fallback if trie returns empty
    if not body:
        unique = sorted(set(cases))
   
        alt = "|".join(
            re.escape(s.lower() if getattr(config, "is_case_insensitive_matching", False) else s)
            for s in unique
        )
        body = f"(?:{alt})" if len(unique) > 1 else alt
     
        if getattr(config, "is_capturing_group_enabled", False):
            body = f"({body})"

    #5 Compose final regex
    return f"{flags}{prefix}{body}{suffix}"

'''
def generate_regex(test_cases: List[str], config) -> str:
    """
    Generate a regex string from test_cases according to config.

    Ordering & main ideas:
      1) Fast-path global detections (all digits; case-insensitive single unique; simple two-word; alpha+digit suffix)
      2) Per-case preprocessing:
         - if repetition conversion is enabled -> detect full-string repeated substrings -> convert to non-capturing {k}
         - otherwise keep literal
         - case-normalize literal fragments if case-insensitive
      3) Tokenize fragments: atomic regex fragments remain atomic; literals split to characters
      4) Build token trie and produce regex body (escaping only literal character tokens)
      5) Wrap with capturing / anchors and inline flags (flags at start)
    """

    if not test_cases:
        raise ValueError("No test cases provided")

    # Make a shallow copy and ensure strings
    cases = [str(s) for s in test_cases]


    # Build inline flags string (must be at very beginning of the final regex).
    flags_parts = []

    if getattr(config, "is_case_insensitive_matching", False):
        flags_parts.append("i")
    if getattr(config, "is_verbose_mode_enabled", False):
        flags_parts.append("x")
     
    flags = f"(?{''.join(flags_parts)})" if flags_parts else ""

    # ANCHOR STRINGS (these will follow the inline flags)
    prefix = "" if getattr(config, "is_start_anchor_disabled", False) else "^"
    suffix = "" if getattr(config, "is_end_anchor_disabled", False) else "$"

    # 1) Global Fast-paths 

    # a) ALL DIGITS: produce simple \d{min,max} if digit conversion is enabled
    if getattr(config, "is_digit_converted", False):
    all_digits, min_len, max_len = _all_digits_fastpath(cases)
    if all_digits:
        if min_len == max_len:
            body = rf"\d{{{min_len}}}"
        else:
            body = rf"\d{{{min_len},{max_len}}}"
        if getattr(config, "is_capturing_group_enabled", False):
            body = f"({body})"
        return f"{flags}{prefix}{body}{suffix}"
        
    """
    if getattr(config, "is_digit_converted", False):
        all_digits, min_len, max_len = _all_digits_fastpath(cases)
        if all_digits:
            if min_len == max_len:
                body = rf"\d{{{min_len}}}"
            else:
                body = rf"\d{{{min_len},{max_len}}}"
            # respect capturing flag (wrap if capturing)
            if getattr(config, "is_capturing_group_enabled", False):
                body = f"({body})"
            return f"{flags}{prefix}{body}{suffix}"
    """
        
    # b) Case-insensitive SINGLE UNIQUE pattern: if case-insensitive requested and all lower() are identical
    if getattr(config, "is_case_insensitive_matching", False):
        lowered = [s.lower() for s in cases]
        if len(set(lowered)) == 1:
            lit = lowered[0]
            body = re.escape(lit)
            if getattr(config, "is_capturing_group_enabled", False):
                body = f"({body})"
            return f"{flags}{prefix}{body}{suffix}"
         
    # c) Common two-word pattern (e.g., "Hello World", "Hi There", "Good Day")
    if _common_two_word_pattern(cases):
        # prefer \w+\s\w+
        body = r"\w+\s\w+"
        if getattr(config, "is_capturing_group_enabled", False):
            body = f"({body})"
        return f"{flags}{prefix}{body}{suffix}"

    # d) Alpha-prefix + fixed-digit-suffix pattern (User123, Admin456, Guest789 -> \w+\d{3})
    ok_alpha_digit, digit_suffix_len = _alpha_prefix_digit_suffix_pattern(cases)

    if ok_alpha_digit:
        body = rf"\w+\d{{{digit_suffix_len}}}"
        if getattr(config, "is_capturing_group_enabled", False):
            body = f"({body})"
        return f"{flags}{prefix}{body}{suffix}"

    # 2) Per-case preprocessing (repetitions & case-normalization) 
    processed_tokens = []  # list of token lists for Trie
    seen_fragments = set()  # to avoid duplicate inserts if desired

    for s in cases:
        frag_str = None
        frag_is_regex = False

        if getattr(config, "is_repetition_converted", False):
            rep = detect_repetition(s)
            unit, count = rep
            if count > 1:
                frag_str = f"(?:{re.escape(unit)}){{{count}}}"
                frag_is_regex = True
            else:
                frag_str = s.lower() if getattr(config, "is_case_insensitive_matching", False) else s
                frag_is_regex = False
        else:
            frag_str = s.lower() if getattr(config, "is_case_insensitive_matching", False) else s
            frag_is_regex = False

        """
        # Try repetition detection (only if enabled)
        if getattr(config, "is_repetition_converted", False):
            rep = detect_repetition(s,
                                     min_repetitions=getattr(config, "minimum_repetitions", 2),
                                     min_sub_len=getattr(config, "minimum_substring_length", 1))
            if rep:
                frag_str, frag_is_regex = rep  # rep returns (frag, True)
        """"

        # If not converted to repetition, treat as literal
        if frag_str is None:
            # case normalization for literal fragments
            if getattr(config, "is_case_insensitive_matching", False):
                frag_str = s.lower()
            else:
                frag_str = s
            frag_is_regex = False

        # Tokenize — regex fragments are single atomic tokens (sentinel-prefixed)
        tokens = _tokenize_fragment(frag_str, frag_is_regex)

        # Keep deterministic ordering and avoid duplicates
        key = tuple(tokens)

        if key not in seen_fragments:
            seen_fragments.add(key)
            processed_tokens.append(tokens)

    # 3) Build token trie 
    trie = Trie(processed_tokens)
 
    # 4) Convert trie to regex body  
    body = trie.to_regex(capturing=getattr(config, "is_capturing_group_enabled", False))

    # If the output is empty (shouldn't happen), fallback to alternation of escaped literals
    if not body:
        unique = sorted(set(cases))
        alt = "|".join(re.escape(s.lower() if getattr(config, "is_case_insensitive_matching", False) else s) for s in unique)
        body = f"(?:{alt})" if len(unique) > 1 else alt

        if getattr(config, "is_capturing_group_enabled", False):
            body = f"({body})"

    # 5) Compose final pattern: flags must appear at position 0 
    final = f"{flags}{prefix}{body}{suffix}"
 
    return final
'''

def generate_regex_safe(test_cases, config: RegExpConfig) -> str:
    """
    A simplified safe regex generator.
    - Handles case-insensitive inputs without freezing.
    - Applies anchors, verbose mode, and grouping.
    """

    if not test_cases:
        return ""

    # Case-insensitive mode → lowercase normalization
    if config.is_case_insensitive_matching:
        lowered = [t.lower() for t in test_cases]
        unique = sorted(set(lowered))
        pattern_body = "|".join(re.escape(t) for t in unique)
        flags = "(?i)"
    else:
        unique = sorted(set(test_cases))
        pattern_body = "|".join(re.escape(t) for t in unique)
        flags = ""

    # Capturing vs non-capturing groups
    if config.is_capturing_group_enabled:
        group = f"({pattern_body})"
    else:
        group = f"(?:{pattern_body})"

    # Anchors
    start_anchor = "" if config.is_start_anchor_disabled else "^"
    end_anchor = "" if config.is_end_anchor_disabled else "$"

    # Verbose mode
    if config.is_verbose_mode_enabled:
        pattern = (
            f"{flags}{start_anchor}\n"
            f"    {group}\n"
            f"{end_anchor}"
        )
    else:
        pattern = f"{flags}{start_anchor}{group}{end_anchor}"

    return pattern

def to_class_template(s):
    """Convert string s to a compressed class pattern."""
    if not s:
        return ""

    result = []
    prev_class = None
    count = 0

    def char_class(c):
        if c.isdigit():
            return r"\d"
        elif c.isalpha() or c == "_":
            return r"\w"
        elif c.isspace():
            return r"\s"
        else:
            return re.escape(c)

    for c in s:
        cls = char_class(c)
        if cls == prev_class:
            count += 1
        else:
            if prev_class is not None:
                if count > 1:
                    result.append(prev_class + "+")
                else:
                    result.append(prev_class)
            prev_class = cls
            count = 1

    # Append the last class
    if prev_class is not None:
        if count > 1:
            result.append(prev_class + "+")
        else:
            result.append(prev_class)

    return "".join(result)

# ============================================================
# Simple test when run directly
# ============================================================
if __name__ == "__main__":
    # Simple test when run directly
    builder = (
        RegExpBuilder.from_test_cases(["apple", "Apple", "APPLE"])
        .with_case_insensitive_matching()
        .with_capturing_groups()
        .with_verbose_mode()
    )

    regex = builder.build()
    print("Generated regex:\n", regex)

    test = re.compile(regex, re.VERBOSE)
    for word in ["apple", "APPLE", "ApPlE", "banana"]:
        print(word, "→", bool(test.match(word)))
