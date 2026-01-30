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
        
    # 5) add flags, anchors, capturing groups
    flags_parts = []
    if getattr(config, "is_case_insensitive_matching", False):
        flags_parts.append("i")
    if getattr(config, "is_verbose_mode_enabled", False):
        flags_parts.append("x")
        
    flags = f"(?{''.join(flags_parts)})" if flags_parts else ""
    prefix = "" if getattr(config, "is_start_anchor_disabled", False) else "^"
    suffix = "" if getattr(config, "is_end_anchor_disabled", False) else "$"
    
    if getattr(config, "is_capturing_group_enabled", False):
        body = f"({body})"
    
    return f"{flags}{prefix}{body}{suffix}"

