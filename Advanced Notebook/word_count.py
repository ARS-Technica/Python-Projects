"""
statistic_tools
case_tools
character_tools
line_tools
transform_tools
space_tools

"""

def count_words(text: str) -> int:
    return len(text.split())


def count_characters(text: str) -> int:
    return len(text)


def count_lines(text: str) -> int:
    return text.count("\n") + 1 if text else 0






