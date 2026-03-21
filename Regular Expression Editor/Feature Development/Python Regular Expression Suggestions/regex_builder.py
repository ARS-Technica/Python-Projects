'''
Next issue: When I type in the text
"abcabc
xyzxyz"
the program returns "^(?abcabc|xyzxyz)"
and
"(?:(?:abc)2∣(?:xyz)2" and "( ?:(?:abc)2∣(?:xyz)2"
It should return "^(?:abc){2}"or"(?:xyz)2" or " ( ?:xyz)2"
'''

from collections import defaultdict
from pathlib import Path
import re
import threading
from trie import Trie
from typing import List, Optional, Union


class RegExpConfig:
    """
    Holds all configuration options for regex generation.
    Mirrors the settings from the Rust version of grex.
    """

    def __init__(
        self,
        use_repetitions: bool = True,
        use_capturing_groups: bool = False,
        verbose: bool = False,
        anchored: bool = True,
        case_insensitive: bool = False,
    ):
        self.use_repetitions = use_repetitions
        self.use_capturing_groups = use_capturing_groups
        self.verbose = verbose
        self.anchored = anchored
        self.case_insensitive = case_insensitive

        # Character conversions
        self.is_digit_converted = False
        self.is_non_digit_converted = False
        self.is_space_converted = False
        self.is_non_space_converted = False
        self.is_word_converted = False
        self.is_non_word_converted = False

        # Pattern optimizations
        self.is_repetition_converted = False
        # Default to 2 so detect_repetition only matches true repetitions (e.g. "abcabc")
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


def detect_repetition(s, min_repetitions=2, min_sub_len=1):
    """
    Detect repeated substrings and return regex fragment like (?:abc){2}.
    """
    n = len(s)
    for sub_len in range(min_sub_len, n // min_repetitions + 1):
        sub = s[:sub_len]
        count = n // sub_len
        if sub * count == s and count >= min_repetitions:
            # Escape only literal characters inside the repeated substring
            return f"(?:{re.escape(sub)}){{{count}}}"
    return None


def generate_regex(test_cases, config):
    """
    Generate a regex string from test cases according to the given configuration.

    The function detects common, simple patterns early (identical strings under
    case-insensitive mode, alpha+digits, words+whitespace, pure repetitions)
    and falls back to a Trie-based alternation for mixed inputs.
    """

    if not test_cases:
        return ""

    # Anchors and flags
    prefix = "" if config.is_start_anchor_disabled else "^"
    suffix = "" if config.is_end_anchor_disabled else "$"

    flags = ""
    processed_cases = test_cases
    if config.is_case_insensitive_matching:
        processed_cases = [s.lower() for s in test_cases]
        flags = "(?i)"

    # Fast path: if all examples collapse to the same string under normalization
    unique = sorted(set(processed_cases))
    if len(unique) == 1:
        body = re.escape(unique[0])
        if config.is_verbose_mode_enabled:
            flags = "(?x)" + flags
        return f"{flags}{prefix}{body}{suffix}"

    # Fast path: all digits and configured to compress digits
    if config.is_digit_converted and all(s.isdigit() for s in processed_cases):
        min_len = min(len(s) for s in processed_cases)
        max_len = max(len(s) for s in processed_cases)
        if min_len == max_len:
            body = rf"\d{{{min_len}}}"
        else:
            body = rf"\d{{{min_len},{max_len}}}"
        if config.is_verbose_mode_enabled:
            flags = "(?x)" + flags
        return f"{flags}{prefix}{body}{suffix}"

    # Step: detect repeated substrings early (only if enabled)
    repetition_patterns = []
    remaining_strings = []

    for s in processed_cases:
        if config.is_repetition_converted:
            rep = detect_repetition(s,
                                    min_repetitions=config.minimum_repetitions,
                                    min_sub_len=config.minimum_substring_length)
        else:
            rep = None

        if rep:
            repetition_patterns.append(rep)
        else:
            remaining_strings.append(s)

    # If everything was a repetition and we found at least one
    if repetition_patterns and not remaining_strings:
        # Try to generalize multiple repetition fragments into a single class-based
        # repeated pattern when they share the same sub-length and repetition count
        if len(repetition_patterns) > 1:
            parsed = []
            ok = True
            for p in repetition_patterns:
                mm = re.fullmatch(r"\(\?:([^)]*)\)\{(\d+)\}", p)
                if not mm:
                    ok = False
                    break
                sub, cnt = mm.group(1), int(mm.group(2))
                if not sub:
                    ok = False
                    break
                parsed.append((sub, cnt))

            if ok:
                counts = {cnt for (_, cnt) in parsed}
                sub_lens = {len(sub) for (sub, _) in parsed}
                if len(counts) == 1 and len(sub_lens) == 1:
                    cnt = counts.pop()
                    # If all repetition units are identical, return the exact repeated pattern
                    subs = [sub for (sub, _) in parsed]
                    unique_subs = list(dict.fromkeys(subs))
                    if len(unique_subs) == 1:
                        sub = unique_subs[0]
                        body = rf"(?:{re.escape(sub)}){{{cnt}}}"
                        if config.is_verbose_mode_enabled:
                            flags = "(?x)" + flags
                        return f"{flags}{prefix}{body}{suffix}"

                    # Otherwise, return alternation of the exact repeated fragments
                    body = f"(?:{'|'.join(rf'(?:{re.escape(sub)}){{{cnt}}}' for sub in unique_subs)})"
                    if config.is_verbose_mode_enabled:
                        flags = "(?x)" + flags
                    return f"{flags}{prefix}{body}{suffix}"

        # Fallback: return alternation of the repetition fragments
        body = repetition_patterns[0] if len(repetition_patterns) == 1 else f"(?:{'|'.join(repetition_patterns)})"
        if config.is_verbose_mode_enabled:
            flags = "(?x)" + flags
        return f"{flags}{prefix}{body}{suffix}"

    # Fast path: alpha + digits pattern (User123, Admin456 ...)
    m = [re.match(r"^([A-Za-z]+)(\d+)$", s) for s in processed_cases]
    if all(m):
        digit_lengths = [len(mi.group(2)) for mi in m]
        min_len, max_len = min(digit_lengths), max(digit_lengths)
        if min_len == max_len:
            digit_part = rf"\d{{{min_len}}}"
        else:
            digit_part = rf"\d{{{min_len},{max_len}}}"
        body = rf"\w+{digit_part}"
        if config.is_verbose_mode_enabled:
            flags = "(?x)" + flags
        return f"{flags}{prefix}{body}{suffix}"

    # Fast path: word + whitespace patterns (e.g. "Hello World")
    # Automatically detect if all strings match word+space pattern, regardless of checkbox settings
    token_lists = [s.split() for s in processed_cases]
    if all(all(re.fullmatch(r"\w+", tok) for tok in toks) for toks in token_lists):
        counts = set(len(toks) for toks in token_lists)
        if len(counts) == 1:
            k = counts.pop()
            if k == 1:
                # single-token case: only compress when word conversion explicitly enabled
                if config.is_word_converted:
                    body = r"\w+"
                else:
                    body = None
            elif k == 2:
                body = r"\w+\s+\w+"
            else:
                body = rf"\w+(?:\s+\w+){{{k-1}}}"

            if body is not None:
                if config.is_capturing_group_enabled:
                    body = f"({body})"
                else:
                    body = f"(?:{body})"

                if config.is_verbose_mode_enabled:
                    flags = "(?x)" + flags
                return f"{flags}{prefix}{body}{suffix}"

    # Step: handle remaining strings via Trie for optimal grouping
    trie_body = ""
    
    if remaining_strings:
        # If no conversion flags are set, prefer a literal alternation of the
        # remaining strings in the original input order — this avoids trie
        # factoring that produces compact but less readable forms.
        if not any([
            config.is_digit_converted,
            config.is_non_digit_converted,
            config.is_space_converted,
            config.is_non_space_converted,
            config.is_word_converted,
            config.is_non_word_converted,
            config.is_repetition_converted,
        ]):
            body = f"(?:{'|'.join(re.escape(s) for s in remaining_strings)})"
            if config.is_verbose_mode_enabled:
                flags = "(?x)" + flags
            return f"{flags}{prefix}{body}{suffix}"

        trie = Trie(remaining_strings)
        trie_body = trie.to_regex(capturing=config.is_capturing_group_enabled,
                                  verbose=config.is_verbose_mode_enabled)

    # Combine repeated-pattern results and trie output
    parts = []
    parts.extend(repetition_patterns)
    if trie_body:
        parts.append(trie_body)

    if not parts:
        # Fallback: nothing matched specially — build an alternation via Trie
        trie = Trie(processed_cases)
        body = trie.to_regex(capturing=config.is_capturing_group_enabled,
                             verbose=config.is_verbose_mode_enabled)
    elif len(parts) == 1:
        body = parts[0]
    else:
        body = f"(?:{'|'.join(parts)})"

    if config.is_verbose_mode_enabled:
        flags = "(?x)" + flags

    return f"{flags}{prefix}{body}{suffix}"


# -----------------------------
# Utilities: safety / candidates
# -----------------------------

def analyze_regex_for_backtracking(pattern: str) -> Optional[str]:
    """Return a brief warning message if the pattern looks risky for backtracking.

    This uses lightweight heuristics (not a full static analysis):
    - nested quantifiers like (.+)+ or (?:.*)+
    - standalone wildcard quantifiers like .* or .+
    - very large alternations (many "|" tokens)
    """
    # nested quantifiers (group with quantifier followed by another quantifier)
    if re.search(r"\([^)]*[+*?]\)\s*[+*?]", pattern):
        return "Nested quantifiers detected (e.g. (.+)+) — may catastrophically backtrack"
    if re.search(r"\.(\*|\+)", pattern):
        return "Wildcard quantifiers (.* or .+) can be unsafe"
    # many alternations
    alt_count = pattern.count("|")
    if alt_count > 20:
        return f"Large alternation ({alt_count} branches) — matching may be slow"
    return None


def safe_match(pattern: str, s: str, timeout: float = 0.05) -> bool:
    """Attempt to match the pattern against s with a timeout in seconds.

    Returns True/False if match completes within timeout, or raises TimeoutError.
    """
    result = {"match": False}

    def target():
        try:
            result["match"] = bool(re.search(pattern, s))
        except re.error:
            result["match"] = False

    t = threading.Thread(target=target)
    t.daemon = True
    t.start()
    t.join(timeout)
    if t.is_alive():
        raise TimeoutError("Regex matching timed out — possible catastrophic backtracking")
    return result["match"]


def generate_candidates(test_cases: List[str], config: RegExpConfig, generalization: str = "balanced", max_candidates: int = 5):
    """Return a ranked list of candidate regex dicts for the given test cases and config.

    Each candidate is a dict: {pattern, score, reason, matches, warning}
    """
    if not test_cases:
        return []

    processed_cases = [s.lower() for s in test_cases] if config.is_case_insensitive_matching else list(test_cases)

    candidates = []

    # Conservative: literal alternation (preserve input order)
    literal = f"(?:{'|'.join(re.escape(s) for s in processed_cases)})"
    candidates.append({"pattern": literal, "score": 0.95, "reason": "literal alternation"})

    # Digits
    if all(s.isdigit() for s in processed_cases):
        min_len = min(len(s) for s in processed_cases)
        max_len = max(len(s) for s in processed_cases)
        if min_len == max_len:
            body = rf"\d{{{min_len}}}"
        else:
            body = rf"\d{{{min_len},{max_len}}}"
        candidates.append({"pattern": body, "score": 0.9, "reason": "digits compression"})

    # Alpha+digits
    m = [re.match(r"^([A-Za-z]+)(\d+)$", s) for s in processed_cases]
    if all(m):
        digit_lengths = [len(mi.group(2)) for mi in m]
        min_len, max_len = min(digit_lengths), max(digit_lengths)
        if min_len == max_len:
            digit_part = rf"\d{{{min_len}}}"
        else:
            digit_part = rf"\d{{{min_len},{max_len}}}"
        body = rf"\w+{digit_part}"
        candidates.append({"pattern": body, "score": 0.88, "reason": "alpha+digits"})

    # Word + whitespace patterns (e.g. "Hello World")
    # Automatically detect if all strings match word+space pattern
    token_lists = [s.split() for s in processed_cases]
    
    if all(all(re.fullmatch(r"\w+", tok) for tok in toks) for toks in token_lists):
        counts = set(len(toks) for toks in token_lists)
        if len(counts) == 1:
            k = counts.pop()
            if k == 2:
                # Add variant with exactly one space (\s)
                body_single = r"\w+\s\w+"
                if config.is_capturing_group_enabled:
                    body_single = f"({body_single})"
                else:
                    body_single = f"(?:{body_single})"
                candidates.append({"pattern": body_single, "score": 0.87, "reason": "word+space (exactly one space)"})
                # Add variant with one or more spaces (\s+)
                body_multi = r"\w+\s+\w+"
                if config.is_capturing_group_enabled:
                    body_multi = f"({body_multi})"
                else:
                    body_multi = f"(?:{body_multi})"
                candidates.append({"pattern": body_multi, "score": 0.86, "reason": "word+space (one or more spaces)"})
            elif k > 2:
                # Add variant with exactly one space
                body_single = rf"\w+(?:\s\w+){{{k-1}}}"
                if config.is_capturing_group_enabled:
                    body_single = f"({body_single})"
                else:
                    body_single = f"(?:{body_single})"
                candidates.append({"pattern": body_single, "score": 0.87, "reason": f"word+space x{k} (exactly one space)"})
                # Add variant with one or more spaces
                body_multi = rf"\w+(?:\s+\w+){{{k-1}}}"
                if config.is_capturing_group_enabled:
                    body_multi = f"({body_multi})"
                else:
                    body_multi = f"(?:{body_multi})"
                candidates.append({"pattern": body_multi, "score": 0.86, "reason": f"word+space x{k} (one or more spaces)"})
    
    # Repetitions
    if config.is_repetition_converted:
        reps = []
        for s in processed_cases:
            rep = detect_repetition(s, min_repetitions=config.minimum_repetitions,
                                    min_sub_len=config.minimum_substring_length)
            if rep:
                reps.append(rep)
        if reps:
            if len(reps) == len(processed_cases) and len(set(reps)) == 1:
                # All inputs have the same repetition pattern
                candidates.append({"pattern": reps[0], "score": 0.92, "reason": "uniform repetition"})
            else:
                # Add individual candidates for each unique repetition pattern
                unique_reps = list(dict.fromkeys(reps))  # preserve order, remove duplicates
                for rep in unique_reps:
                    candidates.append({"pattern": rep, "score": 0.88, "reason": "repeated substring"})
                # Also add the alternation of all repetitions
                candidates.append({"pattern": f"(?:{'|'.join(reps)})", "score": 0.7, "reason": "repetition alternation"})

    # Trie factoring
    trie_body = Trie(processed_cases).to_regex(capturing=config.is_capturing_group_enabled,
                                              verbose=config.is_verbose_mode_enabled)
    candidates.append({"pattern": trie_body, "score": 0.6, "reason": "trie factoring"})

    # Wrap with flags/anchors for presentation and evaluate safety / matches
    def wrap(pat):
        f = "(?x)" + ("(?i)" if config.is_case_insensitive_matching else "") if config.is_verbose_mode_enabled else ("(?i)" if config.is_case_insensitive_matching else "")
        pre = "" if config.is_start_anchor_disabled else "^"
        suf = "" if config.is_end_anchor_disabled else "$"
        return f + pre + pat + suf

    final = []
    for c in sorted(candidates, key=lambda x: -x["score"]):
        pat = wrap(c["pattern"]) if isinstance(c["pattern"], str) else c["pattern"]
        warning = analyze_regex_for_backtracking(pat)
        # Evaluate which test inputs match — try to catch timeouts
        matches = []
        timed_out = False
        for s in test_cases:
            try:
                ok = safe_match(pat, s, timeout=0.05)
            except TimeoutError:
                ok = False
                timed_out = True
            matches.append(ok)
        final.append({"pattern": pat, "score": c["score"], "reason": c["reason"], "warning": warning, "matches": matches, "timed_out": timed_out})
        if len(final) >= max_candidates:
            break

    return final


class RegExpBuilder:
    """
    Builds regexes from test cases using the configured settings.
    """

    def __init__(self, test_cases, config=None):
        if not test_cases:
            raise ValueError("No test cases have been provided for regex generation")

        # Preserve input order while deduplicating
        self.test_cases = list(dict.fromkeys(test_cases))  # avoid duplicates, preserve original order
        self.config = config if config else RegExpConfig()
        # Generalization preference: conservative | balanced | aggressive
        self.generalization = 'balanced'

    # -------------------------------
    # Factory methods
    # -------------------------------
    @classmethod
    def from_test_cases(cls, test_cases):
        return cls(test_cases)
    
    # -------------------------------
    # Config methods
    # -------------------------------
    def with_conversion_of_digits(self):
        self.config.is_digit_converted = True
        return self

    def with_conversion_of_non_digits(self):
        self.config.is_non_digit_converted = True
        return self

    def with_conversion_of_whitespace(self):
        self.config.is_space_converted = True
        return self

    def with_conversion_of_non_whitespace(self):
        self.config.is_non_space_converted = True
        return self

    def with_conversion_of_words(self):
        self.config.is_word_converted = True
        return self

    def with_conversion_of_non_words(self):
        self.config.is_non_word_converted = True
        return self

    def with_conversion_of_repetitions(self):
        self.config.is_repetition_converted = True
        return self

    def with_minimum_repetitions(self, quantity: int):
        if quantity <= 0:
            raise ValueError("Minimum repetitions must be greater than zero")
        self.config.minimum_repetitions = quantity
        return self

    def with_minimum_substring_length(self, length: int):
        if length <= 0:
            raise ValueError("Minimum substring length must be greater than zero")
        self.config.minimum_substring_length = length
        return self

    def with_case_insensitive_matching(self):
        self.config.is_case_insensitive_matching = True
        return self

    # Backwards-compatible alias used by GUI and older callers
    def with_case_insensitive(self):
        return self.with_case_insensitive_matching()

    def with_capturing_groups(self):
        self.config.is_capturing_group_enabled = True
        return self

    def with_generalization(self, mode: str = 'balanced'):
        """Set generalization preference: 'conservative', 'balanced', 'aggressive'"""
        if mode not in ('conservative', 'balanced', 'aggressive'):
            raise ValueError("Invalid generalization mode")
        self.generalization = mode
        return self

    def get_candidates(self, max_candidates: int = 5):
        return generate_candidates(self.test_cases, self.config, generalization=self.generalization, max_candidates=max_candidates)

    def with_verbose_mode(self):
        self.config.is_verbose_mode_enabled = True
        return self

    def without_start_anchor(self):
        self.config.is_start_anchor_disabled = True
        return self

    def without_end_anchor(self):
        self.config.is_end_anchor_disabled = True
        return self

    def without_anchors(self):
        self.config.is_start_anchor_disabled = True
        self.config.is_end_anchor_disabled = True
        return self

    # -------------------------------
    # Build pipeline
    # -------------------------------
    def build(self) -> str:
        """
        Generates the regex pattern string from test cases + config.
        """
        # return generate_regex_safe(self.test_cases, self.config)

        return generate_regex(self.test_cases, self.config)

# ============================================================
# Core generation logic
# ============================================================

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
        pattern_body = "|".join(unique)   # 🔥 no re.escape
        flags = "(?i)"
    else:
        unique = sorted(set(test_cases))
        pattern_body = "|".join(unique)   # 🔥 no re.escape
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


# Simple test when run directly
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

