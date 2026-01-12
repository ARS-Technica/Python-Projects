# Cleaned-up skeleton of generate_regex

# First, preprocess test_cases, tokenize them, and insert them into the trie.
# Call to_regex on that trie.
# trie.to_regex call comes after the trie has been filled with tokens


def generate_regex(test_cases: List[str], config) -> str:
    """
    Generate a regex string from test_cases according to config.

    Strategy (ordering is critical):
      1) Fast-path global detections (e.g. all-digits -> \d{min,max})
      2) Per-case preprocessing:
         - repetition conversion if enabled
         - case normalization if enabled
      3) Tokenize fragments into atomic regex fragments or literal chars
      4) Insert into Trie
      5) Export regex body via Trie.to_regex (with digit compression if enabled)
      6) Wrap with anchors, capturing, inline flags
    """

    if not test_cases:
        raise ValueError("No test cases provided")

    cases = [str(s) for s in test_cases]

    # Step 2: preprocess (detect repetition, normalize, etc.)
    preprocessed = []
    for s in cases:
        # e.g., call detect_repetition(s, config) here if repetition is enabled
        preprocessed.append(s)

    # Step 3: tokenize fragments
    tokenized = [_tokenize_fragment(s, config) for s in preprocessed]

    # Step 4: build trie
    trie = Trie()
    for tokens in tokenized:
        trie.insert(tokens)

    # Step 5: build regex body
    body = trie.to_regex(
        capturing=getattr(config, "is_capturing_group_enabled", False),
        verbose=getattr(config, "is_verbose_enabled", False),
        digits_only=getattr(config, "is_digits_enabled", False),  # <-- new
    )

    # Step 6: wrap with anchors / flags
    if getattr(config, "is_anchor_enabled", True):
        body = f"^{body}$"

    if getattr(config, "is_case_insensitive_enabled", False):
        body = f"(?i){body}"

    return body

