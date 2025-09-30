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


def generate_regex(samples: List[str], config: Optional[RegExpConfig] = None) -> str:
    """
    Generate example matching text for the given regex pattern.
    If generation fails, returns an empty string.
    """
    if not test_cases:
        raise ValueError("No test cases provided")

    cases = [str(s) for s in test_cases]

    # Step 1: Check for simple fast-paths first
    fast_path_result = _check_fast_paths(cases, config)
    if fast_path_result:
        return fast_path_result

    # Step 2: Process cases for advanced patterns (repetitions, Trie)
    pass

    # Step 3: Build Trie and generate the regex body
    try:

    except Exception:
        # Fallback to simple alternation if Trie fails


    # Step 4: Apply flags and anchors
    return _apply_flags_and_anchors(body, config)
 

    pass


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
        """
        Main method that converts the stored test cases and configuration
        into a final regex string.
        """

        # Step 1: Build raw regex from Trie
        trie = Trie()
        trie.build_from_list(self.test_cases)
        regex = trie.to_regex()

        # Step 2: Apply character class conversions
        regex = self.apply_character_conversions(regex)

        # Step 3: Apply repetition detection
        if self.config.convert_repetitions:
            regex = self.apply_repetitions(regex)

        # Step 4: Handle anchors
        if not self.config.start_anchor:
            regex = regex.lstrip("^")
        if not self.config.end_anchor:
            regex = regex.rstrip("$")

        # Step 5: Escape non-ASCII characters if required
        if self.config.escape_non_ascii:
            regex = self.escape_non_ascii(regex)

        # Step 6: Return final regex
        if self.config.case_insensitive:
            regex = "(?i)" + regex  # Python inline flag for case-insensitive
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

      
        
        def repl(match):
            char = match.group(1)
            count = len(match.group(0))
            if count >= min_rep and len(char) >= min_len:
                return f"{char}{{{count}}}"
            return match.group(0)

        pattern = re.compile(r"(.)\1+")
        return pattern.sub(repl, regex)

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


# ============================================================
# Core generation logic
# ============================================================
 

def detect_repetition(s: str, minimum_repetitions: int = 2, minimum_substring_length: int = 1) -> str:
    """
    Detect if the string `s` is made of repetitions of a smaller substring.
    Returns a regex that represents the repetition, or the original string
    if no repetition is found.
    """

   pass


def generate_regex(test_cases, config):
    """
    Generate a regex string from test_cases using fast-paths for uniform classes
    (digits, words, whitespace), then a safe fallback. Respects config flags.

    Parameters
    - test_cases: list[str]
    - config: object with attributes (bools) matching the RegExpConfig names:
        is_digit_converted,
        is_word_converted,
        is_space_converted,
        is_repetition_converted,
        is_capturing_group_enabled,
        is_start_anchor_disabled,
        is_end_anchor_disabled,
        is_case_insensitive_matching,
        is_verbose_mode_enabled
    """
    
   pass


def generate_regex_safe(test_cases, config: RegExpConfig) -> str:
    """
    A simplified safe regex generator.
    - Handles case-insensitive inputs without freezing.
    - Applies anchors, verbose mode, and grouping.
    """

    pass


# ============================================================
# Simple test when run directly
# ============================================================
if __name__ == "__main__":
    '''
    # Simple test when run directly
    builder = RegExpBuilder.from_test_cases(["123", "45", "7"])
    builder.with_conversion_of_digits().with_case_insensitive_matching()
    pattern = builder.build()
    print(pattern)
    '''
    pass

