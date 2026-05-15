"""
Knihovna pro formátování JSON a XML
"""

import json
from defusedxml.minidom import parseString as safe_parseString

MAX_INPUT = 1_000_000


def format_json(text, sort_keys=False):
    if len(text) > MAX_INPUT:
        return None, 'Vstup je příliš velký (max 1 MB)'
    try:
        data = json.loads(text)
        return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=sort_keys), None
    except json.JSONDecodeError as e:
        return None, f'Chyba JSON na řádku {e.lineno}, sloupci {e.colno}: {e.msg}'


def minify_json(text):
    if len(text) > MAX_INPUT:
        return None, 'Vstup je příliš velký (max 1 MB)'
    try:
        data = json.loads(text)
        return json.dumps(data, separators=(',', ':'), ensure_ascii=False), None
    except json.JSONDecodeError as e:
        return None, f'Chyba JSON na řádku {e.lineno}, sloupci {e.colno}: {e.msg}'


def format_xml(text):
    if len(text) > MAX_INPUT:
        return None, 'Vstup je příliš velký (max 1 MB)'
    try:
        dom = safe_parseString(text.strip().encode('utf-8'))
        pretty = dom.toprettyxml(indent='  ')
        lines = [line for line in pretty.splitlines() if line.strip()]
        return '\n'.join(lines), None
    except Exception as e:
        return None, f'Chyba XML: {e}'
