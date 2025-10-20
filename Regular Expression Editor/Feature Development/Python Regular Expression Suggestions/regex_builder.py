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
from typing import List, Optional, Union

 
# ---------------- RegExpConfig ----------------

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
        self.minimum_repetitions = 1
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


class RegExpBuilder:
    """
    Builds regexes from test cases using the configured settings.
    """
     
    MISSING_TEST_CASES_MESSAGE = "No test cases have been provided for regular expression generation"
    MINIMUM_REPETITIONS_MESSAGE = "Quantity of minimum repetitions must be greater than zero"
    MINIMUM_SUBSTRING_LENGTH_MESSAGE = "Minimum substring length must be greater than zero"

    def __init__(self, test_cases: List[str]):
       if not test_cases:
           raise ValueError(self.MISSING_TEST_CASES_MESSAGE)
       self.test_cases: List[str] = test_cases
       self.config: RegExpConfig = RegExpConfig()

    # -------------------------------
    # Conversion methods
    # -------------------------------
    def with_conversion_of_digits(self):
        self.config.convert_digits = True
        return self

    def with_conversion_of_non_digits(self):
        self.config.convert_non_digits = True
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
    def with_conversion_of_repetitions(self):
        self.config.convert_repetitions = True
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

    def with_verbose_mode(self):
        self.config.verbose = True
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


def detect_repetition(strings: list[str]) -> str | None:
    """
    Detect if all strings are repetitions of a smaller substring.
    Example: ["abcabc", "xyzxyz"] -> "^(?:abc){2}$" or "^(?:xyz){2}$"
    """
    reps = []
    for s in strings:
        for size in range(1, len(s) // 2 + 1):
            if len(s) % size == 0:
                unit = s[:size]
                if unit * (len(s) // size) == s:
                    reps.append((unit, len(s) // size))
                    break
        else:
            return None  # no repetition for this string

    # Check if all repetitions share the same unit and count
    units = {u for u, _ in reps}
    counts = {c for _, c in reps}
    if len(units) == 1 and len(counts) == 1:
        unit, count = reps[0]
        return f"^(?:{re.escape(unit)}){{{count}}}$"

    return None

'''
def detect_repetition(strings: list[str]) -> str | None:
    """
    Detect if all strings are repetitions of a smaller substring.
    Example: ["abcabc", "xyzxyz"] -> "^(?:abc){2}$" or "^(?:xyz){2}$"
    """
    reps = []
    for s in strings:
        for size in range(1, len(s) // 2 + 1):
            if len(s) % size == 0:
                unit = s[:size]
                if unit * (len(s) // size) == s:
                    reps.append((unit, len(s) // size))
                    break
        else:
            return None  # no repetition for this string

    # Check if all repetitions share the same unit and count
    units = {u for u, _ in reps}
    counts = {c for _, c in reps}
    if len(units) == 1 and len(counts) == 1:
        unit, count = reps[0]
        return f"^(?:{re.escape(unit)}){{{count}}}$"

    return None
'''


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


def generate_regex(
    samples: list[str],
    use_repetitions: bool = False,
    use_capturing: bool = False,
    verbose: bool = False,
    anchors: bool = True,
    case_insensitive: bool = False,
    char_class: str | None = None,
) -> str:
    """
    Generates a regex pattern from a list of test_cases using the given configuration.
    """

    if not samples:
        return ""
 
    # Handle case-insensitivity early
    if case_insensitive:
        samples = [s.lower() for s in samples]

    # 1. Check for uniform "digits only" case
    if char_class == "digits" and all(s.isdigit() for s in samples):
        lengths = sorted(len(s) for s in samples)
        if lengths:
            min_len, max_len = min(lengths), max(lengths)
            if min_len == max_len:
                pattern = rf"\d{{{min_len}}}"
            else:
                pattern = rf"\d{{{min_len},{max_len}}}"
            return f"^{pattern}$" if anchors else pattern

    # 2. Check for repetition patterns
    if use_repetitions:
        rep = detect_repetition(samples)
        if rep:
            return rep

    # 3. Try char_class generalization for words/whitespace/etc.
    if char_class == "words" and all(s.isalpha() for s in samples):
        lengths = sorted(len(s) for s in samples)
        min_len, max_len = min(lengths), max(lengths)
        if min_len == max_len:
            pattern = rf"\w{{{min_len}}}"
        else:
            pattern = rf"\w{{{min_len},{max_len}}}"
        return f"^{pattern}$" if anchors else pattern

 
    else:
        # Detect simple repeated substrings first
        detected = []
        for s in test_cases:
            rep = detect_repetition(s,
                                    min_reps=config.minimum_repetitions,
                                    min_len=config.minimum_substring_length)
            if rep:
                detected.append(rep)
            else:
                detected.append(re.escape(s))

        if len(set(detected)) == 1:
            body = detected[0]
        else:
            trie = Trie(test_cases)
            body = trie.to_regex()

        # Detect repeated substrings
        if config.is_repetition_converted:
            repetitions = []
            for s in test_cases:
                rep = detect_repetition(s, min_reps=config.minimum_repetitions,
                                        min_len=config.minimum_substring_length)
                if rep:
                    repetitions.append(rep)

            # If all test cases share the same repetition pattern, replace body
            if repetitions and len(set(repetitions)) == 1:
                body = repetitions[0]

    # Apply capturing groups if enabled
    if config.is_capturing_group_enabled and not body.startswith("("):
        body = f"({body})"

    # Prefix/suffix anchors
    prefix = "" if config.is_start_anchor_disabled else "^"
    suffix = "" if config.is_end_anchor_disabled else "$"
 
    # Global flags
    flags = ""
    if config.is_case_insensitive_matching:
        flags += "(?i)"
    if config.is_verbose_mode_enabled:
        flags += "(?x)"

    regex = f"{flags}{prefix}{body}{suffix}"
    return regex


'''
def generate_regex(
    samples: list[str],
    use_repetitions: bool = False,
    use_capturing: bool = False,
    verbose: bool = False,
    anchors: bool = True,
    case_insensitive: bool = False,
    char_class: str | None = None,
) -> str:
    """
    Generate a regex pattern from sample strings with configurable options.
    """

    if not samples:
        return ""

    # Handle case-insensitivity early
    if case_insensitive:
        samples = [s.lower() for s in samples]

    # 1. Check for uniform "digits only" case
    if char_class == "digits" and all(s.isdigit() for s in samples):
        lengths = sorted(len(s) for s in samples)
        if lengths:
            min_len, max_len = min(lengths), max(lengths)
            if min_len == max_len:
                pattern = rf"\d{{{min_len}}}"
            else:
                pattern = rf"\d{{{min_len},{max_len}}}"
            return f"^{pattern}$" if anchors else pattern

    # 2. Check for repetition patterns
    if use_repetitions:
        rep = detect_repetition(samples)
        if rep:
            return rep

    # 3. Try char_class generalization for words/whitespace/etc.
    if char_class == "words" and all(s.isalpha() for s in samples):
        lengths = sorted(len(s) for s in samples)
        min_len, max_len = min(lengths), max(lengths)
        if min_len == max_len:
            pattern = rf"\w{{{min_len}}}"
        else:
            pattern = rf"\w{{{min_len},{max_len}}}"
        return f"^{pattern}$" if anchors else pattern

    if char_class == "whitespace" and all(s.isspace() for s in samples):
        lengths = sorted(len(s) for s in samples)
        min_len, max_len = min(lengths), max(lengths)
        if min_len == max_len:
            pattern = rf"\s{{{min_len}}}"
        else:
            pattern = rf"\s{{{min_len},{max_len}}}"
        return f"^{pattern}$" if anchors else pattern
     
    # 4. Build regex with trie fallback
    trie = Trie()
    for s in samples:
        trie.insert(s)

    body = trie.to_regex(capturing=use_capturing, verbose=verbose)

    # 5. Wrap with anchors
    if anchors:
        body = f"^{body}$"

    # 6. Case-insensitive flag
    if case_insensitive:
        body = f"(?i){body}"

    # 7. Verbose mode flag
    if verbose:
        body = f"(?x){body}"

    return body
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

