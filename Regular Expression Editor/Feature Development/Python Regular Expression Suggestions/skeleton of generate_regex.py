# Cleaned-up skeleton of generate_regex for testing

def generate_regex(cases, config):
    # 0) fast-path digits
    digits_regex = _all_digits_fastpath(cases, config)
    if digits_regex:
        return digits_regex

    # 1) other fast-paths
    fast_regex = _global_fast_paths(cases, config)
    if fast_regex:
        return fast_regex

    # 2) detect repetitions
    repeated, remaining = _detect_repetition(cases, config)

    # 3) build trie for remaining
    trie_tokens = [ _tokenize_fragment(s, False) for s in remaining ]
    body_trie = _build_trie_regex(trie_tokens, config) if remaining else ""

    # 4) combine repeated fragments and trie output
    all_bodies = repeated + ([body_trie] if body_trie else [])
    if len(all_bodies) == 1:
        body = all_bodies[0]
    else:
        body = f"(?:{'|'.join(all_bodies)})"
