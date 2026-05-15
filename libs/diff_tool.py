"""
Knihovna pro porovnání dvou textů (diff)
"""

import difflib

MAX_INPUT = 500_000


def compare(text1, text2):
    """
    Porovná dva texty a vrátí seznam řádků s typem změny.

    Returns:
        tuple: (list of dicts, identical: bool)
    """
    if len(text1) > MAX_INPUT or len(text2) > MAX_INPUT:
        return None, 'Vstup je příliš velký (max 500 KB na text)'
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()

    diff = list(difflib.unified_diff(
        lines1, lines2,
        fromfile='Text A', tofile='Text B',
        lineterm=''
    ))

    if not diff:
        return [], True  # texty jsou identické

    result = []
    for line in diff:
        if line.startswith('+++') or line.startswith('---'):
            result.append({'type': 'header', 'text': line})
        elif line.startswith('@@'):
            result.append({'type': 'hunk', 'text': line})
        elif line.startswith('+'):
            result.append({'type': 'add', 'text': line[1:]})
        elif line.startswith('-'):
            result.append({'type': 'remove', 'text': line[1:]})
        else:
            result.append({'type': 'context', 'text': line[1:] if line.startswith(' ') else line})

    return result, False
