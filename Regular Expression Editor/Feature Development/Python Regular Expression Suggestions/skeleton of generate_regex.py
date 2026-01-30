# Cleaned-up skeleton of generate_regex for testing

def generate_regex(cases, config):
    # 0) fast-path digits
    digits_regex = _all_digits_fastpath(cases, config)
    if digits_regex:
        return digits_regex 

