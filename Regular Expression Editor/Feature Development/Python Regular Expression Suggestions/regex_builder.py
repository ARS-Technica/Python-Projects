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

class RegexConfig:
    def __init__(self, case_insensitive=False, digits_only=False, verbose=False, capturing=False):
        self.case_insensitive = case_insensitive
        self.digits_only = digits_only
        self.verbose = verbose
        self.capturing = capturing

 
    # ---------- Helpers ---------
       def _all_digits_fastpath(cases: List[str], config) -> Optional[str]:
           """
           If digit conversion is enabled and *all* cases are digits, return the final
           anchored/flagged regex immediately (e.g. ^\d{1,3}$). Otherwise return None.
           """
           if not _digits_flag_enabled(config):
               return None
            
           # tolerate incidental whitespace
           stripped = [s.strip() for s in cases]
        
           if not stripped or not all(s.isdigit() for s in stripped):
               return None
            
           lengths = [len(s) for s in stripped]
           min_len, max_len = min(lengths), max(lengths)
           body = rf"\d{{{min_len}}}" if min_len == max_len else rf"\d{{{min_len},{max_len}}}"
        
           if getattr(config, "is_capturing_group_enabled", False):
               body = f"({body})"
            
           flags = _flags_prefix(config)
           prefix, suffix = _anchors(config)
        
           return f"{flags}{prefix}{body}{suffix}"

       def _anchors(config) -> Tuple[str, str]:
           prefix = "" if getattr(config, "is_start_anchor_disabled", False) else "^"
           suffix = "" if getattr(config, "is_end_anchor_disabled", False) else "$"
        
           return prefix, suffix
 
       def _build_trie_regex(processed_tokens: List[List[str]], config) -> str:
           """Build regex body from token trie or fallback to alternation."""
           if not processed_tokens:
               return ""
           try:
               trie = Trie(processed_tokens)  # assumes Trie accepts list-of-token-lists
               try:
                   return trie.to_regex(
                       capturing=getattr(config, "is_capturing_group_enabled", False),
                       verbose=getattr(config, "is_verbose_mode_enabled", False)
                   )
               except TypeError:
                   return trie.to_regex(getattr(config, "is_capturing_group_enabled", False))
           except Exception:
               alts = [_join_tokens_to_literal(seq) for seq in processed_tokens]
               return alts[0] if len(alts) == 1 else f"(?:{'|'.join(alts)})"
   
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

       def _detect_repetition(cases: List[str], config) -> (List[str], List[str]):
           """Detect repeated substrings and return atomic regex fragments and remaining strings."""
           repeated = []
           remaining = []
       
           for s in cases:
               if getattr(config, "is_repetition_converted", False):
                   rep = detect_repetition(
                       s,
                       min_repetitions=getattr(config, "minimum_repetitions", 2),
                       min_sub_len=getattr(config, "minimum_substring_length", 1)
                   )
                
                   if rep:
                       repeated.append(rep if isinstance(rep, str) else rep[0])
                       continue
                    
               remaining.append(s)
            
           return repeated, remaining

       def _global_fast_paths(cases: List[str], config) -> Optional[str]:
           """Other simple fast-paths: case-insensitive single unique, two-word, alpha+digit suffix."""
           # case-insensitive single unique
           if getattr(config, "is_case_insensitive_matching", False):
               lowered = [s.lower() for s in cases]
            
               if len(set(lowered)) == 1:
                   body = re.escape(lowered[0])
                
                   if getattr(config, "is_capturing_group_enabled", False):
                       body = f"({body})"
                    
                   flags = _flags_prefix(config)
                   prefix, suffix = _anchors(config)
                   return f"{flags}{prefix}{body}{suffix}"
       
           # two-word pattern (prefer \w+\s\w+)
           if cases and all(re.fullmatch(r"\w+\s\w+", s) for s in cases):
               body = r"\w+\s\w+"
            
               if getattr(config, "is_capturing_group_enabled", False):
                   body = f"({body})"
                
               flags = _flags_prefix(config)
               prefix, suffix = _anchors(config)
               return f"{flags}{prefix}{body}{suffix}"
       
           # alpha-prefix + fixed-digit-suffix (e.g., User123 / Admin456)
           lengths = []
        
           for s in cases:
               m = re.fullmatch(r"(\w+?)(\d+)$", s)
               if not m:
                   break
                
               lengths.append(len(m.group(2)))
            
           else:  # no break -> all matched
               if len(set(lengths)) == 1:
                   body = rf"\w+\d{{{lengths[0]}}}"
                
                   if getattr(config, "is_capturing_group_enabled", False):
                       body = f"({body})"
                    
                   flags = _flags_prefix(config)
                   prefix, suffix = _anchors(config)
                   return f"{flags}{prefix}{body}{suffix}"
       
           return None

       def _is_regex_fragment_token(s: str) -> bool:
           """Rudimentary check: treat strings containing backslash, parentheses, braces,
           or '?:' as already-formed regex fragments."""
        
           # This is conservative: if the string contains any of these characters, we will
           # treat it as a fragment token (atomic) and not escape/split it.
           return any(ch in s for ch in ("\\", "(", ")", "{", "}", "[", "]", "?"))

       def _join_tokens_to_literal(tokens: List[str]) -> str:
           """Join a token list into a regex-safe literal string."""
           return "".join(re.escape(t) for t in tokens)

       def _node_to_regex(self, node, capturing: bool = False, verbose: bool = False):
           """
           If all strings are digit-only, return a \d{min,max} pattern.
           Otherwise return None.
           """
           if node.is_leaf:
               return re.escape(node.char)
   
           parts = []
   
           for child in node.children.values():
               parts.append(self._node_to_regex(child, capturing, verbose))
        
           # Try digit compression if this node leads only to digit leaves
           if all(c.is_leaf for c in node.children.values()):
               digit_strings = ["".join(self._collect_string(c)) for c in node.children.values()]
               compressed = compress_digit_alternation(digit_strings)
   
               if compressed:
                   return compressed
   
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
   
       def _tokenize_fragment(fragment: str, is_regex: bool) -> List[str]:
           """Tokenize a fragment into a list of tokens. Atomic regex fragments stay intact."""
        
           if is_regex:
               return [fragment]
           else:
               return list(fragment)  # each char as token


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

            else:
                # fallback manual alternation build
                alts = [join_tokens_to_literal(seq) for seq in processed_token_seqs]
                body = alts[0] if len(alts) == 1 else f"(?:{'|'.join(alts)})"

             except Exception:
              # As last resort make a safe alternation of escaped strings
              alts = []
              for tok_seq in processed_token_seqs:
                  # join tokens but escape literal tokens (is_atomic_token keeps regex fragments and \d, \w)
                  alts.append(join_tokens_to_literal(tok_seq))
              body = alts[0] if len(alts) == 1 else f"(?:{'|'.join(alts)})"

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

def compress_digit_alternation(regex: str) -> str | None:
    """
    Compress an alternation of pure digits into \d{min,max}.
    Example: (?:123|45|7) -> \d{1,3}
    """ 
    
    m = re.fullmatch(r"\(\?:([0-9|]+)\)", regex)
 
    if not m:
        return None
             
    parts = regex[3:-1].split("|")  # strip (?: ... )
 
    if all(p.isdigit() for p in parts):
        lengths = [len(p) for p in parts]
        return rf"\d{{{min(lengths)},{max(lengths)}}}"
    
   return None

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

def generate_regex(test_cases: List[str], config) -> str:
    """
    Generate a regex string from test_cases according to config.

    Strategy:
      0) FAST-PATH: all-digits -> \d{min,max}  (run before any normalization)
      1) Other global fast-paths (case-insensitive unique, two-word, alpha+digit suffix)
      2) Detect repeated substrings first (convert to atomic regex fragments)
      3) Tokenize fragments and build token trie
      4) Wrap with capturing / anchors / inline flags
    """
    if not test_cases:
        raise ValueError("No test cases provided")

    # Normalize input type
    cases = [str(s).strip() for s in test_cases]

    # Inline flags
    flags_parts = []
    if getattr(config, "is_case_insensitive_matching", False):
        flags_parts.append("i")
    if getattr(config, "is_verbose_mode_enabled", False):
        flags_parts.append("x")
    flags = f"(?{''.join(flags_parts)})" if flags_parts else ""

    # Anchors
    prefix = "" if getattr(config, "is_start_anchor_disabled", False) else "^"
    suffix = "" if getattr(config, "is_end_anchor_disabled", False) else "$"
 
    # 0) All-digits fast-path
    '''
    if getattr(config, "is_digit_converted", False) and all(s.isdigit() for s in cases):
        lengths = [len(s) for s in cases]
        min_len, max_len = min(lengths), max(lengths)

        body = rf"\d{{{min_len}}}" if min_len == max_len else rf"\d{{{min_len},{max_len}}}"
     
        if getattr(config, "is_capturing_group_enabled", False):
            body = f"({body})"
        
        return f"{flags}{prefix}{body}{suffix}
    '''
    digits_regex = _all_digits_fastpath(cases, config)

    if digits_regex:
        return digits_regex
        
    # 1) Global fast-paths (run BEFORE trie/tokenization) 
    '''
    # a) Case-insensitive single unique
    if getattr(config, "is_case_insensitive_matching", False):
        lowered = [s.lower() for s in cases]
     
        if len(set(lowered)) == 1:
            body = re.escape(lowered[0])
            if getattr(config, "is_capturing_group_enabled", False):
                body = f"({body})"
            
            return f"{flags}{prefix}{body}{suffix}"

    # b) Common two-word pattern
    if all(re.fullmatch(r"\w+\s\w+", s) for s in cases):
        body = r"\w+\s\w+"
     
        if getattr(config, "is_capturing_group_enabled", False):
            body = f"({body})"
         
        return f"{flags}{prefix}{body}{suffix}"
     
    # c) Alpha-prefix + fixed-digit-suffix pattern (User123, Admin456, Guest789 -> \w+\d{3})
    def _alpha_prefix_digit_suffix_pattern(cases_list):
        lengths = []
     
        for s in cases_list:
            m = re.fullmatch(r"(\w+?)(\d+)$", s)
            if not m:
                return False, 0
            lengths.append(len(m.group(2)))
         
        if len(set(lengths)) == 1:
            return True, lengths[0]
         
        return False, 0

    ok_alpha_digit, digit_suffix_len = _alpha_prefix_digit_suffix_pattern(cases)
 
    if ok_alpha_digit:
        body = rf"\w+\d{{{digit_suffix_len}}}"
     
        if getattr(config, "is_capturing_group_enabled", False):
            body = f"({body})"
         
        return f"{flags}{prefix}{body}{suffix}"
    '''
    fast_regex = _global_fast_paths(cases, config)
    
    if fast_regex:
        return fast_regex

    # 2. Detect repeated substrings Per-case preprocessing (Handle repetitions)
    # This ensures repeated substrings like "abcabc" become (?:abc){2}
    '''
    processed_tokens = []   # list of token lists
    seen_fragments = set()

    for s in cases:
        frag_str = None
        frag_is_regex = False
            
        # repetition detection (if enabled)
        if getattr(config, "is_repetition_converted", False):
            rep = detect_repetition(
                s,
                min_repetitions=getattr(config, "minimum_repetitions", 2),
                min_sub_len=getattr(config, "minimum_substring_length", 1),
            )
            if rep:
                # ensure repetition is atomic
                frag_str, frag_is_regex = (rep, True) if not isinstance(rep, tuple) else rep

        # If no repetition detected, treat as literal (case-normalize)
        if frag_str is None:
            frag_str = s.lower() if getattr(config, "is_case_insensitive_matching", False) else s
            frag_is_regex = False
     
        # Tokenize fragment; atomic regex fragments become single-token lists
        tokens = _tokenize_fragment(frag_str, frag_is_regex)

        if frag_is_regex:
            tokens = [frag_str]  # keep repeated substrings atomic

        # Deduplicate token-sequences while preserving order
        key = tuple(tokens)
     
        if key not in seen_fragments:
            seen_fragments.add(key)
            processed_tokens.append(tokens)
    '''
    repeated, remaining = _detect_repetition(cases, config)

    # 3) Build token trie or fallback
    '''
    body = ""
 
    try:
        trie = Trie(processed_tokens)
        try:
            body = trie.to_regex(
                capturing=getattr(config, "is_capturing_group_enabled", False),
                verbose=getattr(config, "is_verbose_mode_enabled", False),
            )
         
        except TypeError:
            body = trie.to_regex(getattr(config, "is_capturing_group_enabled", False))
         
    except Exception:
        # fallback: safe alternation
        alts = [_join_tokens_to_literal(seq) for seq in processed_tokens]
        body = alts[0] if len(alts) == 1 else f"(?:{'|'.join(alts)})"
    '''

    processed_tokens = [_tokenize_fragment(s, False) for s in remaining]
    trie_body = _build_trie_regex(processed_tokens, config) if remaining else ""
        
    # Step 4: Safety fallback
    # Combine repeated fragments and trie output
    '''
    # Fallback if trie returns empty
    # Triggers in Body is empty
 
    if not body:
        unique = sorted(set(cases))
        alt = "|".join(re.escape(t.lower() if getattr(config, "is_case_insensitive_matching", False) else t) for t in unique)
        body = alt if len(unique) == 1 else f"(?:{alt})"
     
        if getattr(config, "is_capturing_group_enabled", False):
            body = f"({body})"
    '''

    all_bodies = repeated + ([trie_body] if trie_body else [])

    if not all_bodies:
        body = ""
    elif len(all_bodies) == 1:
        body = all_bodies[0]
    else:
        body = f"(?:{'|'.join(all_bodies)})"   

    '''
    # Step 5: Compose final regex
    return f"{flags}{prefix}{body}{suffix}"
    '''

    # Step 5: Inline flags, anchors, capturing
    flags_parts = []
    
    if getattr(config, "is_case_insensitive_matching", False):
        flags_parts.append("i")
    if getattr(config, "is_verbose_mode_enabled", False):
        flags_parts.append("x")
    
    flags = f"(?{''.join(flags_parts)})" if flags_parts else ""

    prefix = "" if getattr(config, "is_start_anchor_disabled", False) else "^"
    suffix = "" if getattr(config, "is_end_anchor_disabled", False) else "$"

    if getattr(config, "is_capturing_group_enabled", False) and not body.startswith("("):
        body = f"({body})"

    return f"{flags}{prefix}{body}{suffix}"    

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
